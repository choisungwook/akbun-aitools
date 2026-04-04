---
name: blog-post-template
description: "기술 블로그 포스트의 문서틀(목차, 공부 배경, 결론, 참고자료 등)을 생성한다. 글의 구조와 섹션 순서를 정의하는 템플릿 스킬. Trigger on: '문서틀', '블로그 템플릿', '글 구조', 'post template', 'blog template', '목차 만들어줘', '글 틀 잡아줘', or any request to create a blog post structure or template."
---

# Blog Post Template

기술 블로그 포스트의 문서 구조를 정의하는 스킬. 글의 섹션 순서, 필수/선택 섹션, post type별 템플릿을 제공한다.

## Common Structure Rules

모든 포스트는 type에 관계없이 아래 순서를 따른다. 글 앞부분 순서가 중요하다:

1. **## 목차** — always first. 각 섹션 헤더로 앵커 링크(`[섹션명](#헤더)`)를 걸어 클릭하면 해당 섹션으로 이동할 수 있게 한다.
2. **## 해결하려는 문제** (또는 **## 공부 배경**) — 이 글을 쓰게 된 동기. 어떤 문제를 해결하려는지, 또는 어떤 주제를 공부하려는지 짧게 설명한다. 독자가 "이 글이 나한테 필요한 글인가?"를 바로 판단할 수 있게 해준다.
3. **## 이 글을 읽고 답할 수 있는 질문** — 글의 핵심 내용을 질문 형태로 3~5개 뽑아 나열한다. 독자가 글을 읽기 전에 기대치를 잡거나, 읽은 후 자기 점검에 활용할 수 있다. 제목은 글 내용에 맞게 자연스럽게 조정한다.
4. **## 결론** — 글에서 얻은 핵심 교훈이나 인사이트를 1~3문장으로 정리한다. 형식적인 마무리가 아니라, 실제 경험에서 느낀 구체적인 깨달음을 담는다. 참고자료 바로 앞에 위치.
5. **## 더 공부할 것** (optional) — forward-looking topics to explore.
6. **## 부록** (optional) — for deep dives: architecture internals, debugging tips.
7. **## 참고자료** — always last. Bulleted URL list.

## Post Types

Read `references/post-types.md` for the 5 post type templates:

- Type 1: Concept Explanation (개념 설명)
- Type 2: Incident / Troubleshooting Story (트러블슈팅 이야기)
- Type 3: Tool / How-To Guide (도구 사용법)
- Type 4: Discussion / Decision Story (토론/의사결정)
- Type 5: Career Reflection (커리어 회고)

## Reference Files

- **`references/post-types.md`** — 5가지 post type별 상세 구조 템플릿
