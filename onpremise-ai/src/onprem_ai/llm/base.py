"""백엔드 공통 인터페이스.

플래그십 API 를 쓰지 않는 것이 전제다. 구현체는 전부 루프백 주소의
로컬 런타임(Ollama, llama.cpp server 등)만 바라본다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from ..config import Settings
from ..errors import ConfigError


@dataclass(frozen=True)
class ChatMessage:
    """대화 한 턴."""

    role: str
    content: str

    def __post_init__(self) -> None:
        if self.role not in {"system", "user", "assistant"}:
            raise ValueError(f"허용하지 않는 role: {self.role!r}")

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@runtime_checkable
class LLMBackend(Protocol):
    """로컬 추론 백엔드가 만족해야 하는 최소 규격."""

    name: str

    def chat(self, messages: Sequence[ChatMessage], **options: object) -> str:
        """대화를 받아 응답 본문을 반환."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """문장 목록을 임베딩 벡터 목록으로 변환."""

    def health(self) -> dict[str, object]:
        """백엔드 상태를 점검해 진단 정보를 반환."""


def build_backend(settings: Settings) -> LLMBackend:
    """설정의 `backend` 이름으로 구현체를 만든다."""
    from .mock import MockBackend
    from .ollama import OllamaBackend

    table = {
        "ollama": OllamaBackend,
        "llamacpp": OllamaBackend,  # OpenAI 호환 경로는 별도 어댑터 예정
        "mock": MockBackend,
    }
    factory = table.get(settings.backend)
    if factory is None:
        raise ConfigError(
            f"알 수 없는 backend: {settings.backend!r}. 가능: {sorted(table)}"
        )
    return factory(settings)
