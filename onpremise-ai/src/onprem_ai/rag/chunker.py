"""청킹.

문단 경계를 최대한 지키면서 목표 길이에 맞춰 자른다. 문단 하나가
목표보다 길면 문장 경계로, 그래도 길면 글자 단위로 쪼갠다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_PARA_RE = re.compile(r"\n\s*\n")
_SENT_RE = re.compile(r"(?<=[.!?。？！])\s+|(?<=[다요])\.\s+")


@dataclass(frozen=True)
class Chunk:
    """색인 단위."""

    chunk_id: str
    doc_id: str
    text: str
    ordinal: int
    meta: dict[str, str] = field(default_factory=dict)


def _split_long(text: str, size: int) -> list[str]:
    """긴 덩어리를 문장 → 글자 순으로 쪼갠다."""
    pieces: list[str] = []
    buffer = ""
    for sentence in _SENT_RE.split(text):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) > size:
            if buffer:
                pieces.append(buffer)
                buffer = ""
            pieces.extend(
                sentence[i : i + size] for i in range(0, len(sentence), size)
            )
            continue
        candidate = f"{buffer} {sentence}".strip() if buffer else sentence
        if len(candidate) > size:
            pieces.append(buffer)
            buffer = sentence
        else:
            buffer = candidate
    if buffer:
        pieces.append(buffer)
    return pieces


def chunk_text(
    text: str,
    doc_id: str,
    size: int = 700,
    overlap: int = 120,
    meta: dict[str, str] | None = None,
) -> list[Chunk]:
    """문서 하나를 청크 목록으로 만든다.

    `overlap` 은 앞 청크 꼬리를 다음 청크 머리에 붙여 문맥 단절을 줄인다.
    겹침 접두가 더해지므로 청크 길이 상한은 `size + overlap` 이다.
    """
    if size <= 0:
        raise ValueError("size 는 1 이상이어야 함")
    if not 0 <= overlap < size:
        raise ValueError("overlap 은 0 이상 size 미만이어야 함")

    units: list[str] = []
    for para in _PARA_RE.split(text):
        para = para.strip()
        if not para:
            continue
        units.extend(_split_long(para, size) if len(para) > size else [para])

    # 겹침 접두에 구분자까지 포함시켜 청크 길이 상한을 size + overlap 으로 묶는다.
    separator = "\n\n"
    tail_room = max(0, overlap - len(separator))

    packed: list[str] = []
    buffer = ""
    for unit in units:
        candidate = f"{buffer}{separator}{unit}" if buffer else unit
        if len(candidate) > size and buffer:
            packed.append(buffer)
            tail = buffer[-tail_room:] if tail_room else ""
            buffer = f"{tail}{separator}{unit}".strip() if tail else unit
        else:
            buffer = candidate
    if buffer.strip():
        packed.append(buffer)

    return [
        Chunk(
            chunk_id=f"{doc_id}#{i}",
            doc_id=doc_id,
            text=body.strip(),
            ordinal=i,
            meta=dict(meta or {}),
        )
        for i, body in enumerate(packed)
    ]
