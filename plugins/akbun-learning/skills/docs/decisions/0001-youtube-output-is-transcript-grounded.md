# YouTube Output Is Transcript Grounded

YouTube transcript skill의 산출물은 짧은 영상 요약이나 해설이 아니라, 자막 발화를 시간 순서대로 옮긴 Markdown 대본이다. 자동 자막은 중복과 karaoke tag가 많으므로 cleaned transcript를 기본 입력으로 사용하고, 원본 VTT는 fallback으로만 본다.
