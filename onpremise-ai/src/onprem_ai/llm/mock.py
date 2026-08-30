"""테스트·개발용 결정적 백엔드.

모델 가중치 없이 파이프라인 전체를 돌려보기 위한 것이다. 임베딩은
해시 기반 결정적 벡터라 같은 입력에 항상 같은 값을 준다.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Sequence

from ..config import Settings
from .base import ChatMessage

_DIM = 128
_TOKEN_RE = re.compile(r"[0-9A-Za-z가-힣]+")


def hashing_embed(text: str, dim: int = _DIM) -> list[float]:
    """토큰 해시를 버킷에 누적한 뒤 L2 정규화한 벡터.

    실제 임베딩 모델의 대체물이 아니라, 검색 파이프라인의 형태를
    검증하기 위한 결정적 스텁이다.
    """
    vec = [0.0] * dim
    tokens = _TOKEN_RE.findall(text.lower())
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[index] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


class MockBackend:
    """호출 기록을 남기는 가짜 백엔드."""

    name = "mock"

    def __init__(self, settings: Settings, reply: str | None = None) -> None:
        self.settings = settings
        self.reply = reply
        self.calls: list[list[ChatMessage]] = []

    def chat(self, messages: Sequence[ChatMessage], **options: object) -> str:
        self.calls.append(list(messages))
        if self.reply is not None:
            return self.reply
        question = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        return f"[mock] 질의 {len(question)}자 처리, 근거 [1] 기준 요약."

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [hashing_embed(t) for t in texts]

    def health(self) -> dict[str, object]:
        return {
            "backend": self.name,
            "base_url": "n/a",
            "models": [self.settings.chat_model],
            "chat_model_ready": True,
            "embed_model_ready": True,
        }
