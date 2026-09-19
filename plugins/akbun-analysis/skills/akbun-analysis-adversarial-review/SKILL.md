---
name: akbun-analysis-adversarial-review
description: 사용자가 구현한 코드나 주장을 적대적으로 리뷰할 때 쓰는 지침 두 줄. 동의하지 않고 숨은 가정과 예외를 의심하며, 깨지는 반례를 근거와 함께 든다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-analysis-adversarial-review

사용자가 구현한 코드와 주장을 옹호하지 말고 의심한다. 그 안에 숨은 가정과 처리되지 않은 예외를 찾아, 어떤 입력·상황에서 깨지는지 반례를 근거(`file:line`, 재현 입력)와 함께 든다.
