# YouTube Output Is Transcript Grounded

YouTube transcript skill의 산출물은 짧은 영상 요약이 아니라, 자막에 근거해 화자의 말을 한국어 독자가 따라갈 수 있게 풀어쓴 walkthrough이다. 자동 자막은 중복과 karaoke tag가 많으므로 cleaned transcript를 기본 입력으로 사용하고, 원본 VTT는 fallback으로만 본다.
