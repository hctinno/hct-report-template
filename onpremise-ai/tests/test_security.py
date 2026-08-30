import json
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT  # noqa: F401

from onprem_ai.errors import IsolationError
from onprem_ai.security.audit import AuditLog
from onprem_ai.security.egress import EgressReport, assert_isolated, check_egress
from onprem_ai.security.redact import redact, scan_secrets


class TestRedact(unittest.TestCase):
    def test_masks_korean_rrn(self):
        text, findings = redact("주민번호 900101-1234567 확인")
        self.assertNotIn("900101-1234567", text)
        self.assertEqual([f.kind for f in findings], ["rrn"])

    def test_masks_multiple_kinds_in_order(self):
        text, findings = redact("메일 a@b.co 키 AKIAIOSFODNN7EXAMPLE 폰 010-1234-5678")
        self.assertEqual([f.kind for f in findings], ["email", "aws_key", "phone_kr"])
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", text)

    def test_overlapping_matches_take_first_rule(self):
        findings = scan_secrets("card 4111-1111-1111-1111")
        self.assertEqual([f.kind for f in findings], ["card"])

    def test_clean_text_untouched(self):
        text, findings = redact("망분리 정책 문서")
        self.assertEqual(text, "망분리 정책 문서")
        self.assertEqual(findings, [])

    def test_private_key_header_detected(self):
        _, findings = redact("-----BEGIN RSA PRIVATE KEY-----")
        self.assertEqual([f.kind for f in findings], ["private_key"])


class TestEgress(unittest.TestCase):
    def test_isolated_report_is_clean(self):
        report = EgressReport(checked=3)
        self.assertTrue(report.isolated)
        self.assertIn("격리 양호", report.summary())

    def test_reachable_target_fails_isolation(self):
        report = EgressReport(reachable=["8.8.8.8:53"], checked=1)
        self.assertFalse(report.isolated)
        self.assertIn("TCP 도달", report.summary())

    def test_dns_resolution_fails_isolation(self):
        report = EgressReport(resolvable=["example.com"], checked=1)
        self.assertFalse(report.isolated)

    def test_assert_isolated_raises_on_leak(self):
        with self.assertRaises(IsolationError):
            assert_isolated(EgressReport(reachable=["1.1.1.1:53"], checked=1))

    def test_assert_isolated_passes_when_clean(self):
        report = EgressReport(checked=2)
        self.assertIs(assert_isolated(report), report)

    def test_check_egress_counts_all_probes(self):
        report = check_egress(targets=(("127.0.0.1", 9),), dns_probes=(), timeout=0.2)
        self.assertEqual(report.checked, 1)


class TestAuditLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "audit.jsonl"
        self.log = AuditLog(self.path, actor="tester")

    def tearDown(self):
        self.tmp.cleanup()

    def test_chain_verifies(self):
        self.log.append("ingest", docs=3)
        self.log.append("ask", question="망분리 원칙")
        ok, reason = self.log.verify()
        self.assertTrue(ok, reason)
        self.assertEqual(len(self.log.records()), 2)

    def test_empty_log_verifies(self):
        self.assertEqual(self.log.verify(), (True, "체인 정상"))

    def test_secrets_never_written(self):
        self.log.append("ask", question="내 메일 hong@hct.co.kr 로 보내줘")
        raw = self.path.read_text(encoding="utf-8")
        self.assertNotIn("hong@hct.co.kr", raw)
        self.assertIn("REDACTED:email", raw)

    def test_tampering_is_detected(self):
        self.log.append("ask", question="첫 질문")
        self.log.append("ask", question="둘째 질문")
        lines = self.path.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[0])
        record["detail"]["question"] = "조작된 질문"
        lines[0] = json.dumps(record, ensure_ascii=False)
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        ok, reason = self.log.verify()
        self.assertFalse(ok)
        self.assertIn("1번째", reason)

    def test_deleted_record_is_detected(self):
        for i in range(3):
            self.log.append("ask", question=f"질문 {i}")
        lines = self.path.read_text(encoding="utf-8").splitlines()
        del lines[1]
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertFalse(self.log.verify()[0])


if __name__ == "__main__":
    unittest.main()
