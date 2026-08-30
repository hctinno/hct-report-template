"""외부 망 차단 검증.

"격리했다"는 선언이 아니라 측정으로 확인한다. 컨테이너 기동 시
이 검사를 통과하지 못하면 서비스를 올리지 않는 것이 운영 전제다.
"""

from __future__ import annotations

import socket
from dataclasses import dataclass, field

#: 도달 가능하면 격리 실패로 보는 대표 목적지. (호스트, 포트)
PROBE_TARGETS: tuple[tuple[str, int], ...] = (
    ("8.8.8.8", 53),
    ("1.1.1.1", 53),
    ("93.184.216.34", 80),
)

#: DNS 로 풀리면 외부 이름 해석이 살아 있다고 본다.
DNS_PROBES: tuple[str, ...] = ("example.com", "api.openai.com")


@dataclass
class EgressReport:
    """격리 점검 결과."""

    reachable: list[str] = field(default_factory=list)
    resolvable: list[str] = field(default_factory=list)
    checked: int = 0

    @property
    def isolated(self) -> bool:
        """외부로 나가는 경로가 하나도 없으면 참."""
        return not self.reachable and not self.resolvable

    def summary(self) -> str:
        if self.isolated:
            return f"격리 양호. 점검 대상 {self.checked}건 전부 차단됨"
        parts = []
        if self.reachable:
            parts.append(f"TCP 도달 {len(self.reachable)}건: {', '.join(self.reachable)}")
        if self.resolvable:
            parts.append(f"DNS 해석 {len(self.resolvable)}건: {', '.join(self.resolvable)}")
        return "격리 실패. " + " / ".join(parts)


def check_egress(
    targets: tuple[tuple[str, int], ...] = PROBE_TARGETS,
    dns_probes: tuple[str, ...] = DNS_PROBES,
    timeout: float = 1.5,
) -> EgressReport:
    """외부 TCP 연결과 DNS 해석 가능 여부를 실측한다."""
    report = EgressReport()

    for host, port in targets:
        report.checked += 1
        try:
            with socket.create_connection((host, port), timeout=timeout):
                report.reachable.append(f"{host}:{port}")
        except OSError:
            pass  # 차단이 정상 상태

    for name in dns_probes:
        report.checked += 1
        try:
            socket.getaddrinfo(name, None)
            report.resolvable.append(name)
        except OSError:
            pass

    return report


def assert_isolated(report: EgressReport | None = None) -> EgressReport:
    """격리되지 않았으면 `IsolationError` 를 던진다."""
    from ..errors import IsolationError

    result = report if report is not None else check_egress()
    if not result.isolated:
        raise IsolationError(result.summary())
    return result
