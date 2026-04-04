---
name: akbun-writing
description: "Write technical blog posts in akbun's distinctive Korean writing style. Use this skill whenever the user mentions 'akbun style', 'akbun 스타일', '악분 스타일', 'writing like akbun', '악분처럼 글쓰기', or asks to write a blog post, technical article, or study notes in akbun's voice. Also trigger when the user says '내 스타일대로 써줘', '내 블로그 스타일로', or references akbun's blog. Trigger on any request that combines technical writing with akbun's name or style reference."
---

# akbun 스타일 글쓰기

akbun 스타일 글쓰기는 모든 문서가 "3개월 후의 내가 다시 봤을 때 이해할 수 있는가?"를 기준으로 쓴다.

- 내 말로 쓰여 있다 — 공식 문서 문체가 아니라, 내가 이해한 방식으로 설명한다
- "왜"가 먼저 나온다 — 동기 없는 지식은 3개월 후에 의미를 잃는다
- 재현할 수 있다 — 핸즈온 코드가 있으면 동작해야 한다
- 삽질 과정이 있으면 보너스 — 뭘 시도했고, 뭐가 안 됐고, 어떻게 해결했는지
- 나쁜 문서: 공식 문서를 번역하듯 옮겨놓은 것, "~할 수 있다"로 끝나는 기능 나열, 코드만 있고 설명이 없는 것

## 목소리와 톤

- akbun 스타일 글쓰기는 실무자의 목소리로, 격식체보다는 대화체에 가깝다.
- akbun은 akbun자신이 이해하는 글을 쓰려고 노력하고 이 이유때문에 남이 이해하기 쉬운 글로 보인다.
- 핵심 문장 1~2개에만 굵은 글씨를 사용해 강조한다. 긴 복합 문장은 짧게 나눈다.
- 불필요한 내용과 과도한 인사말을 제거한다.
- 실습자료는 "저의 github", "저의 유투브" 같은 1인칭 표현을 사용한다.

## 한국어·영어 사용 기준

- 본문은 전부 한국어로 작성한다. 기술 용어, 서비스명, 약어, 코드, 명령어, URL은 영어를 사용한다.
- 이미 굳어진 영어 기술 용어는 영어 그대로 표기한다. 예: TCP, IPsec, eBPF, IKE, AMI, nvidia-smi, k6, LM studio, obsidian
- 약어가 처음 나올때는 영어 약어(Full English Name)을 사용한다. 예: mTLS(mutual TLS), SNI(Server Name Indication), VPN(Virtual Private Network)

## 포맷

- H1 > H2 > H3 계층 구조를 일관되게 사용한다
- 순서가 있는 단계나 순위 항목에는 번호 목록을 사용한다
- 순서 없는 항목에는 bullet 목록을 사용한다
- 비교에는 표를 사용한다
- 굵은 글씨는 섹션당 핵심 문장 1~2개에만 사용한다
- 짧은 문단: 문단을 1~3 문장으로 유지한다

## 콘텐츠 생태계

akbun 블로그는 더 넓은 생태계의 일부다:

- **실습 코드**: "실습자료는 저의 github에 있습니다" + GitHub 링크
- **YouTube**: "실습과정은 저의 유투브에 자세히 다룹니다" + YouTube 링크
- **이전 글**: "이전 글에서 설명한 것처럼..." + 블로그 링크
- **블로그 URL**: malwareanalysis.tistory.com

## 참고 파일

- **`references/writing-techniques.md`** — 구체적인 글쓰기 기법이 필요할 때 읽는다: 분해 설명, 정의 먼저, 질문형 헤더, 비유, 코드 블록, 아키텍처 다이어그램, mermaid 다이어그램, 문장 패턴
