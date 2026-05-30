# AI Context

## 작업 맥락

akbun-learning skills는 한국어 사용자의 영어/일본어 학습과 학습 자료 생성을 돕는 Codex/Claude용 skill 모음이다. YouTube transcript skill은 요약이나 해설이 아니라 자막 발화를 Markdown 대본으로 옮기는 것을 우선한다. Anki 생성 skill은 한국어 초보 학습자가 바로 복습할 수 있도록 일본어 원문, 읽기, 한국어 의미, 음성 경험을 함께 고려한다. 작업 이력은 changelog로 남기지 않고, 다음 agent에게 필요한 용어와 중요한 결정만 이 디렉터리의 context와 결정 기록에 남긴다.

## 용어 정리

- transcript markdown: 유튜브 자막 발화를 시간 순서대로 옮긴 Markdown 대본이다. 기술적 중복과 추임새만 제거하고, 자막에 없는 설명이나 요약은 추가하지 않는다.
- cleaned transcript: 자동 자막의 롤링 중복과 karaoke tag를 정리해 읽기 쉬운 발화 단위로 만든 자막 텍스트이다.
- Korean beginner learner: 일본어 학습에서 히라가나 읽기와 한국어 의미가 함께 필요한 초급 한국어 사용자이다.
