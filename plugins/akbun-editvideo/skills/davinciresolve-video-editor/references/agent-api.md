# 전용 영상 편집기에 필요한 Agent API

`davinciresolve-video-editor`와 하위 skill이 기대하는 조작 단위를 인터페이스로 적어 둔 것이다. 현재 DaVinci Resolve 스크립팅 API가 제공하는 것과 제공하지 않는 것을 구분하고, 없는 기능은 무엇으로 대신하는지 정한다.

## 인터페이스

각 skill의 절차를 이 인터페이스의 호출로 옮길 수 있어야 한다. 실제 구현 수단(스크립팅 API, 화면 조작, 사람 절차)은 `davinciresolve-video-editor`의 실행 환경 확인 결과와 아래 대응표에 따른다.

```typescript
interface VideoEditorAgentAPI {
  project: {
    getProject(): Project;
    saveProject(): void;
    createSnapshot(name: string): SnapshotId;
    restoreSnapshot(id: SnapshotId): void;
  };

  timeline: {
    listTimelines(): Timeline[];
    duplicateTimeline(id: TimelineId, name: string): TimelineId;
    createTimeline(name: string, settings: TimelineSettings): TimelineId;
    getItems(id: TimelineId): TimelineItem[];
    sortByCaptureTime(items: TimelineItemId[]): void;
    trim(item: TimelineItemId, range: TimeRange): void;
    deleteItems(items: TimelineItemId[]): void;
    addMarker(time: Timecode, marker: Marker): MarkerId;
  };

  media: {
    getMetadata(mediaId: MediaId): {
      fileName: string;
      captureTime?: string;
      camera?: string;
      lens?: string;
      colorSpace?: string;
      gamma?: string;
      resolution: Size;
      frameRate: number;
    };
    extractFrames(
      item: TimelineItemId,
      positions: Array<"start" | "middle" | "end" | number>
    ): ImageFrame[];
    detectBadFrames(item: TimelineItemId): {
      overexposed: TimeRange[];
      underexposed: TimeRange[];
      outOfFocus: TimeRange[];
      shaky: TimeRange[];
      blackFrames: TimeRange[];
    };
  };

  scopes: {
    analyze(item: TimelineItemId, range?: TimeRange): {
      waveform: ScopeStatistics;
      rgbParade: RGBStatistics;
      vectorscope: VectorscopeStatistics;
      clipping: {
        shadows: number;
        highlights: number;
      };
      estimatedWhiteBalance: {
        temperature: number;
        tint: number;
        confidence: number;
      };
    };
    compare(items: TimelineItemId[]): ClipConsistencyReport;
  };

  color: {
    listNodes(item: TimelineItemId): ColorNode[];
    addSerialNode(item: TimelineItemId, name: string): NodeId;
    setNodeOrder(item: TimelineItemId, nodes: NodeId[]): void;
    setExposure(node: NodeId, adjustment: {
      lift?: number;
      gamma?: number;
      gain?: number;
      offset?: number;
    }): void;
    setWhiteBalance(node: NodeId, temperature: number, tint: number): void;
    applyLUT(node: NodeId, lutId: string): void;
    copyGrade(source: TimelineItemId, targets: TimelineItemId[]): void;
    bypassNode(node: NodeId, bypass: boolean): void;
    getBeforeAfterFrame(item: TimelineItemId): {
      before: ImageFrame;
      after: ImageFrame;
    };
  };

  privacy: {
    detectFaces(item: TimelineItemId): FaceTrack[];
    createPowerWindow(node: NodeId, shape: WindowShape): WindowId;
    setWindowSoftness(window: WindowId, value: number): void;
    applyMosaic(node: NodeId, settings: MosaicSettings): void;
    validateCoverage(window: WindowId, face: FaceTrack): CoverageReport;
  };

  stabilization: {
    analyze(item: TimelineItemId): {
      shakeScore: number;
      recommended: boolean;
      expectedCrop: number;
    };
    apply(item: TimelineItemId, settings: StabilizationSettings): void;
    preview(item: TimelineItemId): StabilizationPreview;
  };

  titles: {
    addText(text: string, range: TimeRange): TitleId;
    setFont(title: TitleId, family: "Gmarket Sans", weight: string): void;
    setSafeArea(title: TitleId, safeArea: SafeArea): void;
    retimeTitlesAfterEdit(changes: TimelineChange[]): void;
  };

  audio: {
    analyzeLoudness(item: TimelineItemId): LoudnessReport;
    createTrack(type: "location" | "ambience" | "sfx" | "music"): TrackId;
    setGain(item: AudioItemId, db: number): void;
    addCrossfade(item: AudioItemId, duration: number): void;
    duckMusic(musicTrack: TrackId, referenceTracks: TrackId[]): void;
  };

  review: {
    beginTransaction(name: string): TransactionId;
    previewTransaction(id: TransactionId): ChangeReport;
    commitTransaction(id: TransactionId): void;
    rollbackTransaction(id: TransactionId): void;
    addReviewMarker(item: TimelineItemId, reason: string, severity: MarkerColor): void;
    exportEditDecisionList(): EditDecision[];
  };

  render: {
    validateTimeline(id: TimelineId): ValidationReport;
    render(id: TimelineId, preset: "youtube-4k"): RenderJobId;
    getJobStatus(job: RenderJobId): RenderStatus;
    inspectOutput(path: string): MediaInspection;
  };
}
```

