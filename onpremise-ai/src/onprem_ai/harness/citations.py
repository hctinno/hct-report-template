"""인용 검증.

작은 모델은 없는 번호를 붙이거나 아예 안 붙인다. 규칙 위반을
후처리에서 잡아 응답 신뢰도를 판정한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_CITE_RE = re.compile(r"\[(\d{1,2})\]")


@dataclass
class CitationReport:
    """인용 판정 결과."""

    used: list[int] = field(default_factory=list)
    invalid: list[int] = field(default_factory=list)
    uncited_sentences: int = 0
    total_sentences: int = 0

    @property
    def valid(self) -> bool:
        return not self.invalid and self.uncited_sentences == 0

    @property
    def coverage(self) -> float:
        """인용이 붙은 문장 비율."""
        if self.total_sentences == 0:
            return 0.0
        return (self.total_sentences - self.uncited_sentences) / self.total_sentences

    def summary(self) -> str:
        if self.valid:
            return f"인용 정상. 근거 {sorted(set(self.used))} 사용"
        parts = []
        if self.invalid:
            parts.append(f"존재하지 않는 근거 번호 {sorted(set(self.invalid))}")
        if self.uncited_sentences:
            parts.append(
                f"인용 없는 문장 {self.uncited_sentences}/{self.total_sentences}개"
            )
        return "인용 문제. " + ", ".join(parts)


def verify_citations(answer: str, evidence_count: int) -> CitationReport:
    """응답의 인용 번호가 실제 근거 범위 안인지 검사한다."""
    report = CitationReport()
    lines = [
        line.strip()
        for line in re.split(r"[\n]+", answer)
        if line.strip() and not line.strip().startswith("#")
    ]
    report.total_sentences = len(lines)

    for line in lines:
        marks = [int(m) for m in _CITE_RE.findall(line)]
        if not marks:
            report.uncited_sentences += 1
            continue
        for n in marks:
            if 1 <= n <= evidence_count:
                report.used.append(n)
            else:
                report.invalid.append(n)
    return report
