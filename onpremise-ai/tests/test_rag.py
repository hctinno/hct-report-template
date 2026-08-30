import tempfile
import unittest
from pathlib import Path

from tests.support import DOCS, make_retriever, make_settings

from onprem_ai.errors import RetrievalError
from onprem_ai.llm.mock import MockBackend
from onprem_ai.rag.bm25 import BM25Index
from onprem_ai.rag.chunker import chunk_text
from onprem_ai.rag.loaders import load_corpus, load_file
from onprem_ai.rag.retriever import HybridRetriever, reciprocal_rank_fusion
from onprem_ai.rag.store import StoredChunk, VectorStore, cosine
from onprem_ai.rag.tokenize import tokenize


class TestTokenize(unittest.TestCase):
    def test_keeps_word_and_bigrams_for_hangul(self):
        tokens = tokenize("망분리")
        self.assertIn("망분리", tokens)
        self.assertIn("망분", tokens)
        self.assertIn("분리", tokens)

    def test_ascii_words_have_no_bigrams(self):
        self.assertEqual(tokenize("BM25 rrf"), ["bm25", "rrf"])

    def test_normalizes_case_and_width(self):
        self.assertEqual(tokenize("ＲＡＧ"), tokenize("rag"))


class TestChunker(unittest.TestCase):
    def test_respects_size_bound(self):
        text = "\n\n".join("가나다라마" * 60 for _ in range(5))
        chunks = chunk_text(text, "d.md", size=300, overlap=50)
        self.assertTrue(chunks)
        for c in chunks:
            self.assertLessEqual(len(c.text), 300 + 50)

    def test_ids_are_sequential(self):
        chunks = chunk_text("문단 하나.\n\n문단 둘.\n\n문단 셋.", "d.md", size=20, overlap=5)
        self.assertEqual([c.ordinal for c in chunks], list(range(len(chunks))))
        self.assertEqual(chunks[0].chunk_id, "d.md#0")

    def test_short_text_is_single_chunk(self):
        chunks = chunk_text("짧은 글", "d.md", size=700, overlap=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].text, "짧은 글")

    def test_rejects_overlap_ge_size(self):
        with self.assertRaises(ValueError):
            chunk_text("x", "d.md", size=10, overlap=10)


class TestBM25(unittest.TestCase):
    def setUp(self):
        self.index = BM25Index()
        self.index.add_many(list(DOCS.items()))

    def test_exact_term_wins(self):
        results = self.index.search("SHA256 해시 대조", top_k=3)
        self.assertEqual(results[0][0], "weights.md")

    def test_empty_index_returns_empty(self):
        self.assertEqual(BM25Index().search("무엇이든"), [])

    def test_unknown_term_scores_nothing(self):
        self.assertEqual(self.index.search("zzzznotpresent"), [])

    def test_roundtrip_serialization(self):
        restored = BM25Index.from_dict(self.index.to_dict())
        self.assertEqual(
            restored.search("하이브리드 검색"), self.index.search("하이브리드 검색")
        )


class TestVectorStore(unittest.TestCase):
    def test_cosine_bounds(self):
        self.assertAlmostEqual(cosine([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(cosine([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertAlmostEqual(cosine([1.0, 0.0], [-1.0, 0.0]), -1.0)

    def test_cosine_zero_vector_is_zero(self):
        self.assertEqual(cosine([0.0, 0.0], [1.0, 1.0]), 0.0)

    def test_dimension_mismatch_rejected(self):
        store = VectorStore([StoredChunk("a#0", "a", "본문", [1.0, 0.0], {})])
        with self.assertRaises(RetrievalError):
            store.add(StoredChunk("b#0", "b", "본문", [1.0, 0.0, 0.0], {}))

    def test_save_load_roundtrip(self):
        store = VectorStore(
            [StoredChunk("a#0", "a", "한글 본문", [0.1, 0.2], {"k": "v"})]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = store.save(Path(tmp) / "vectors.jsonl")
            loaded = VectorStore.load(path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded.get("a#0").text, "한글 본문")
        self.assertEqual(loaded.get("a#0").meta, {"k": "v"})

    def test_load_missing_file_explains(self):
        with self.assertRaises(RetrievalError) as ctx:
            VectorStore.load("/nonexistent/vectors.jsonl")
        self.assertIn("ingest", str(ctx.exception))


class TestLoaders(unittest.TestCase):
    def test_rejects_binary_format_with_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "보고서.pdf"
            p.write_bytes(b"%PDF-1.4")
            with self.assertRaises(RetrievalError) as ctx:
                load_file(p)
        self.assertIn("pdftotext", str(ctx.exception))

    def test_corpus_skips_unsupported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("내용", encoding="utf-8")
            (root / "b.pdf").write_bytes(b"%PDF")
            (root / ".hidden.md").write_text("숨김", encoding="utf-8")
            docs = load_corpus(root)
        self.assertEqual([d.doc_id for d in docs], ["a.md"])

    def test_checksum_is_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "a.md"
            p.write_text("같은 내용", encoding="utf-8")
            self.assertEqual(load_file(p).checksum, load_file(p).checksum)


class TestRetriever(unittest.TestCase):
    def test_rrf_prefers_agreement(self):
        fused = reciprocal_rank_fusion([["a", "b"], ["b", "a"]])
        self.assertAlmostEqual(fused["a"], fused["b"])
        fused2 = reciprocal_rank_fusion([["a", "b"], ["a", "c"]])
        self.assertGreater(fused2["a"], fused2["b"])

    def test_search_finds_sparse_only_term(self):
        retriever = make_retriever()
        hits = retriever.search("SHA256", top_k=3, candidate_k=10)
        self.assertIn("weights.md", {h.doc_id for h in hits})

    def test_hits_report_match_source(self):
        hits = make_retriever().search("하이브리드 검색 RRF", top_k=3, candidate_k=10)
        self.assertTrue(hits)
        self.assertIn(hits[0].matched_by, {"hybrid", "dense", "sparse"})

    def test_empty_query_rejected(self):
        with self.assertRaises(RetrievalError):
            make_retriever().search("   ")

    def test_build_rejects_empty_corpus(self):
        with self.assertRaises(RetrievalError):
            HybridRetriever.build(MockBackend(make_settings()), [])

    def test_index_roundtrip(self):
        retriever = make_retriever()
        with tempfile.TemporaryDirectory() as tmp:
            retriever.save(tmp)
            reloaded = HybridRetriever.load(MockBackend(make_settings()), tmp)
        query = "격리 실패 판정"
        self.assertEqual(
            [h.chunk_id for h in reloaded.search(query, top_k=3, candidate_k=10)],
            [h.chunk_id for h in retriever.search(query, top_k=3, candidate_k=10)],
        )


if __name__ == "__main__":
    unittest.main()
