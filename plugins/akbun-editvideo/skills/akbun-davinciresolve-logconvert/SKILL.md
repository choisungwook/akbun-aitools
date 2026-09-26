---
name: akbun-davinciresolve-logconvert
description: DaVinci Resolve 21.1 스크립팅 API로 클립마다 Log 촬영 여부를 근거 기준으로 `Log`·`비Log`·`미확인`으로 판정하고, `Log`로 확인된 클립에만 Color 페이지의 새 `CST` 라벨 노드에 Log → Rec.709 변환 LUT를 건다(`Graph.SetLUT`). iPhone Apple Log/Apple Log 2, Insta360 I-Log 대상. BT.709 태그와 화면 외관은 근거로 쓰지 않는다. "Log 변환해줘", "LUT 걸어줘", "이 클립 Log야?" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-logconvert

Log로 찍은 클립만 골라 Rec.709로 변환한다. 변환은 Log로 **확인된** 클립에만 하고, 확인 못 한 클립은 건드리지 않는다. 실행 수단은 [`scripts/logconvert.py`](scripts/logconvert.py)다. 측정·세션·노드 규칙은 `akbun-davinciresolve-exposure`의 `exposure_scope.py`를 가져다 쓴다.

색 작업 순서에서 이 skill은 `EXPOSURE`·`WB`(변환 앞) 다음, `CONTRAST`·`SAT`·`SKY`(변환 뒤) 앞이다.

## Log 판정 규칙

| 우선순위 | 근거 | 판정 |
|---|---|---|
| 1 | 사용자 지정 `--profile 접두어=프로파일` (예: `VID_=Insta360 I-Log`) | `Log` |
| 2 | Resolve 클립 속성 `Input Color Space` 또는 `Input Gamma`에 `log` (예: `Apple Log 2`, `Apple Log`) | `Log` |
| 3 | `ffprobe` 스트림 `color_transfer`에 `log` | `Log` |
| 4 | `ffprobe` `pix_fmt`가 8비트(예: `yuv420p`). Apple Log·I-Log는 10비트 | `비Log` |
| 그 밖 | 근거 없음 | `미확인` |

- `BT.709` 색공간 태그는 근거로 쓰지 않는다. Insta360 I-Log 파일도 `bt709`로 기록된다(실측: `VID_*.mp4`는 `color_transfer=bt709`, `pix_fmt=yuv420p10le`). 그래서 Insta360은 메타데이터만으로는 `미확인`이고, 촬영자가 Log 모드로 찍었다고 알려주면 `--profile VID_=Insta360 I-Log`로 지정한다.
- 화면이 평평하거나 채도가 낮다는 외관으로 판정하지 않는다.
- iPhone 기본 카메라 앱 클립은 8비트 H.264라 `비Log`, Blackmagic Cam·Final Cut Camera의 Apple Log 클립은 Resolve가 `Apple Log 2`로 읽어 `Log`다.
- `exiftool`이 있으면 `Color Mode`·`Picture Profile` 태그도 볼 수 있지만 이 스크립트는 쓰지 않는다. 필요하면 그 값을 `--profile`로 옮긴다.

## 노드 규칙

Color 페이지에서 새 노드를 만들고 라벨 `CST`(또는 `LUT`, `03_CST`)를 단다. 스크립트는 라벨에 `cst`나 `lut`가 들어간 노드만 쓴다. 절차는 `akbun-davinciresolve-exposure`의 노드 규칙과 같다.

- 클립의 다른 노드에 이미 LUT나 Color Space Transform이 있으면 건너뛰고 "다른 노드에 변환 있음"으로 적는다. 변환을 두 번 걸지 않는다.
- API는 LUT만 걸 수 있다(`Graph.SetLUT`). CST OFX는 API가 없으므로 CST를 원하면 화면에서 넣고 이 skill은 건너뛴다.
- LUT는 프로파일별로 사용자가 지정한다. Resolve LUT 폴더(`/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`) 기준 상대 경로다.

## 실행 순서

1. `--dry-run`으로 클립별 판정과 근거를 본다. `미확인` 클립은 사용자에게 Log 모드로 찍었는지 묻고 `--profile`로 지정받는다.
2. `Log` 클립마다 `CST` 노드를 준비한다.
3. 적용한다. 스크립트가 `SetLUT` 뒤 `GetLUT`로 경로를 확인하고 중앙값이 바뀌었는지 스틸로 확인한다.

dry-run 명령이다.

```bash
python3 scripts/logconvert.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --profile "VID_=Insta360 I-Log" --dry-run
```

적용 명령이다. 프로파일마다 LUT를 준다.

```bash
python3 scripts/logconvert.py --out "<출력 폴더>" --timeline "<작업 타임라인>" \
  --profile "VID_=Insta360 I-Log" \
  --lut "Apple Log 2=Apple Log 2/65x/Eterna_iPh17_ALog2_G4_65x.cube" \
  --lut "I-Log=Luna_Ultra/Luna_I-Log_to_Rec709_BT1886_s65_v2.cube"
```

## 작업 로그

`<출력 폴더>/logconvert_<YYYYMMDD_HHMM>.md`를 작업 로그 `5. LUT` 절에 넣는다.

```markdown
| 파일명 | 시작 TC | 색공간/감마 | 비트 | 판정 | 근거 | 프로파일 | 노드/LUT | 중앙값 전→후 | 결과 |
|---|---|---|---|---|---|---|---|---|---|
| IVDB4951.MOV | 01:00:00:00 | Apple Log 2 / Apple Log | yuv422p10le | Log | Resolve 클립 속성 Input Color Space/Gamma | Apple Log 2 | 노드1 Apple Log 2/65x/Eterna_iPh17_ALog2_G4_65x.cube | 412→308 | 적용 |
| IMG_1829.MOV | 01:02:24:15 | Rec.709 (Scene) / Rec.709 | yuv420p | 비Log | 8비트 소스(yuv420p). Apple Log·I-Log는 10비트 | - | - | - | 변환 안 함(비Log) |
```

## 하지 않는 것

- `미확인`·`비Log` 클립에 변환 LUT 적용
- BT.709 태그·외관으로 Log 판정
- 이미 변환이 있는 클립에 LUT 중복 적용
- 사용자가 지정하지 않은 LUT 선택
