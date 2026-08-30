"""입출력 가드.

두 가지를 막는다. 하나는 비밀정보가 프롬프트나 로그로 흐르는 것,
다른 하나는 검색된 문서에 심긴 지시문이 모델을 조종하는 것이다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..errors import GuardError
from ..security.redact import Finding, redact, scan_secrets

#: 검색 문서 안에서 지시문처럼 보이는 패턴. 무력화 대상.
INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("override", re.compile(r"(?i)(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above)")),
    ("override_ko", re.compile(r"(?:이전|위의|앞의)\s*(?:지시|지침|규칙|명령)[을를]?\s*(?:무시|무효|취소)")),
    ("role_swap", re.compile(r"(?i)^\s*(?:system|assistant)\s*:", re.MULTILINE)),
    ("exfil", re.compile(r"(?i)(?:send|post|upload|전송|반출)\s+(?:this|the|해당)?\s*(?:to|로)\s*https?://")),
    ("tag_forge", re.compile(r"(?i)</?\s*(?:근거|system|instructions)\s*>")),
)

MARK = "[차단된 지시문]"


@dataclass
class GuardReport:
    """가드 판정 결과."""

    secrets: list[Finding] = field(default_factory=list)
    injections: list[str] = field(default_factory=list)
    blocked: bool = False
    reason: str = ""

    @property
    def clean(self) -> bool:
        return not self.secrets and not self.injections and not self.blocked


def guard_input(question: str, max_chars: int = 4000, redact_secrets: bool = True) -> tuple[str, GuardReport]:
    """사용자 질의를 검사한다. 비밀정보는 마스킹, 과대 입력은 차단."""
    report = GuardReport()
    text = question.strip()
    if not text:
        raise GuardError("빈 질의")
    if len(text) > max_chars:
        report.blocked = True
        report.reason = f"질의 길이 {len(text)}자, 상한 {max_chars}자 초과"
        raise GuardError(report.reason)

    if redact_secrets:
        text, report.secrets = redact(text)
    else:
        report.secrets = scan_secrets(text)
    return text, report


def sanitize_context(text: str) -> tuple[str, list[str]]:
    """검색된 문서에서 지시문 패턴을 무력화한다.

    삭제하지 않고 표식으로 바꾼다. 원문에 그런 문장이 있었다는 사실
    자체가 감사 대상이기 때문이다.
    """
    found: list[str] = []
    out = text
    for kind, pattern in INJECTION_PATTERNS:
        out, count = pattern.subn(MARK, out)
        if count:
            found.extend([kind] * count)
    return out, found
