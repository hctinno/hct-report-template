"""설정 로딩.

우선순위: 명시 인자 > 환경변수 > 기본값. 폐쇄망에서 .env 파일을 읽되
파싱은 표준 라이브러리로만 처리한다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path

from .errors import ConfigError

_ENV_PREFIX = "ONPREM_"

#: 로컬 백엔드로 허용하는 호스트. 격리 원칙상 루프백만 허용한다.
ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "::1", "host.docker.internal"})


def load_dotenv(path: str | os.PathLike[str]) -> dict[str, str]:
    """`KEY=VALUE` 형식 파일을 읽어 사전으로 반환. 없는 파일은 빈 사전."""
    result: dict[str, str] = {}
    p = Path(path)
    if not p.is_file():
        return result
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        result[key.strip()] = value
    return result


@dataclass(frozen=True)
class Settings:
    """런타임 설정 한 벌."""

    # 추론 백엔드
    backend: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    chat_model: str = "gemma3:12b"
    embed_model: str = "bge-m3"
    request_timeout: float = 120.0
    temperature: float = 0.2
    num_ctx: int = 8192

    # RAG
    corpus_dir: Path = Path("data/corpus")
    index_dir: Path = Path("var/index")
    chunk_size: int = 700
    chunk_overlap: int = 120
    top_k: int = 5
    candidate_k: int = 30
    min_score: float = 0.05

    # 하네스
    context_budget_chars: int = 6000
    require_citation: bool = True
    refuse_without_evidence: bool = True

    # 보안
    enforce_isolation: bool = True
    audit_log: Path = Path("var/audit/audit.jsonl")
    redact_secrets: bool = True

    #: 설정이 유래한 소스 표시. 진단 출력용.
    source: str = "default"
    extra: dict[str, str] = field(default_factory=dict)

    def validated(self) -> "Settings":
        """값 범위를 검사한 자기 자신을 반환."""
        if self.chunk_size <= 0:
            raise ConfigError("chunk_size 는 1 이상이어야 함")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ConfigError("chunk_overlap 은 0 이상 chunk_size 미만이어야 함")
        if self.top_k <= 0:
            raise ConfigError("top_k 는 1 이상이어야 함")
        if self.candidate_k < self.top_k:
            raise ConfigError("candidate_k 는 top_k 이상이어야 함")
        if not 0.0 <= self.temperature <= 2.0:
            raise ConfigError("temperature 는 0.0~2.0 범위")
        if self.context_budget_chars <= 0:
            raise ConfigError("context_budget_chars 는 1 이상이어야 함")
        assert_local_url(self.base_url)
        return self

    def with_overrides(self, **kwargs: object) -> "Settings":
        """일부 필드만 바꾼 새 설정을 반환."""
        clean = {k: v for k, v in kwargs.items() if v is not None}
        return replace(self, **clean).validated()  # type: ignore[arg-type]


def assert_local_url(url: str) -> None:
    """백엔드 주소가 루프백인지 확인. 아니면 격리 위반으로 본다."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ConfigError(f"지원하지 않는 스킴: {parsed.scheme!r}")
    host = (parsed.hostname or "").strip("[]")
    if host not in ALLOWED_HOSTS:
        raise ConfigError(
            f"로컬 백엔드만 허용. 허용 목록 밖 호스트: {host!r}. "
            "외부 API 를 가리키면 폐쇄망 전제가 깨진다."
        )


def _coerce(raw: str, sample: object) -> object:
    if isinstance(sample, bool):
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    if isinstance(sample, int):
        return int(raw)
    if isinstance(sample, float):
        return float(raw)
    if isinstance(sample, Path):
        return Path(raw)
    return raw


def load_settings(
    env: dict[str, str] | None = None,
    dotenv_path: str | os.PathLike[str] | None = ".env",
) -> Settings:
    """환경변수와 .env 를 합쳐 설정을 만든다.

    실제 환경변수가 .env 값을 덮는다. 키는 `ONPREM_` 접두사에 대문자 필드명.
    """
    merged: dict[str, str] = {}
    if dotenv_path is not None:
        merged.update(load_dotenv(dotenv_path))
    merged.update(env if env is not None else os.environ)

    base = Settings()
    overrides: dict[str, object] = {}
    known = {f.name for f in Settings.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    for key, value in merged.items():
        if not key.startswith(_ENV_PREFIX):
            continue
        field_name = key[len(_ENV_PREFIX) :].lower()
        if field_name not in known or field_name in {"extra", "source"}:
            continue
        try:
            overrides[field_name] = _coerce(value, getattr(base, field_name))
        except ValueError as exc:
            raise ConfigError(f"{key} 값 변환 실패: {value!r}") from exc

    overrides["source"] = "env" if overrides else "default"
    return replace(base, **overrides).validated()  # type: ignore[arg-type]
