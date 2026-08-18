---
name: akbun-make-directorystruture-foragents
description: 프로젝트에 agent용 기억 디렉터리 구조와 AGENTS.md, CLAUDE.md를 만든다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-make-directorystruture-foragents

기억을 많이 저장하는 것보다 **필요한 순간에 올바른 기억을 꺼내주는 것**이 목표다. 그래서 이 skill은 저장소를 늘리는 게 아니라, 현재 상황에 정말 필요한 기억만 우선순위대로 꺼낼 수 있게 디렉터리를 설계한다.

## 할 일

1. 프로젝트를 훑어 어떤 맥락이 반복해서 필요한지 파악하고, 그 기준으로 기억 디렉터리 구조를 만든다. 종류마다 디렉터리를 나누고, 각 디렉터리에 언제 읽어야 하는지를 한 줄로 적는다.
2. `AGENTS.md`를 만든다. 만든 디렉터리를 **읽는 순서와 조건**으로 적어서, agent가 매번 전부 읽지 않고 상황에 맞는 것만 꺼내 쓰도록 지시한다.
3. `CLAUDE.md`는 `AGENTS.md`를 읽고 따르라는 지시만 담는다. 내용을 중복해서 쓰지 않는다.
