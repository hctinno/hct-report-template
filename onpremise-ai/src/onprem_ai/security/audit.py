"""감사 로그.

해시 체인으로 이어 붙여 사후 변조를 탐지한다. 폐쇄망 운영에서
"누가 무엇을 물었나" 는 남기되, 원문 비밀정보는 남기지 않는다.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64


@dataclass(frozen=True)
class AuditRecord:
    """감사 항목 한 건."""

    ts: str
    event: str
    actor: str
    detail: dict[str, object] = field(default_factory=dict)
    prev_hash: str = GENESIS
    hash: str = ""

    def compute_hash(self) -> str:
        payload = json.dumps(
            {
                "ts": self.ts,
                "event": self.event,
                "actor": self.actor,
                "detail": self.detail,
                "prev_hash": self.prev_hash,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditLog:
    """JSONL 감사 로그. 한 줄이 한 레코드."""

    def __init__(self, path: str | Path, actor: str | None = None) -> None:
        self.path = Path(path)
        self.actor = actor or os.environ.get("USER") or "unknown"

    def _last_hash(self) -> str:
        if not self.path.is_file():
            return GENESIS
        last = GENESIS
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if raw.strip():
                last = json.loads(raw).get("hash", last)
        return last

    def append(self, event: str, **detail: object) -> AuditRecord:
        """레코드를 이어 붙이고 저장한 레코드를 반환."""
        from .redact import redact

        safe = {
            k: redact(v)[0] if isinstance(v, str) else v for k, v in detail.items()
        }
        base = AuditRecord(
            ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            event=event,
            actor=self.actor,
            detail=safe,
            prev_hash=self._last_hash(),
        )
        record = AuditRecord(**{**asdict(base), "hash": base.compute_hash()})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        return record

    def records(self) -> list[AuditRecord]:
        if not self.path.is_file():
            return []
        return [
            AuditRecord(**json.loads(raw))
            for raw in self.path.read_text(encoding="utf-8").splitlines()
            if raw.strip()
        ]

    def verify(self) -> tuple[bool, str]:
        """체인 무결성을 검사한다. (정상 여부, 사유)."""
        prev = GENESIS
        for i, record in enumerate(self.records(), 1):
            if record.prev_hash != prev:
                return False, f"{i}번째 레코드의 prev_hash 불일치"
            if record.compute_hash() != record.hash:
                return False, f"{i}번째 레코드 내용이 해시와 불일치"
            prev = record.hash
        return True, "체인 정상"
