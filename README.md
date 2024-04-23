# Misskey Ace Court
Misskey에서 역전재판을 렌더링하기

Try now : [@court@hoto.moe](https://hoto.moe/@court)

**@objection@hoto.moe**와는 관련 없는 프로젝트입니다!

## 구동 확인된 환경
* AMD64 환경에서 동작하는 Ubuntu (Python 3.12)
* objection-engine 패키지의 한계로 이외 환경에서 동작을 보증하지 않습니다.

## 설정해야 하는 값
* config.json
```json
{
    "token": "API Token",
    "origin": "wss://example.com/streaming"
}
```

* banlist.txt
```
# 금지할 단어를 줄바꿈으로 구분해서 작성
코코아
무라쿠모
슈플
라온
.
.
.
```