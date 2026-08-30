import tempfile
import unittest
from pathlib import Path

from tests.support import make_retriever, make_settings

from onprem_ai.evaluate import EvalCase, evaluate, load_cases
from onprem_ai.harness.pipeline import RagPipeline
from onprem_ai.llm.mock import MockBackend


class TestLoadCases(unittest.TestCase):
    def test_reads_jsonl_and_skips_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "golden.jsonl"
            p.write_text(
                '// 주석\n{"question": "질문1", "expect_docs": ["a.md"]}\n\n'
                '{"question": "질문2", "expect_refusal": true}\n',
                encoding="utf-8",
            )
            cases = load_cases(p)
        self.assertEqual(len(cases), 2)
        self.assertEqual(cases[0].expect_docs, ["a.md"])
        self.assertTrue(cases[1].expect_refusal)


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.settings = make_settings()
        self.retriever = make_retriever()

    def _pipeline(self, reply: str) -> RagPipeline:
        return RagPipeline(
            MockBackend(self.settings, reply=reply), self.retriever, self.settings
        )

    def test_scores_retrieval_and_citations(self):
        result = evaluate(
            self._pipeline("격리 경로 없음 [1]"),
            [EvalCase(question="망 분리 원칙은?", expect_docs=["isolation.md"])],
        )
        self.assertEqual(result.total, 1)
        self.assertEqual(result.recall, 1.0)
        self.assertEqual(result.citation_rate, 1.0)
        self.assertEqual(result.failures, [])

    def test_wrong_document_is_reported(self):
        result = evaluate(
            self._pipeline("응답 [1]"),
            [EvalCase(question="망 분리 원칙은?", expect_docs=["없는문서.md"])],
        )
        self.assertEqual(result.recall, 0.0)
        self.assertTrue(result.failures)

    def test_missing_citation_lowers_rate(self):
        result = evaluate(
            self._pipeline("인용 없는 응답"),
            [EvalCase(question="망 분리 원칙은?", expect_docs=["isolation.md"])],
        )
        self.assertEqual(result.citation_rate, 0.0)

    def test_empty_case_list_has_zero_rates(self):
        result = evaluate(self._pipeline("응답 [1]"), [])
        self.assertEqual(result.recall, 0.0)
        self.assertIn("0건", result.report())

    def test_report_lists_failures(self):
        result = evaluate(
            self._pipeline("응답 [1]"),
            [EvalCase(question="아무거나", expect_refusal=True)],
        )
        self.assertIn("실패 항목", result.report())


if __name__ == "__main__":
    unittest.main()
