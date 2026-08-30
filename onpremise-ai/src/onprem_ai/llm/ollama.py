"""Ollama 로컬 런타임 어댑터.

표준 라이브러리 urllib 만 사용한다. 프록시 환경변수를 무시하는 오프너를
쓰기 때문에 사내 프록시가 설정돼 있어도 루프백 밖으로 나가지 않는다.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Sequence

from ..config import Settings, assert_local_url
from ..errors import BackendError
from .base import ChatMessage


def _local_opener() -> urllib.request.OpenerDirector:
    """프록시를 타지 않는 오프너. 폐쇄망 전제를 코드로 강제한다."""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


class OllamaBackend:
    """`/api/chat`, `/api/embed` 를 호출하는 얇은 클라이언트."""

    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        assert_local_url(settings.base_url)
        self.settings = settings
        self.base_url = settings.base_url.rstrip("/")
        self._opener = _local_opener()

    # --- 내부 ---------------------------------------------------------
    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with self._opener.open(req, timeout=self.settings.request_timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise BackendError(f"{path} HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise BackendError(
                f"{url} 연결 실패: {exc.reason}. 로컬 런타임이 떠 있는지 확인 필요"
            ) from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BackendError(f"{path} 응답이 JSON 이 아님: {raw[:200]!r}") from exc

    def _get(self, path: str) -> dict[str, Any]:
        req = urllib.request.Request(f"{self.base_url}{path}", method="GET")
        try:
            with self._opener.open(req, timeout=min(self.settings.request_timeout, 10)) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise BackendError(f"{path} 조회 실패: {exc}") from exc

    # --- 공개 API -----------------------------------------------------
    def chat(self, messages: Sequence[ChatMessage], **options: object) -> str:
        payload: dict[str, Any] = {
            "model": options.pop("model", self.settings.chat_model),
            "messages": [m.as_dict() for m in messages],
            "stream": False,
            "options": {
                "temperature": options.pop("temperature", self.settings.temperature),
                "num_ctx": options.pop("num_ctx", self.settings.num_ctx),
                **options,
            },
        }
        data = self._post("/api/chat", payload)
        content = (data.get("message") or {}).get("content")
        if not isinstance(content, str):
            raise BackendError(f"chat 응답 형식이 예상과 다름: {list(data)}")
        return content

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        data = self._post(
            "/api/embed", {"model": self.settings.embed_model, "input": list(texts)}
        )
        vectors = data.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise BackendError(
                f"임베딩 개수 불일치: 요청 {len(texts)}, 응답 {len(vectors or [])}"
            )
        return [[float(x) for x in vec] for vec in vectors]

    def health(self) -> dict[str, object]:
        data = self._get("/api/tags")
        installed = [m.get("name", "") for m in data.get("models", [])]
        return {
            "backend": self.name,
            "base_url": self.base_url,
            "models": installed,
            "chat_model_ready": any(
                n.split(":")[0] == self.settings.chat_model.split(":")[0]
                for n in installed
            ),
            "embed_model_ready": any(
                n.split(":")[0] == self.settings.embed_model.split(":")[0]
                for n in installed
            ),
        }
