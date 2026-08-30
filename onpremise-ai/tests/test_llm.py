"""백엔드 테스트.

Ollama 어댑터는 루프백에 띄운 스텁 HTTP 서버로 검증한다. 실제 모델
가중치 없이 프로토콜 계약만 확인하는 것이 목적이다.
"""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from tests.support import make_settings

from onprem_ai.config import Settings
from onprem_ai.errors import BackendError, ConfigError
from onprem_ai.llm.base import ChatMessage, LLMBackend, build_backend
from onprem_ai.llm.mock import MockBackend, hashing_embed
from onprem_ai.llm.ollama import OllamaBackend


class _StubHandler(BaseHTTPRequestHandler):
    """`/api/chat`, `/api/embed`, `/api/tags` 만 흉내 낸다."""

    def log_message(self, *args):  # 테스트 출력 오염 방지
        pass

    def _send(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/tags":
            self._send(200, {"models": [{"name": "gemma3:12b"}, {"name": "bge-m3"}]})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        request = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/chat":
            last = request["messages"][-1]["content"]
            self._send(200, {"message": {"role": "assistant", "content": f"echo:{last}"}})
        elif self.path == "/api/embed":
            texts = request["input"]
            self._send(200, {"embeddings": [[float(len(t)), 1.0] for t in texts]})
        elif self.path == "/api/broken":
            self._send(500, {"error": "boom"})
        else:
            self._send(404, {"error": "not found"})


class TestMockBackend(unittest.TestCase):
    def test_satisfies_protocol(self):
        self.assertIsInstance(MockBackend(make_settings()), LLMBackend)

    def test_embedding_is_deterministic_and_normalized(self):
        a = hashing_embed("망분리 정책")
        b = hashing_embed("망분리 정책")
        self.assertEqual(a, b)
        self.assertAlmostEqual(sum(x * x for x in a) ** 0.5, 1.0, places=6)

    def test_empty_text_gives_zero_vector(self):
        self.assertEqual(set(hashing_embed("")), {0.0})

    def test_records_calls(self):
        backend = MockBackend(make_settings())
        backend.chat([ChatMessage("user", "질문")])
        self.assertEqual(len(backend.calls), 1)


class TestChatMessage(unittest.TestCase):
    def test_rejects_unknown_role(self):
        with self.assertRaises(ValueError):
            ChatMessage("root", "내용")

    def test_serializes_to_dict(self):
        self.assertEqual(
            ChatMessage("user", "안녕").as_dict(), {"role": "user", "content": "안녕"}
        )


class TestBuildBackend(unittest.TestCase):
    def test_unknown_backend_lists_options(self):
        with self.assertRaises(ConfigError) as ctx:
            build_backend(Settings(backend="gpt-5"))
        self.assertIn("mock", str(ctx.exception))

    def test_builds_mock(self):
        self.assertIsInstance(build_backend(Settings(backend="mock")), MockBackend)


class TestOllamaBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _StubHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        port = cls.server.server_address[1]
        cls.settings = Settings(
            backend="ollama", base_url=f"http://127.0.0.1:{port}", request_timeout=5.0
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_chat_returns_content(self):
        backend = OllamaBackend(self.settings)
        self.assertEqual(backend.chat([ChatMessage("user", "안녕")]), "echo:안녕")

    def test_embed_matches_input_count(self):
        vectors = OllamaBackend(self.settings).embed(["가", "나다"])
        self.assertEqual(vectors, [[1.0, 1.0], [2.0, 1.0]])

    def test_embed_empty_list_short_circuits(self):
        self.assertEqual(OllamaBackend(self.settings).embed([]), [])

    def test_health_detects_installed_models(self):
        health = OllamaBackend(self.settings).health()
        self.assertTrue(health["chat_model_ready"])
        self.assertTrue(health["embed_model_ready"])

    def test_refuses_non_loopback_base_url(self):
        with self.assertRaises(ConfigError):
            OllamaBackend(Settings(base_url="http://10.0.0.5:11434"))

    def test_connection_failure_is_actionable(self):
        dead = Settings(base_url="http://127.0.0.1:1", request_timeout=1.0)
        with self.assertRaises(BackendError) as ctx:
            OllamaBackend(dead).chat([ChatMessage("user", "안녕")])
        self.assertIn("로컬 런타임", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
