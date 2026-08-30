#!/usr/bin/env sh
# 기동 전 격리 점검. 실패하면 0 이 아닌 코드로 끝난다.
#
# 컨테이너 entrypoint 앞에 두거나 systemd ExecStartPre 로 건다.
set -eu

PYTHONPATH="${PYTHONPATH:-/app/src}"
export PYTHONPATH

echo "[preflight] 격리 점검 시작"
python - <<'PY'
import sys

from onprem_ai.security.egress import check_egress

report = check_egress()
print(f"[preflight] {report.summary()}")
sys.exit(0 if report.isolated else 3)
PY
echo "[preflight] 통과"
