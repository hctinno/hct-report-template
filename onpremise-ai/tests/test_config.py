import unittest

from tests.support import ROOT  # noqa: F401  (sys.path 준비)

from onprem_ai.config import Settings, assert_local_url, load_dotenv, load_settings
from onprem_ai.errors import ConfigError


class TestSettings(unittest.TestCase):
    def test_defaults_validate(self):
        settings = Settings().validated()
        self.assertEqual(settings, settings.validated())
        self.assertEqual(settings.backend, "ollama")

    def test_rejects_remote_backend_url(self):
        with self.assertRaises(ConfigError) as ctx:
            Settings(base_url="https://api.openai.com").validated()
        self.assertIn("로컬 백엔드만 허용", str(ctx.exception))

    def test_allows_loopback(self):
        assert_local_url("http://127.0.0.1:11434")
        assert_local_url("http://localhost:8080")

    def test_rejects_bad_overlap(self):
        with self.assertRaises(ConfigError):
            Settings(chunk_size=100, chunk_overlap=100).validated()

    def test_rejects_candidate_below_top_k(self):
        with self.assertRaises(ConfigError):
            Settings(top_k=10, candidate_k=3).validated()

    def test_env_overrides_are_typed(self):
        s = load_settings(
            env={
                "ONPREM_TOP_K": "9",
                "ONPREM_TEMPERATURE": "0.7",
                "ONPREM_REDACT_SECRETS": "false",
                "ONPREM_INDEX_DIR": "/srv/index",
            },
            dotenv_path=None,
        )
        self.assertEqual(s.top_k, 9)
        self.assertAlmostEqual(s.temperature, 0.7)
        self.assertFalse(s.redact_secrets)
        self.assertEqual(str(s.index_dir), "/srv/index")
        self.assertEqual(s.source, "env")

    def test_unknown_env_keys_ignored(self):
        s = load_settings(env={"ONPREM_NOPE": "1", "PATH": "/bin"}, dotenv_path=None)
        self.assertEqual(s.source, "default")

    def test_dotenv_missing_file_is_empty(self):
        self.assertEqual(load_dotenv("/nonexistent/.env"), {})


if __name__ == "__main__":
    unittest.main()
