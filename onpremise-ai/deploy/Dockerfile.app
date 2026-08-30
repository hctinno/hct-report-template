# 응용 컨테이너.
#
# 서드파티 패키지를 설치하지 않는다. 폐쇄망 반입 시 pip 인덱스가 없고,
# 의존성이 늘수록 공급망 검증 부담이 커지기 때문이다.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY src/ /app/src/
COPY scripts/ /app/scripts/

# 비특권 사용자로 실행한다.
RUN useradd --system --uid 10001 --create-home onprem \
    && mkdir -p /var/onprem/index /var/onprem/audit \
    && chown -R onprem:onprem /app /var/onprem
USER onprem

ENTRYPOINT ["python", "-m", "onprem_ai"]
CMD ["doctor"]
