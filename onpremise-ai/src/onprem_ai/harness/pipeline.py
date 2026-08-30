"""RAG 질의응답 파이프라인.

가드 → 검색 → 근거 정화 → 프롬프트 조립 → 추론 → 인용 검증 → 감사.
각 단계가 무엇을 걸렀는지 `Answer` 에 남겨 사후 추적이 가능하게 한다.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, replace
from typing import Sequence

from ..config import Settings
from ..errors import GuardError
from ..llm.base import LLMBackend
from ..rag.retriever import Hit, HybridRetriever
from ..security.audit import AuditLog
from .citations import CitationReport, verify_citations
from .guard import GuardReport, guard_input, sanitize_context
from .prompt import NO_EVIDENCE, build_messages


@dataclass
class Answer:
    """응답 한 건과 그 근거·판정."""

    question: str
    text: str
    evidence: list[Hit] = field(default_factory=list)
    citations: CitationReport | None = None
    guard: GuardReport | None = None
    injections: list[str] = field(default_factory=list)
    elapsed_ms: int = 0
    refused: bool = False

    @property
    def sources(self) -> list[str]:
        """실제로 인용된 근거의 출처 문서 목록."""
        if self.citations is None:
            return sorted({h.doc_id for h in self.evidence})
        used = sorted(set(self.citations.used))
        return [self.evidence[n - 1].doc_id for n in used if n <= len(self.evidence)]

    @property
    def trustworthy(self) -> bool:
        """근거가 있고 인용도 온전하면 참."""
        return bool(self.evidence) and self.citations is not None and self.citations.valid


class RagPipeline:
    """검색 증강 질의응답 실행기."""

    def __init__(
        self,
        backend: LLMBackend,
        retriever: HybridRetriever,
        settings: Settings,
        audit: AuditLog | None = None,
    ) -> None:
        self.backend = backend
        self.retriever = retriever
        self.settings = settings
        self.audit = audit

    def ask(self, question: str) -> Answer:
        """질문 하나를 처리한다."""
        started = time.monotonic()
        try:
            clean_question, guard_report = guard_input(
                question, redact_secrets=self.settings.redact_secrets
            )
        except GuardError as exc:
            return Answer(
                question=question,
                text=f"요청 차단: {exc}",
                refused=True,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            )

        hits = self.retriever.search(
            clean_question,
            top_k=self.settings.top_k,
            candidate_k=self.settings.candidate_k,
            min_score=self.settings.min_score,
        )

        injections: list[str] = []
        safe_hits: list[Hit] = []
        for hit in hits:
            text, found = sanitize_context(hit.text)
            injections.extend(found)
            safe_hits.append(replace(hit, text=text))

        if not safe_hits and self.settings.refuse_without_evidence:
            answer = Answer(
                question=clean_question,
                text=NO_EVIDENCE,
                guard=guard_report,
                injections=injections,
                refused=True,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            )
            self._record(answer)
            return answer

        messages, used = build_messages(
            clean_question, safe_hits, budget_chars=self.settings.context_budget_chars
        )
        text = self.backend.chat(messages).strip()
        citations = verify_citations(text, evidence_count=len(used))

        answer = Answer(
            question=clean_question,
            text=text,
            evidence=used,
            citations=citations,
            guard=guard_report,
            injections=injections,
            elapsed_ms=int((time.monotonic() - started) * 1000),
            refused=text.startswith(NO_EVIDENCE),
        )
        self._record(answer)
        return answer

    def ask_many(self, questions: Sequence[str]) -> list[Answer]:
        return [self.ask(q) for q in questions]

    def _record(self, answer: Answer) -> None:
        if self.audit is None:
            return
        self.audit.append(
            "ask",
            question=answer.question,
            evidence=[h.chunk_id for h in answer.evidence],
            citation_valid=bool(answer.citations and answer.citations.valid),
            injections=answer.injections,
            refused=answer.refused,
            elapsed_ms=answer.elapsed_ms,
        )
