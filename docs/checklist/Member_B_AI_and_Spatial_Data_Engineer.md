# 📋 [Member B] AI & Spatial Data Engineer — AI Pair Programming 체크리스트

## 1. 역할 개요 및 미션
- **역할 (Role)**: AI & Spatial Data Engineer
- **핵심 목표**: Gemini 차세대 멀티모달 비전 모델 체인(3.5 Flash-Lite ➔ 3.1 Flash-Lite ➔ 3.6 Flash)을 통한 공원 종합안내판 판독 및 현장 위험 장애물 진단, DEM 고도 래스터 파이프라인, SunCalc 태양 궤적 그늘 분석, n8n 기상청 지면열 수지식 연산, 커뮤니티 출발지 200m 공간 지터링(Spatial Jittering) 파이프라인 구축을 전담한다.
- **배정 공수 및 스토리**: 총 **71 Hours (14개 Task)** | **US-B1, US-B2, US-B3, US-D1, US-D2, US-F1, US-G1, US-G2**

---

## 2. AI Pair Programming 기본 원칙 & 프롬프팅 가이드

### 2.1 Gemini 멀티모달 프롬프팅 가이드라인
- **Gemini 1.5 계열 차단 및 Fallback Chain 준수**: AI와 협업하여 비전 호출 코드를 작성할 때, 구형 `gemini-1.5-flash`를 하드코딩하지 않고, `GeminiModelSelector`를 통해 `gemini-3.5-flash-lite` ➔ `gemini-3.1-flash-lite` ➔ `gemini-3.6-flash` 순으로 가용 모델을 자동 바인딩하도록 강제한다.
- **Pydantic V2 Structured JSON 강제**: LLM 비전 응답에 반드시 `response_schema` 또는 `response_mime_type="application/json"`을 지정하여 `ParkBoardInspectionResult`, `HazardInspectionResult` 스키마와 완벽 일치하도록 유도한다.
- **실시간 비디오 촬영 유도 금지**: 산책 중 리드줄을 쥔 상태에서 스마트폰을 들고 바닥을 지속 촬영하는 기능은 안전상 금지하며, **단발성 사진 제보** 및 **공원 입구 안내판 정적 촬영**으로 범위를 제한한다.

---

## 3. 단계별 AI Pair Programming 체크리스트

### 1단계: 작업 착수 전 준비 (Pre-Coding)
- [ ] **스토리 및 인수 조건(AC) 재확인**: `docs/03_PawTrail_Agile_User_Stories.md`의 US-D1, US-D2, US-B1~B3, US-F1, US-G1~G2 확인.
- [ ] **테스트 스위트 참조**: `test_case/test_vision_safety_inspector.py`, `test_case/test_thermal_and_parking.py` 실행 환경 및 DTO 확인.
- [ ] **외부 데이터 소스 규격 점검**: DEM GeoTIFF 래스터 형식, SunCalc 계산식, 기상청 단기예보 격자 좌표계, 공영주차장 API 스키마 확인.

### 2단계: AI 코드 생성 및 페어링 (During Coding)
- [ ] **Gemini 모델 선택기 및 비전 분석 파이프라인 (TASK-D1-1, D1-2)**:
  - [ ] `gemini-1.5` 계열 호출 시 즉시 `DeprecatedModelError`가 발생하는가?
  - [ ] 1순위(`3.5 Flash-Lite`) 비가용 시 2순위(`3.1 Flash-Lite`), 3순위(`3.6 Flash`)로 무중단 순차 폴백이 작동하는가?
  - [ ] 비전 분석 결과의 신뢰도(Confidence)가 0.85 이상일 때만 자동 라우팅 제약으로 주입하고, 미달 시 사용자 재촬영 가이드(`TASK-D1-3`)를 반환하는가?
- [ ] **공원 종합안내판 판독기 (ParkBoardInspector) (TASK-D1-4)**:
  - [ ] 흙길 산책로(`has_dirt_trail`) 및 반려견 출입 금지 구역(`dog_restricted_zones`)을 정확히 분리 파싱하는가?
  - [ ] 이미지 리사이징(최대 1024px) 전처리를 거쳐 API 응답 지연을 2.5초 이내로 단축하는가?
