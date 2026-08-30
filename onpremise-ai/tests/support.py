"""테스트 공용 도우미."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from onprem_ai.config import Settings  # noqa: E402
from onprem_ai.llm.mock import MockBackend  # noqa: E402
from onprem_ai.rag.chunker import chunk_text  # noqa: E402
from onprem_ai.rag.retriever import HybridRetriever  # noqa: E402

DOCS = {
    "isolation.md": (
        "추론 컨테이너는 외부 인터넷으로 나가는 경로를 갖지 않는다. "
        "DNS 해석이 가능하면 격리 실패로 판정한다. 기동 시 egress 점검을 수행한다."
    ),
    "rag.md": (
        "하이브리드 검색은 BM25 와 임베딩 코사인 유사도를 RRF 로 결합한다. "
        "가중합 대신 순위 결합을 쓰는 이유는 점수 스케일이 다르기 때문이다."
    ),
    "weights.md": (
        "모델 가중치는 승인된 매체로만 반입한다. 반입 전후로 SHA256 해시를 대조한다."
    ),
}


def make_settings(**overrides: object) -> Settings:
    """테스트 기본 설정."""
    base = Settings(backend="mock", enforce_isolation=False, top_k=3, candidate_k=10)
    return base.with_overrides(**overrides) if overrides else base


def make_retriever(docs: dict[str, str] | None = None) -> HybridRetriever:
    """메모리 상의 작은 색인을 만든다."""
    corpus = DOCS if docs is None else docs
    chunks = [
        c
        for doc_id, text in corpus.items()
        for c in chunk_text(text, doc_id, size=300, overlap=50)
    ]
    return HybridRetriever.build(MockBackend(make_settings()), chunks)
