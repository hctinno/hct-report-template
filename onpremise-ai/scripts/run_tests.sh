#!/usr/bin/env sh
# 테스트 실행. 서드파티 러너를 요구하지 않는다.
set -eu

cd "$(dirname "$0")/.."
PYTHONPATH="src:." python3 -m unittest discover -s tests -t . "$@"