- [ ] **DEM 고도 샘플링 및 경사도 파이프라인 (TASK-B2-1, B2-4)**:
  - [ ] GeoTIFF 고도 래스터에서 보행 링크 좌표별 표고차($\Delta h$) 및 거리($L$)를 통해 종단 경사도(`slope_percent = \Delta h / L \times 100`)가 정확히 연산되는가?
  - [ ] 급경사(>8%) 구간에 대한 페널티 가중치가 라우터 엔진으로 투명하게 전달되는가?
- [ ] **SunCalc 태양 궤적 및 그림자 차폐 모델링 (TASK-B3-1, B3-4)**:
  - [ ] 산책 시작 시각 및 위경도 기준 태양 고도각(Altitude)과 방위각(Azimuth)이 정확히 산출되는가?
  - [ ] 11~15시 직사광선 피크 시간대에 그늘 비율이 높은 링크에 비용 할인 가중치($W_{\text{shade}} = 0.6$)가 부여되는가?
- [ ] **기상청 지면열 수지식 및 주차장/마스킹 (TASK-F1-1, F1-2, G1-1, G2-2)**:
  - [ ] 지면열 수지식($\text{Surface Temp} = \text{Air Temp} + \text{Insolation Weight} \times 15$) 연산이 기상청 API 파싱 데이터와 올바르게 결합하는가?
  - [ ] 커뮤니티 코스 공유 시 **출발지/도착지 반경 200m 공간 절단 및 지터링(Spatial Jittering)**이 누락 없이 강제 적용되는가?
- [ ] **클린코드 가드레일 준수**:
  - [ ] 단일 파일 250줄 이하, 함수 40줄 이하, 인지 복잡도 10 이하를 준수하는가?
  - [ ] 데이터 변환 및 공간 연산 함수에 철저한 방어 코드와 예외 처리가 적용되었는가?

### 3단계: 단위 테스트 및 검증 (Testing & Verification)
- [ ] **TDD 테스트 스위트 실행**:
  ```bash
  python -m pytest test_case/test_vision_safety_inspector.py -v
  python -m pytest test_case/test_thermal_and_parking.py -v
  ```
- [ ] **모델 Fallback 동작 검증**: 모의 장애 상황에서 `3.5 Flash-Lite` ➔ `3.1 Flash-Lite` ➔ `3.6 Flash` 순차 전환이 정상 동작하는가?
- [ ] **200m 공간 지터링 검증**: 원본 좌표와 마스킹된 좌표 간 유클리드 거리가 최소 200m 이상 이격되는가?

### 4단계: 산출물 동기화 및 형상 관리 (Post-Coding & Review)
- [ ] **문서 정합성 확인**: 비전 DTO 및 GIS 파이프라인 수정 시 `docs/04_PawTrail_Architecture_Design.md` 및 `06_PawTrail_Task_Breakdown_and_Estimations.md` 즉시 동기화.
- [ ] **민감정보 누출 방지**: 테스트 이미지 및 제보 사진 내 사람 얼굴, 자동차 번호판 블러링 처리 가이드라인 준수.

---

## 4. 핵심 안티패턴 (주의해야 할 금기사항)
1. ❌ **구형 Gemini 1.5 모델 하드코딩 금지**: `gemini-1.5-flash`를 코드나 설정에 재도입하지 말 것.
2. ❌ **원시 위성영상 CV 세그멘테이션 금지**: 실현 불가능한 원시 항공/위성 영상 딥러닝 대신 검증된 GIS 데이터(OSM, DEM, 건물 폴리곤)를 활용할 것.
3. ❌ **원점(0, 0) 좌표 노출 금지**: 200m 공간 지터링 파이프라인에서 예외 발생 시 원본 자택 좌표가 그대로 커뮤니티에 공개되지 않도록 Fallback 예외 차단할 것.
