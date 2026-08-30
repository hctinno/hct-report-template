# 온프레미스 AI

> **이 디렉터리는 독립 저장소로 분리하기 위한 완결된 프로젝트다.**
> 현 세션의 GitHub 권한으로는 새 저장소를 만들 수 없어(`POST /user/repos` 403)
> `hct-report-template` 의 브랜치에 임시로 담았다. 아래 한 줄로 떼어낸다.
>
> ```
> git subtree split --prefix=onpremise-ai -b onpremise-ai-main
> ```
>
> 분리 후 이 안내 블록을 지운다.

사내 PC 에서 도는 로컬 LLM 을 **네트워크가 끊긴 격리 환경**에 두고, 그 위에
RAG 와 하네스를 올린 스택이다. 플래그십 API 를 쓰지 않는다.

호스트 PC 는 사내망에 연결돼 있다. 격리 대상은 PC 가 아니라 추론 런타임과 그
위의 응용이다. 컨테이너 네트워크에 게이트웨이를 두지 않아 외부로 나가는 경로
자체를 없앤다.

## 무엇을 하는가

| 축 | 내용 |
| --- | --- |
| 격리 | internal 네트워크 + egress 실측 점검. 통과 못 하면 실행 안 함 |
| 로컬 추론 | Ollama/GGUF 런타임. 루프백 아닌 주소는 설정 단계에서 거부 |
| RAG | BM25 + 임베딩 하이브리드 검색, RRF 결합, 한국어 바이그램 색인 |
| 하네스 | 입력 마스킹, 근거 주입 방어, 인용 검증, 근거 없으면 거절 |
| 감사 | 해시 체인 JSONL. 중간 레코드 조작·삭제를 검출 |
| 계측 | 골든셋 평가로 근거 적중률·인용 준수율 추적 |

## 빠른 시작

가중치 없이 파이프라인 전체를 확인할 수 있다.

```
PYTHONPATH=src python3 -m onprem_ai --backend mock --allow-egress ingest
PYTHONPATH=src python3 -m onprem_ai --backend mock --allow-egress ask "격리 원칙은?"
```

테스트:

```
scripts/run_tests.sh
```

실제 모델로 격리 구동하는 절차는 `docs/SETUP.md` 를 본다.

## 명령

| 명령 | 설명 |
| --- | --- |
| `ingest` | 코퍼스를 청킹·임베딩해 색인 |
| `ask "질문"` | 하이브리드 검색 후 근거 기반 응답 |
| `doctor` | 격리·런타임·색인·감사 상태 진단 |
| `eval` | 골든셋으로 검색·인용 품질 계측 |
| `audit` | 감사 로그 해시 체인 검증 |

공통 옵션: `--backend`, `--corpus`, `--index`, `--audit-log`, `--allow-egress`

## 설정

`ONPREM_` 접두사 환경변수 또는 `.env` 로 준다. 실제 환경변수가 `.env` 를 덮는다.

| 키 | 기본값 | 설명 |
| --- | --- | --- |
| `ONPREM_BACKEND` | `ollama` | `ollama` 또는 `mock` |
| `ONPREM_BASE_URL` | `http://127.0.0.1:11434` | 루프백만 허용 |
| `ONPREM_CHAT_MODEL` | `gemma3:12b` | 채팅 모델 태그 |
| `ONPREM_EMBED_MODEL` | `bge-m3` | 임베딩 모델 태그 |
| `ONPREM_CHUNK_SIZE` | `700` | 청크 목표 길이 |
| `ONPREM_CHUNK_OVERLAP` | `120` | 겹침 길이 |
| `ONPREM_TOP_K` | `5` | 프롬프트에 넣을 근거 수 |
| `ONPREM_CANDIDATE_K` | `30` | 결합 전 후보 수 |
| `ONPREM_CONTEXT_BUDGET_CHARS` | `6000` | 근거 블록 예산 |
| `ONPREM_ENFORCE_ISOLATION` | `true` | 격리 실패 시 실행 차단 |
| `ONPREM_REDACT_SECRETS` | `true` | 프롬프트 진입 전 마스킹 |
| `ONPREM_REFUSE_WITHOUT_EVIDENCE` | `true` | 근거 없으면 거절 |

모델 태그는 설정 값이다. 세대가 올라가면 코드가 아니라 이 값을 바꾼다.

## 구조

```
src/onprem_ai/
  config.py        설정 병합, 원격 URL 거부
  cli.py           명령 5종
  evaluate.py      골든셋 평가
  llm/             로컬 백엔드 (ollama, mock)
  rag/             적재·청킹·토크나이저·BM25·벡터·하이브리드
  harness/         가드·프롬프트·인용 검증·파이프라인
  security/        egress 점검·마스킹·감사 체인
deploy/            internal 네트워크 compose, Dockerfile, 반입 절차
docs/              아키텍처·보안·RAG·하네스·운영·설치·로드맵
tests/             표준 라이브러리 테스트
```

## 설계 원칙

**서드파티 의존성을 두지 않는다.** 폐쇄망에는 pip 인덱스가 없다. 휠 반입은 그
자체로 공급망 검증 대상이다. 표준 라이브러리로 안 되는 지점에 도달하면 그때
도입한다.

**격리는 측정한다.** 선언하지 않는다. `doctor` 가 실제로 외부 TCP 연결과 DNS
해석을 시도해 하나라도 성공하면 실패로 판정한다.

**막지 못하는 것을 적어 둔다.** `docs/SECURITY.md` 의 한계 절이 그것이다.
막는다고 믿는 것보다 안전하다.

## 문서

| 문서 | 내용 |
| --- | --- |
| `docs/ARCHITECTURE.md` | 격리 경계와 계층 구조, 질의 흐름 |
| `docs/SECURITY.md` | 위협 모델, 마스킹, 주입 방어, 한계 |
| `docs/RAG.md` | 하이브리드 검색, 한국어 처리, 청킹, 성능 특성 |
| `docs/HARNESS.md` | 소형 모델 제어, 프롬프트, 출력 검증, 계측 |
| `docs/SETUP.md` | 하드웨어 요건, 개발·운영 구동 |
| `docs/OPERATIONS.md` | 일상 운영, 점검 주기, 장애 대응 |
| `docs/ROADMAP.md` | 단계별 계획, 하지 않기로 한 것 |
