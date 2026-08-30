# 운영 절차

## 초기 구축

1. 호스트 PC 사양 확인. `docs/SETUP.md` 의 최소 요건을 본다.
2. 이미지 빌드: `docker compose -f deploy/docker-compose.yml build`
3. 런타임 기동: `docker compose -f deploy/docker-compose.yml up -d runtime`
4. 가중치 반입: `deploy/models/README.md` 절차를 따른다.
5. 격리 확인: `docker compose -f deploy/docker-compose.yml run --rm app doctor`
6. 색인: `docker compose -f deploy/docker-compose.yml run --rm app ingest`

5번에서 격리 실패가 나오면 6번으로 넘어가지 않는다.

## 일상 운영

| 작업 | 명령 |
| --- | --- |
| 질의 | `docker compose run --rm app ask "질문"` |
| 문서 갱신 후 재색인 | `docker compose run --rm app ingest` |
| 환경 진단 | `docker compose run --rm app doctor` |
| 감사 로그 검증 | `docker compose run --rm app audit` |
| 품질 계측 | `docker compose run --rm app eval` |

## 점검 주기

| 항목 | 주기 | 판정 기준 |
| --- | --- | --- |
| 격리 점검 | 기동 시마다 | `doctor` 격리 양호 |
| 감사 체인 | 주 1회 | `audit` 체인 정상 |
| 골든셋 평가 | 코퍼스·모델 변경 시 | 근거 적중률 하락 없음 |
| 가중치 해시 | 반입 시 | SHA256 일치 |

## 반입 대장

가중치를 반입할 때마다 아래 표에 한 줄을 추가한다.

| 일자 | 모델 | 양자화 | SHA256(앞 16자) | 승인 번호 | 담당 |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## 장애 대응

**`ask` 가 "색인 파일 없음" 을 낸다**
색인 볼륨이 비었다. `ingest` 를 먼저 돌린다.

**`doctor` 가 런타임 실패를 낸다**
`docker compose ps` 로 runtime 상태를 본다. healthcheck 가 통과하려면 가중치가
하나 이상 등록돼 있어야 한다.

**`doctor` 가 격리 실패를 낸다**
`docker network inspect onprem-ai_ai_internal` 에서 `Internal: true` 를 확인한다.
거짓이면 네트워크를 지우고 compose 를 다시 올린다. compose 파일에서
`internal: true` 를 지운 변경이 있었는지 이력을 본다.

**응답에 인용 경고가 계속 붙는다**
모델이 규칙을 못 따르고 있다. 순서대로 본다.
1. `eval` 로 인용 준수율을 수치로 확인
2. 컨텍스트 예산을 줄여 근거 수를 낮춤
3. 더 큰 양자화 또는 더 큰 파라미터 모델로 교체

**차원 불일치 오류**
임베딩 모델이 바뀌었다. 색인 볼륨을 비우고 전체 재색인한다.

## 백업

백업 대상은 세 가지다.

- `data/corpus/` — 원본 문서
- `audit` 볼륨 — 감사 로그. 체인 검증을 위해 전체를 보관한다.
- 반입 대장

색인 볼륨은 백업하지 않는다. 코퍼스에서 언제든 다시 만든다.
