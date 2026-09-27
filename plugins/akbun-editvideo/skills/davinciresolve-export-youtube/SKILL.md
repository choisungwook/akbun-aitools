---
name: davinciresolve-export-youtube
description: DaVinci Resolve 프로젝트를 기본 YouTube 렌더 프리셋으로 출력할 때 사용한다. 프로젝트 해상도에 따라 2160p 또는 1080p 프리셋을 선택한다.
disable-model-invocation: true
---

# davinciresolve-export-youtube

- 프로젝트 설정에서 타임라인 해상도를 확인한다.
- 타임라인이 3840×2160 등 4K이면 기본 `YouTube 2160p` 프리셋을 선택한다.
- 4K가 아니면 기본 `YouTube 1080p` 프리셋을 선택한다.
- 프레임레이트와 출력 범위를 확인하고 렌더한 뒤 결과 해상도를 검사한다.