## 인터페이스와 Resolve 스크립팅 API 대응표

"있음"은 외부 스크립팅 API 함수로 바로 할 수 있는 것, "화면"은 API가 없어 화면 조작이나 사람 절차가 필요한 것이다. 버전은 Resolve 릴리스 기준이고, 사용 중인 버전이 낮으면 "화면"으로 본다.

| 인터페이스 | 상태 | Resolve API 함수 / 대체 |
|---|---|---|
| `project.getProject`, `saveProject` | 있음 | `ProjectManager.GetCurrentProject`, `SaveProject` |
| `project.createSnapshot`, `restoreSnapshot` | 화면 | 타임라인 복제로 대신(아래 "없는 기능" 표) |
| `timeline.listTimelines`, `createTimeline` | 있음 | `Project.GetTimelineByIndex`, `MediaPool.CreateEmptyTimeline`, `CreateTimelineFromClips` |
| `timeline.duplicateTimeline` | 있음(19 이상) | `Timeline.DuplicateTimeline(name)`. 18 이하는 화면에서 Duplicate Timeline |
| `timeline.getItems` | 있음 | `Timeline.GetItemListInTrack("video", n)` |
| `timeline.sortByCaptureTime` | 화면 | 클립 이동 함수 없음. `CreateTimelineFromClips`로 시간순 새 타임라인 생성 |
| `timeline.trim`, `deleteItems` | 화면 | 트림·삭제 API 없음. 화면 조작하거나 `CreateTimelineFromClips`에 `startFrame`·`endFrame`을 준 클립 정보로 새 타임라인 구성 |
| `timeline.addMarker` | 있음 | `Timeline.AddMarker(frameId, color, name, note, duration)`, 클립 마커는 `TimelineItem.AddMarker` |
| `media.getMetadata` | 있음 | `MediaPoolItem.GetMetadata`, `GetClipProperty`(촬영 시간은 `Date Recorded`, 색공간은 `Input Color Space`) |
| `media.extractFrames` | 화면 | 미디어 파일에서 `ffmpeg`로 추출(원본 프레임). 그레이드 뒤 프레임은 Gallery still 내보내기 |
| `media.detectBadFrames` | 없음 | 아래 "없는 기능" 표 |
| `scopes.*` | 없음 | 아래 "없는 기능" 표 |
| `color.listNodes`, `addSerialNode`, `setNodeOrder`, `setExposure`, `setWhiteBalance` | 화면 | 노드 편집 API 없음. `TimelineItem.SetLUT(nodeIndex, path)`만 있음 |
| `color.applyLUT` | 있음 | `TimelineItem.SetLUT(nodeIndex, lutPath)` |
| `color.copyGrade` | 있음 | `Timeline.ApplyGradeFromDRX` 또는 `TimelineItem.CopyGrades(targets)`(19 이상) |
| `color.bypassNode`, `getBeforeAfterFrame` | 화면 | 노드 bypass 전후 Gallery still |
| `privacy.detectFaces`, `validateCoverage` | 없음 | 아래 "없는 기능" 표 |
| `privacy.createPowerWindow`, `setWindowSoftness`, `applyMosaic` | 화면 | Color 페이지 Window·OpenFX 패널 |
| `stabilization.apply` | 있음(파라미터 없음) | `TimelineItem.Stabilize()`는 현재 Inspector 값으로 실행. Mode·Cropping Ratio·Smooth는 화면 |
| `stabilization.analyze`, `preview` | 없음 | 아래 "없는 기능" 표 |
| `titles.addText`, `setFont` | 있음 | `Timeline.InsertFusionTitleIntoTimeline("Text+")` 뒤 `TimelineItem.GetFusionCompByIndex(1)`로 Text+ 툴의 `StyledText`, `Font`, `Style`, `Size` 입력 설정 |
| `titles.setSafeArea` | 화면 | Text+ `Center`·레이아웃 값을 Fusion 툴 입력으로 설정하고 스틸로 확인 |
| `titles.retimeTitlesAfterEdit` | 화면 | 자막 클립 이동 API 없음. 새 위치에 다시 삽입하고 옛 것을 삭제 |
| `audio.analyzeLoudness` | 화면 | Fairlight 라우드니스 미터 또는 렌더 파일에 `ffmpeg -af ebur128` |
| `audio.createTrack`, `setGain`, `addCrossfade`, `duckMusic` | 화면 | `Timeline.AddTrack("audio")`만 있음(18.5 이상). 게인·페이드·덕킹은 Fairlight 화면 |
| `review.*Transaction` | 없음 | 아래 "없는 기능" 표 |
| `review.addReviewMarker` | 있음 | `TimelineItem.AddMarker` |
| `review.exportEditDecisionList` | 있음 | `Timeline.Export(path, EXPORT_EDL)` |
| `render.render`, `getJobStatus` | 있음 | `Project.SetRenderSettings`, `AddRenderJob`, `StartRendering`, `GetRenderJobStatus`. 코덱 목록은 `GetRenderFormats`, `GetRenderCodecs` |
| `render.validateTimeline`, `inspectOutput` | 화면 | 렌더 파일에 `ffprobe` |

