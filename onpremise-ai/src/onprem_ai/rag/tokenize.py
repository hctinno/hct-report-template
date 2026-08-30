"""토크나이저.

한국어는 형태소 분석기 없이도 쓸 수 있게 어절 토큰과 음절 바이그램을
함께 낸다. 폐쇄망에서 추가 사전 반입 없이 동작하는 것이 목적이다.
"""

from __future__ import annotations

import re
import unicodedata

_WORD_RE = re.compile(r"[0-9A-Za-z]+|[가-힣]+|[぀-ヿ一-鿿]+")
_HANGUL_RE = re.compile(r"[가-힣]")


def normalize(text: str) -> str:
    """NFKC 정규화 후 소문자화. 색인과 질의에 같은 함수를 쓴다."""
    return unicodedata.normalize("NFKC", text).lower()


def _bigrams(token: str) -> list[str]:
    return [token[i : i + 2] for i in range(len(token) - 1)]


def tokenize(text: str) -> list[str]:
    """검색용 토큰 목록.

    한글·CJK 덩어리는 원형과 음절 바이그램을 함께 낸다. 두 글자
    이상이면 부분 일치가 가능해져 조사 변화에 덜 민감해진다.
    """
    tokens: list[str] = []
    for match in _WORD_RE.findall(normalize(text)):
        tokens.append(match)
        if len(match) > 2 and (_HANGUL_RE.search(match) or not match.isascii()):
            tokens.extend(_bigrams(match))
    return tokens
