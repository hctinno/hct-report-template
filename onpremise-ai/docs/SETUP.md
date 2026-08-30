# 설치

## 하드웨어 요건

| 항목 | 최소 | 권장 |
| --- | --- | --- |
| RAM | 16GB | 32GB |
| VRAM | 없음(CPU 추론) | 12GB 이상 |
| 저장 공간 | 40GB | 100GB |
| CPU | 8코어 | 16코어 |

GPU 없이도 동작한다. 12B 모델 CPU 추론은 응답까지 수십 초가 걸린다. 대화형
용도라면 GPU 를 권한다.

## 소프트웨어 요건

- Python 3.11 이상 (표준 라이브러리만 사용)
- Docker 24 이상, Docker Compose v2 (컨테이너 배포 시)

파이썬 서드파티 패키지는 설치하지 않는다.

## 로컬 개발 (격리 전)

```
git clone <저장소 주소>
cd onpremise-ai

# 모델 없이 파이프라인 확인
PYTHONPATH=src python3 -m onprem_ai --backend mock --allow-egress ingest
PYTHONPATH=src python3 -m onprem_ai --backend mock --allow-egress ask "격리 원칙은?"

# 테스트
scripts/run_tests.sh
```

`--backend mock` 은 결정적 스텁이다. 가중치 없이 검색·가드·인용 검증 경로를
전부 통과시킨다.

`--allow-egress` 는 개발 편의 옵션이다. 운영에서는 쓰지 않는다.

## 실제 모델로 (격리 후)

```
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d runtime
# deploy/models/README.md 절차로 가중치 반입
docker compose -f deploy/docker-compose.yml run --rm app doctor
docker compose -f deploy/docker-compose.yml run --rm app ingest
docker compose -f deploy/docker-compose.yml run --rm app ask "격리 원칙은?"
```

## 설정

`.env.example` 을 `.env` 로 복사해 값을 채운다. 실제 환경변수가 `.env` 를 덮는다.

주요 값은 `README.md` 의 설정 표를 본다.
