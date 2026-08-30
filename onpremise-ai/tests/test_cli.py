import io
import contextlib
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT  # noqa: F401

from onprem_ai.cli import main


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.corpus = self.root / "corpus"
        self.corpus.mkdir()
        (self.corpus / "policy.md").write_text(
            "추론 컨테이너는 외부로 나가는 경로를 갖지 않는다. DNS 해석이 되면 격리 실패다.",
            encoding="utf-8",
        )
        self.index = self.root / "index"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = main(list(argv))
        return code, out.getvalue()

    def _base(self) -> list[str]:
        return [
            "--backend", "mock",
            "--allow-egress",
            "--corpus", str(self.corpus),
            "--index", str(self.index),
            "--audit-log", str(self.root / "audit.jsonl"),
        ]

    def test_ingest_then_ask(self):
        code, out = self._run(*self._base(), "ingest")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.index / "vectors.jsonl").is_file())

        code, out = self._run(*self._base(), "ask", "격리", "실패", "판정")
        self.assertEqual(code, 0, out)
        self.assertIn("policy.md", out)

    def test_ask_without_index_explains(self):
        code, out = self._run(*self._base(), "ask", "질문")
        self.assertEqual(code, 1)
        self.assertIn("색인", out)

    def test_ingest_empty_corpus_fails(self):
        empty = self.root / "empty"
        empty.mkdir()
        code, out = self._run(
            "--backend", "mock", "--allow-egress",
            "--corpus", str(empty), "--index", str(self.index),
            "--audit-log", str(self.root / "audit.jsonl"), "ingest",
        )
        self.assertEqual(code, 1)
        self.assertIn("비어 있음", out)

    def test_doctor_reports_environment(self):
        code, out = self._run(*self._base(), "doctor")
        self.assertIn("백엔드:", out)
        self.assertIn("격리:", out)
        self.assertIn("색인:", out)
        self.assertIn(code, (0, 2))

    def test_audit_verifies_after_ingest(self):
        self._run(*self._base(), "ingest")
        code, out = self._run(*self._base(), "audit")
        self.assertEqual(code, 0, out)
        self.assertIn("체인 정상", out)


if __name__ == "__main__":
    unittest.main()
