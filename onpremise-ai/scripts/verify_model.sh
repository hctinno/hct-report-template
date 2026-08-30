#!/usr/bin/env sh
# 반입 가중치 해시 검증. 인자: <가중치 파일> <기대 sha256>
set -eu

if [ "$#" -ne 2 ]; then
    echo "사용법: $0 <가중치 파일> <기대 sha256>" >&2
    exit 2
fi

file="$1"
expected="$2"

if [ ! -f "$file" ]; then
    echo "파일 없음: $file" >&2
    exit 1
fi

actual="$(sha256sum "$file" | cut -d' ' -f1)"

if [ "$actual" = "$expected" ]; then
    echo "검증 통과: $file"
    echo "  sha256=$actual"
    exit 0
fi

echo "검증 실패. 해당 가중치는 폐기 대상" >&2
echo "  기대=$expected" >&2
echo "  실제=$actual" >&2
exit 1
