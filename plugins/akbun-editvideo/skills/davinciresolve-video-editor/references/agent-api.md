# 전용 영상 편집기에 필요한 Agent API

`davinciresolve-video-editor`와 하위 skill이 기대하는 조작 단위를 인터페이스로 적어 둔 것이다. 현재 DaVinci Resolve 스크립팅 API가 제공하는 것과 제공하지 않는 것을 구분하고, 없는 기능은 무엇으로 대신하는지 정한다.

## 인터페이스

각 skill의 절차를 이 인터페이스의 호출로 옮길 수 있어야 한다. 실제 구현 수단(스크립팅 API, 화면 조작, 사람 절차)은 `davinciresolve-video-editor`의 실행 환경 확인 결과에 따른다.

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

## 현재 Resolve 스크립팅 API에 없는 기능과 대체 방법

아래 기능이 있으면 Agent가 화면 좌표를 클릭하는 방식보다 정확하고 안전하게 편집할 수 있다. 지금은 없으므로 대체 방법으로 판정하고, 대체로도 판정할 수 없으면 검토 마커를 찍고 `확인 필요`로 남긴다.

| 부족한 기능 | 인터페이스 | 대체 방법 | 대체의 한계 |
|---|---|---|---|
| 프레임별 초점·노출 이상 탐지 | `media.detectBadFrames` | 클립 시작·중간·끝과 앞 2초를 0.5초 간격으로 프레임 추출(`ffmpeg`)해 밝기 평균·라플라시안 분산으로 흰 화면·초점 이탈 후보를 계산 | 프레임 샘플 사이의 짧은 이상은 놓칠 수 있음. 컷 위치는 사람이 마커에서 확인 |
| 스코프의 수치화된 결과 | `scopes.analyze`, `scopes.compare` | 추출한 프레임에서 휘도 히스토그램·RGB 채널 평균·상하위 1% 값을 계산해 Waveform·Parade 대신 사용 | Resolve 내부 색공간 변환 뒤 값과 다를 수 있음. 최종 판정은 Resolve 스코프 화면으로 확인 |
| 얼굴 범위 검증 | `privacy.detectFaces`, `privacy.validateCoverage` | 추출 프레임에 얼굴 탐지를 돌려 좌표를 얻고 Power Window 좌표와 겹치는지 계산 | 트래킹 중간 프레임은 검증하지 못함. 시작·중간·끝 3점만 보장 |
| 색보정 전후 프리뷰 | `color.getBeforeAfterFrame` | 노드 bypass 전후로 같은 프레임을 스틸로 저장(Gallery Still 또는 화면 캡처)해 나란히 비교 | 스틸 저장은 Color 페이지 화면 조작이 필요 |
| 전체 작업의 트랜잭션 롤백 | `review.beginTransaction`, `review.rollbackTransaction` | 단계 시작 전 작업 타임라인을 한 번 더 복제해 `<작업 타임라인>_before_<단계>`로 두고, 실패하면 그 복제본으로 돌아감 | 타임라인 수가 늘어남. 단계 완료 뒤 사용자 확인을 받고 복제본을 지움 |

스크립팅 API가 제공하는 것은 그대로 쓴다. 타임라인 복제·클립 목록·마커·메타데이터·렌더 설정·렌더 실행은 API로 하고, 화면 조작은 Color 페이지 노드·Power Window·Fusion Text+ 설정처럼 API가 노출하지 않는 곳에만 쓴다.
