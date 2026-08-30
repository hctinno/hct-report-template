"""골든셋 평가.

모델을 바꾸거나 청크 크기를 손볼 때 감으로 판단하지 않기 위한 최소
계측이다. 검색 품질과 하네스 준수를 나눠서 본다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .harness.pipeline import RagPipeline


@dataclass(frozen=True)
class EvalCase:
    """평가 항목. `expect_docs` 는 정답 근거 문서 id."""

    question: str
    expect_docs: list[str] = field(default_factory=list)
    expect_refusal: bool = False


@dataclass
class EvalResult:
    """평가 집계."""

    total: int = 0
    retrieval_hits: int = 0
    citation_valid: int = 0
    refusal_correct: int = 0
    failures: list[str] = field(default_factory=list)

    @property
    def recall(self) -> float:
        return self.retrieval_hits / self.total if self.total else 0.0

    @property
    def citation_rate(self) -> float:
        return self.citation_valid / self.total if self.total else 0.0

    def report(self) -> str:
        lines = [
            f"평가 항목: {self.total}건",
            f"근거 적중률: {self.recall:.0%}",
            f"인용 준수율: {self.citation_rate:.0%}",
            f"거절 판정 일치: {self.refusal_correct}/{self.total}",
        ]
        if self.failures:
            lines.append("실패 항목:")
            lines.extend(f"  - {f}" for f in self.failures)
        return "\n".join(lines)


def load_cases(path: str | Path) -> list[EvalCase]:
    """JSONL 골든셋을 읽는다."""
    p = Path(path)
    cases: list[EvalCase] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("//"):
            continue
        data = json.loads(raw)
        cases.append(
            EvalCase(
                question=data["question"],
                expect_docs=list(data.get("expect_docs", [])),
                expect_refusal=bool(data.get("expect_refusal", False)),
            )
        )
    return cases


def evaluate(pipeline: RagPipeline, cases: Sequence[EvalCase]) -> EvalResult:
    """골든셋을 돌려 집계를 낸다."""
    result = EvalResult(total=len(cases))
    for case in cases:
        answer = pipeline.ask(case.question)

        if answer.refused == case.expect_refusal:
            result.refusal_correct += 1
        else:
            result.failures.append(
                f"{case.question[:30]}: 거절 기대 {case.expect_refusal}, 실제 {answer.refused}"
            )

        if case.expect_docs:
            retrieved = {h.doc_id for h in answer.evidence}
            if retrieved & set(case.expect_docs):
                result.retrieval_hits += 1
            else:
                result.failures.append(
                    f"{case.question[:30]}: 기대 근거 {case.expect_docs}, 실제 {sorted(retrieved)}"
                )
        elif case.expect_refusal:
            result.retrieval_hits += 1

        if answer.citations is not None and answer.citations.valid:
            result.citation_valid += 1
        elif case.expect_refusal:
            result.citation_valid += 1
    return result
