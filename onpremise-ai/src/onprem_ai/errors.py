"""프로젝트 공통 예외."""


class OnPremError(Exception):
    """모든 프로젝트 예외의 최상위."""


class ConfigError(OnPremError):
    """설정 값이 잘못되었을 때."""


class BackendError(OnPremError):
    """로컬 추론 백엔드 호출 실패."""


class IsolationError(OnPremError):
    """격리 정책 위반. 외부 망 접근이 가능한 상태 등."""


class GuardError(OnPremError):
    """입출력 가드가 차단한 요청."""


class RetrievalError(OnPremError):
    """색인·검색 단계 실패."""
