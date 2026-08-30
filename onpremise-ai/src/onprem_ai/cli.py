"""명령줄 진입점.

`python -m onprem_ai <명령>` 으로 쓴다. 하위 명령은 ingest, ask,
doctor, eval, audit 다섯이다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import Settings, load_settings
from .errors import IsolationError, OnPremError
from .evaluate import evaluate, load_cases
from .harness.pipeline import RagPipeline
from .llm.base import build_backend
from .rag.chunker import chunk_text
from .rag.loaders import load_corpus
from .rag.retriever import HybridRetriever
from .security.audit import AuditLog
from .security.egress import check_egress


def _settings(args: argparse.Namespace) -> Settings:
    base = load_settings()
    return base.with_overrides(
        backend=getattr(args, "backend", None),
        corpus_dir=Path(args.corpus) if getattr(args, "corpus", None) else None,
        index_dir=Path(args.index) if getattr(args, "index", None) else None,
        audit_log=Path(args.audit_log) if getattr(args, "audit_log", None) else None,
        top_k=getattr(args, "top_k", None),
    )


def _preflight(settings: Settings, skip: bool) -> None:
    """격리 점검. 실패하면 실행을 막는다."""
    if skip or not settings.enforce_isolation:
        return
    report = check_egress()
    if not report.isolated:
        raise IsolationError(
            report.summary()
            + "\n격리 상태에서만 실행하도록 설정됨. 개발 중이면 --allow-egress 사용"
        )


# --- 하위 명령 ---------------------------------------------------------
def cmd_ingest(args: argparse.Namespace) -> int:
    settings = _settings(args)
    _preflight(settings, args.allow_egress)

    docs = load_corpus(settings.corpus_dir)
    if not docs:
        print(f"코퍼스 비어 있음: {settings.corpus_dir}", file=sys.stderr)
        return 1

    chunks = [
        c
        for doc in docs
        for c in chunk_text(
            doc.text,
            doc.doc_id,
            size=settings.chunk_size,
            overlap=settings.chunk_overlap,
            meta={"source": doc.source, "checksum": doc.checksum},
        )
    ]
    backend = build_backend(settings)
    retriever = HybridRetriever.build(backend, chunks)
    target = retriever.save(settings.index_dir)

    AuditLog(settings.audit_log).append(
        "ingest", docs=len(docs), chunks=len(chunks), index=str(target)
    )
    print(f"문서 {len(docs)}건 → 청크 {len(chunks)}건 색인 완료: {target}")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    settings = _settings(args)
    _preflight(settings, args.allow_egress)

    backend = build_backend(settings)
    retriever = HybridRetriever.load(backend, settings.index_dir)
    pipeline = RagPipeline(backend, retriever, settings, AuditLog(settings.audit_log))

    answer = pipeline.ask(" ".join(args.question))
    print(answer.text)
    if answer.evidence:
        print("\n근거:")
        for i, hit in enumerate(answer.evidence, 1):
            print(f"  [{i}] {hit.doc_id} ({hit.matched_by}, {hit.score:.4f})")
    if answer.citations and not answer.citations.valid:
        print(f"\n경고: {answer.citations.summary()}", file=sys.stderr)
    if answer.injections:
        print(f"경고: 근거에서 지시문 패턴 차단 {answer.injections}", file=sys.stderr)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    settings = _settings(args)
    print(f"설정 출처: {settings.source}")
    print(f"백엔드: {settings.backend} @ {settings.base_url}")
    print(f"모델: chat={settings.chat_model}, embed={settings.embed_model}")

    report = check_egress()
    print(f"격리: {report.summary()}")

    try:
        health = build_backend(settings).health()
        print(f"런타임: 응답 정상, 설치 모델 {len(health['models'])}종")
        print(f"  chat 준비: {health['chat_model_ready']}, embed 준비: {health['embed_model_ready']}")
    except OnPremError as exc:
        print(f"런타임: 실패 - {exc}", file=sys.stderr)

    index = Path(settings.index_dir) / "vectors.jsonl"
    print(f"색인: {'있음' if index.is_file() else '없음'} ({index})")

    ok, reason = AuditLog(settings.audit_log).verify()
    print(f"감사 로그: {reason}")
    return 0 if report.isolated or not settings.enforce_isolation else 2


def cmd_eval(args: argparse.Namespace) -> int:
    settings = _settings(args)
    _preflight(settings, args.allow_egress)

    backend = build_backend(settings)
    retriever = HybridRetriever.load(backend, settings.index_dir)
    pipeline = RagPipeline(backend, retriever, settings)
    result = evaluate(pipeline, load_cases(args.cases))
    print(result.report())
    return 0 if not result.failures else 1


def cmd_audit(args: argparse.Namespace) -> int:
    log = AuditLog(_settings(args).audit_log)
    ok, reason = log.verify()
    print(f"{reason} (레코드 {len(log.records())}건)")
    return 0 if ok else 1


# --- 파서 -------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="onprem_ai", description="폐쇄망 로컬 AI 질의응답 스택"
    )
    parser.add_argument("--backend", help="ollama | mock")
    parser.add_argument("--corpus", help="코퍼스 디렉터리")
    parser.add_argument("--index", help="색인 디렉터리")
    parser.add_argument("--audit-log", help="감사 로그 경로")
    parser.add_argument(
        "--allow-egress", action="store_true", help="격리 점검을 건너뛴다(개발용)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ingest", help="코퍼스를 색인").set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="질문")
    p_ask.add_argument("question", nargs="+")
    p_ask.add_argument("--top-k", type=int)
    p_ask.set_defaults(func=cmd_ask)

    sub.add_parser("doctor", help="환경 진단").set_defaults(func=cmd_doctor)

    p_eval = sub.add_parser("eval", help="골든셋 평가")
    p_eval.add_argument("--cases", default="data/eval/golden.jsonl")
    p_eval.set_defaults(func=cmd_eval)

    sub.add_parser("audit", help="감사 로그 검증").set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except OnPremError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
