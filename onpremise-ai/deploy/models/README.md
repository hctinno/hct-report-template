# 모델 가중치 반입 절차

폐쇄망 안에서는 `ollama pull` 이 동작하지 않는다. 의도한 상태다.
가중치는 아래 절차로만 들어온다.

## 1. 외부 구역에서 내려받기

인터넷이 되는 반출입 전용 PC 에서 GGUF 파일과 배포처의 공식 해시를 받는다.

```
sha256sum <모델>.gguf > <모델>.gguf.sha256
```

## 2. 승인과 매체 이동

- 보안팀 반입 승인 번호를 기록한다.
- 승인된 매체로만 옮긴다.
- 해시 파일을 가중치와 같은 매체에 함께 담는다.

## 3. 폐쇄망에서 검증

```
scripts/verify_model.sh <모델>.gguf <기대 sha256>
```

불일치하면 폐기한다. 재시도하지 않는다.

## 4. 런타임에 등록

```
docker compose cp <모델>.gguf runtime:/tmp/model.gguf
docker compose exec runtime sh -c \
  'printf "FROM /tmp/model.gguf\n" > /tmp/Modelfile && ollama create gemma3:12b -f /tmp/Modelfile'
docker compose exec runtime rm -f /tmp/model.gguf /tmp/Modelfile
```

## 5. 기록

`docs/OPERATIONS.md` 의 반입 대장에 모델명, 해시, 승인 번호, 반입 일자를 남긴다.

## 모델 태그에 관해

`ONPREM_CHAT_MODEL` 은 설정 값이다. 세대가 올라가면 이 값 한 줄만 바꾼다.
코드에는 특정 세대에 의존하는 분기를 두지 않는다.

## 내부 PC 기준 모델 크기 선택

| 가용 VRAM/RAM | 권장 양자화 | 비고 |
| --- | --- | --- |
| 8GB 미만 | 4B q4_K_M | 요약·분류 위주 |
| 8~16GB | 12B q4_K_M | 일반 문서 질의응답 |
| 16~24GB | 12B q8_0 또는 27B q4_K_M | 장문 근거 처리 |
| 24GB 초과 | 27B q4_K_M 이상 | 다중 사용자 |

임베딩 모델은 별도로 상주한다. 채팅 모델 크기를 정할 때 1~2GB 를 남겨 둔다.
