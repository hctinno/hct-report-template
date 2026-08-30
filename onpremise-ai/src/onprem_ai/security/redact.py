"""비밀정보·개인정보 탐지와 마스킹.

프롬프트로 들어가는 문자열과 로그로 나가는 문자열 양쪽에 적용한다.
탐지 규칙은 사내 실사용 형식에 맞춰 늘려 가는 것을 전제로 한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MASK = "[REDACTED:{kind}]"


@dataclass(frozen=True)
class Finding:
    """탐지 한 건."""

    kind: str
    start: int
    end: int
    preview: str


#: (종류, 정규식). 순서가 우선순위다.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("rrn", re.compile(r"\b\d{6}[-\s]?[1-4]\d{6}\b")),
    ("aws_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("bearer", re.compile(r"\b[Bb]earer\s+[A-Za-z0-9._\-]{20,}")),
    ("api_key", re.compile(r"\b(?:sk|pk|ghp|gho|glpat)[-_][A-Za-z0-9]{16,}\b")),
    ("password_kv", re.compile(r"(?i)\b(?:password|passwd|비밀번호)\s*[:=]\s*\S{4,}")),
    ("card", re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]{2,}\b")),
    ("phone_kr", re.compile(r"\b01[016789][-\s]?\d{3,4}[-\s]?\d{4}\b")),
)


def scan_secrets(text: str, kinds: set[str] | None = None) -> list[Finding]:
    """탐지 목록을 위치 순으로 반환. 겹치는 구간은 앞 규칙이 이긴다."""
    found: list[Finding] = []
    taken: list[tuple[int, int]] = []
    for kind, pattern in PATTERNS:
        if kinds is not None and kind not in kinds:
            continue
        for m in pattern.finditer(text):
            if any(m.start() < e and s < m.end() for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            found.append(
                Finding(kind=kind, start=m.start(), end=m.end(), preview=m.group()[:4] + "…")
            )
    found.sort(key=lambda f: f.start)
    return found


def redact(text: str, kinds: set[str] | None = None) -> tuple[str, list[Finding]]:
    """탐지된 구간을 마스크로 바꾼 문자열과 탐지 목록을 반환."""
    findings = scan_secrets(text, kinds=kinds)
    if not findings:
        return text, []
    out: list[str] = []
    cursor = 0
    for f in findings:
        out.append(text[cursor : f.start])
        out.append(MASK.format(kind=f.kind))
        cursor = f.end
    out.append(text[cursor:])
    return "".join(out), findings