## 현재 Resolve 스크립팅 API에 없는 기능과 대체 방법

아래 기능이 있으면 Agent가 화면 좌표를 클릭하는 방식보다 정확하고 안전하게 편집할 수 있다. 지금은 없으므로 대체 방법으로 판정하고, 대체로도 판정할 수 없으면 마커를 찍고 `확인 필요`로 남긴다.

| 부족한 기능 | 인터페이스 | 대체 방법 | 대체의 한계 |
|---|---|---|---|
| 프레임별 초점·노출 이상 탐지 | `media.detectBadFrames` | 클립 앞 5초를 0.25초 간격, 나머지는 시작·중간·끝으로 `ffmpeg`로 프레임 추출해 밝기 평균(8비트 0~255)과 라플라시안 분산으로 흰 화면·초점 이탈 후보를 계산 | 샘플 사이의 짧은 이상은 놓칠 수 있음. 컷 위치는 사람이 마커에서 확인 |
| 스코프의 수치화된 결과 | `scopes.analyze`, `scopes.compare` | 원본 프레임은 `ffmpeg` 추출, 그레이드 뒤 프레임은 Gallery still(또는 화면 캡처)로 얻어 휘도 히스토그램·RGB 채널 평균·상하위 1% 값을 계산. 8비트 값에 4를 곱해 10비트 스코프 스케일로 적는다 | Resolve 내부 색공간 변환 뒤 값과 다를 수 있음. 최종 판정은 Resolve 스코프 화면으로 확인 |
| 얼굴 범위 검증 | `privacy.detectFaces`, `privacy.validateCoverage` | 추출 프레임을 축소하지 않고 원본 해상도로 OpenCV YuNet(`cv2.FaceDetectorYN`) 같은 탐지기에 넣어 좌표를 얻고 Power Window 좌표와 겹치는지 계산 | 트래킹 중간 프레임은 검증하지 못함. 샘플 프레임만 보장. 탐지기가 없으면 전 클립 `PRIVACY_CHECK` |
| 색보정 전후 프리뷰 | `color.getBeforeAfterFrame` | 노드 bypass 전후로 같은 프레임을 Gallery still로 저장해 나란히 비교 | 스틸 저장은 Color 페이지 화면 조작이 필요 |
| 안정화 분석·프리뷰 | `stabilization.analyze`, `preview` | 추출 프레임 사이 광학 흐름(`cv2.calcOpticalFlowFarneback`)의 평균 이동량 표준편차로 흔들림 점수를 내고, 적용 전후 스틸에서 같은 물체의 폭 비율로 크롭을 산출 | Resolve는 크롭 비율을 표시하지 않음. 스틸 비교값이 유일한 근거 |
| 전체 작업의 트랜잭션 롤백 | `review.beginTransaction`, `review.rollbackTransaction` | 단계 시작 전 작업 타임라인을 한 번 더 복제해 `<작업 타임라인>_before_<단계>`로 두고, 실패하면 그 복제본으로 돌아감 | 타임라인 수가 늘어남. 단계 완료 뒤 사용자 확인을 받고 복제본을 지움 |

스크립팅 API가 제공하는 것은 그대로 쓴다. 화면 조작은 대응표에서 "화면"인 항목에만 쓴다.
