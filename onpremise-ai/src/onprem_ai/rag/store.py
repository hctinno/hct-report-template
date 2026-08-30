"""로컬 벡터 스토어.

외부 벡터 DB 를 두지 않는다. 서비스가 하나 늘면 격리 경계와 감사
대상이 함께 늘기 때문이다. JSONL 파일 하나로 유지한다.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from ..errors import RetrievalError


@dataclass(frozen=True)
class StoredChunk:
    """저장된 청크 한 건."""

    chunk_id: str
    doc_id: str
    text: str
    vector: list[float]
    meta: dict[str, str]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """코사인 유사도. 길이가 다르면 오류."""
    if len(a) != len(b):
        raise RetrievalError(f"벡터 차원 불일치: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class VectorStore:
    """append-only JSONL 로 유지되는 조밀 벡터 색인."""

    def __init__(self, chunks: Iterable[StoredChunk] = ()) -> None:
        self._chunks: list[StoredChunk] = list(chunks)

    def __len__(self) -> int:
        return len(self._chunks)

    def __iter__(self):
        return iter(self._chunks)

    @property
    def dim(self) -> int:
        return len(self._chunks[0].vector) if self._chunks else 0

    def add(self, chunk: StoredChunk) -> None:
        if self._chunks and len(chunk.vector) != self.dim:
            raise RetrievalError(
                f"{chunk.chunk_id}: 차원 {len(chunk.vector)}, 색인 차원 {self.dim}. "
                "임베딩 모델이 바뀌었으면 전체 재색인 필요"
            )
        self._chunks.append(chunk)

    def get(self, chunk_id: str) -> StoredChunk | None:
        return next((c for c in self._chunks if c.chunk_id == chunk_id), None)

    def search(self, vector: Sequence[float], top_k: int = 10) -> list[tuple[str, float]]:
        """질의 벡터와 가까운 (청크 id, 유사도) 목록."""
        if not self._chunks:
            return []
        scored = [(c.chunk_id, cosine(vector, c.vector)) for c in self._chunks]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored[:top_k]

    # --- 영속화 -------------------------------------------------------
    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            for c in self._chunks:
                fh.write(
                    json.dumps(
                        {
                            "chunk_id": c.chunk_id,
                            "doc_id": c.doc_id,
                            "text": c.text,
                            "vector": c.vector,
                            "meta": c.meta,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return p

    @classmethod
    def load(cls, path: str | Path) -> "VectorStore":
        p = Path(path)
        if not p.is_file():
            raise RetrievalError(f"색인 파일 없음: {p}. 먼저 ingest 를 실행해야 함")
        chunks: list[StoredChunk] = []
        for line_no, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                data = json.loads(raw)
                chunks.append(
                    StoredChunk(
                        chunk_id=data["chunk_id"],
                        doc_id=data["doc_id"],
                        text=data["text"],
                        vector=[float(x) for x in data["vector"]],
                        meta=dict(data.get("meta", {})),
                    )
                )
            except (json.JSONDecodeError, KeyError) as exc:
                raise RetrievalError(f"{p}:{line_no} 색인 레코드 손상: {exc}") from exc
        return cls(chunks)
