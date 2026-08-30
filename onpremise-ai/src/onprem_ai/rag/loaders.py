"""문서 적재.

바이너리 포맷 파서를 끌어오지 않는다. 폐쇄망 반입 시 의존성이 늘면
검증 부담이 커지므로, 텍스트 계열만 읽고 나머지는 사전 변환을 요구한다.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from ..errors import RetrievalError

#: 그대로 읽는 확장자.
TEXT_SUFFIXES = frozenset({".txt", ".md", ".markdown", ".rst", ".csv", ".json", ".yaml", ".yml"})

#: 사전 변환이 필요한 확장자와 안내.
NEEDS_CONVERSION = {
    ".pdf": "pdftotext 로 .txt 변환 후 반입",
    ".docx": "사내 변환 도구로 .md 변환 후 반입",
    ".pptx": "사내 변환 도구로 .md 변환 후 반입",
    ".hwp": "한글 문서는 .txt 로 내보낸 뒤 반입",
    ".hwpx": "한글 문서는 .txt 로 내보낸 뒤 반입",
}


@dataclass(frozen=True)
class Document:
    """원문 한 건."""

    doc_id: str
    source: str
    text: str
    meta: dict[str, str] = field(default_factory=dict)

    @property
    def checksum(self) -> str:
        """내용 해시. 재색인 필요 여부 판정에 쓴다."""
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()[:16]


def load_file(path: str | Path, root: str | Path | None = None) -> Document:
    """텍스트 파일 한 건을 문서로 읽는다."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in NEEDS_CONVERSION:
        raise RetrievalError(f"{p.name}: 직접 색인 불가. {NEEDS_CONVERSION[suffix]}")
    if suffix not in TEXT_SUFFIXES:
        raise RetrievalError(
            f"{p.name}: 지원하지 않는 확장자 {suffix!r}. 허용: {sorted(TEXT_SUFFIXES)}"
        )
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RetrievalError(f"{p.name}: UTF-8 아님. 인코딩 변환 후 반입 필요") from exc

    rel = str(p.relative_to(root)) if root is not None else p.name
    return Document(doc_id=rel, source=str(p), text=text, meta={"suffix": suffix})


def load_corpus(root: str | Path, skip_unsupported: bool = True) -> list[Document]:
    """디렉터리를 재귀 순회해 문서 목록을 만든다."""
    base = Path(root)
    if not base.is_dir():
        raise RetrievalError(f"코퍼스 디렉터리 없음: {base}")

    docs: list[Document] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        try:
            docs.append(load_file(path, root=base))
        except RetrievalError:
            if not skip_unsupported:
                raise
    return docs
