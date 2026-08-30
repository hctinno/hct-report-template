"""하이브리드 검색.

조밀 검색(임베딩)과 희소 검색(BM25)을 RRF 로 합친다. 두 점수의
스케일이 서로 달라 가중합은 코퍼스마다 재조정이 필요한데, 순위 기반
결합은 그 조정을 없앤다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ..errors import RetrievalError
from ..llm.base import LLMBackend
from .bm25 import BM25Index
from .chunker import Chunk
from .store import StoredChunk, VectorStore

#: RRF 상수. 값이 클수록 상위 순위 가중이 완만해진다.
RRF_K = 60


@dataclass(frozen=True)
class Hit:
    """검색 결과 한 건."""

    chunk_id: str
    doc_id: str
    text: str
    score: float
    dense_rank: int | None = None
    sparse_rank: int | None = None

    @property
    def matched_by(self) -> str:
        if self.dense_rank is not None and self.sparse_rank is not None:
            return "hybrid"
        return "dense" if self.dense_rank is not None else "sparse"


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]], k: int = RRF_K
) -> dict[str, float]:
    """여러 순위 목록을 RRF 점수 사전으로 합친다."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank)
    return fused


class HybridRetriever:
    """벡터 스토어와 BM25 색인을 함께 들고 질의를 처리한다."""

    def __init__(
        self, backend: LLMBackend, store: VectorStore, bm25: BM25Index
    ) -> None:
        self.backend = backend
        self.store = store
        self.bm25 = bm25

    # --- 구축 ---------------------------------------------------------
    @classmethod
    def build(
        cls, backend: LLMBackend, chunks: Sequence[Chunk], batch_size: int = 16
    ) -> "HybridRetriever":
        """청크 목록을 임베딩해 검색기를 만든다."""
        if not chunks:
            raise RetrievalError("색인할 청크가 없음. 코퍼스를 먼저 채워야 함")

        store = VectorStore()
        bm25 = BM25Index()
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            vectors = backend.embed([c.text for c in batch])
            for chunk, vector in zip(batch, vectors):
                store.add(
                    StoredChunk(
                        chunk_id=chunk.chunk_id,
                        doc_id=chunk.doc_id,
                        text=chunk.text,
                        vector=vector,
                        meta=chunk.meta,
                    )
                )
                bm25.add(chunk.chunk_id, chunk.text)
        return cls(backend, store, bm25)

    # --- 질의 ---------------------------------------------------------
    def search(
        self, query: str, top_k: int = 5, candidate_k: int = 30, min_score: float = 0.0
    ) -> list[Hit]:
        """질의에 대한 상위 청크를 반환."""
        if not query.strip():
            raise RetrievalError("빈 질의")
        if len(self.store) == 0:
            return []

        query_vector = self.backend.embed([query])[0]
        dense = self.store.search(query_vector, top_k=candidate_k)
        sparse = self.bm25.search(query, top_k=candidate_k)

        dense_rank = {cid: i + 1 for i, (cid, _) in enumerate(dense)}
        sparse_rank = {cid: i + 1 for i, (cid, _) in enumerate(sparse)}
        fused = reciprocal_rank_fusion([list(dense_rank), list(sparse_rank)])

        hits: list[Hit] = []
        for chunk_id, score in sorted(fused.items(), key=lambda p: (-p[1], p[0])):
            stored = self.store.get(chunk_id)
            if stored is None:
                continue
            hits.append(
                Hit(
                    chunk_id=chunk_id,
                    doc_id=stored.doc_id,
                    text=stored.text,
                    score=score,
                    dense_rank=dense_rank.get(chunk_id),
                    sparse_rank=sparse_rank.get(chunk_id),
                )
            )

        ceiling = max((h.score for h in hits), default=0.0)
        if ceiling > 0.0:
            hits = [h for h in hits if h.score / ceiling >= min_score]
        return hits[:top_k]

    # --- 영속화 -------------------------------------------------------
    def save(self, index_dir: str | Path) -> Path:
        d = Path(index_dir)
        d.mkdir(parents=True, exist_ok=True)
        self.store.save(d / "vectors.jsonl")
        (d / "bm25.json").write_text(
            json.dumps(self.bm25.to_dict(), ensure_ascii=False), encoding="utf-8"
        )
        return d

    @classmethod
    def load(cls, backend: LLMBackend, index_dir: str | Path) -> "HybridRetriever":
        d = Path(index_dir)
        bm25_path = d / "bm25.json"
        if not bm25_path.is_file():
            raise RetrievalError(f"BM25 색인 없음: {bm25_path}")
        store = VectorStore.load(d / "vectors.jsonl")
        bm25 = BM25Index.from_dict(json.loads(bm25_path.read_text(encoding="utf-8")))
        return cls(backend, store, bm25)
