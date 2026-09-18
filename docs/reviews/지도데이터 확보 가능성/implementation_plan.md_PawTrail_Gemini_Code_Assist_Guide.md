# PawTrail 아키텍처 리팩토링 및 구현 가이드 반영 계획

`docs/reviews/PawTrail_Gemini_Code_Assist_Guide.md` 및 `docs/reviews/air_view.md`에서 도출된 핵심 아키텍처 개선사항(비전 모델의 실용적 피벗, 환경부 토지피복지도 공간 결합 융합, 시드 데이터셋 구축)을 전 프로젝트 문서에 일관되게 반영합니다.

## User Review Required

> [!IMPORTANT]
> - **멀티모달 Vision AI의 핵심 피벗**:
>   - ❌ **기존**: 산책 중 리드줄을 잡고 발밑 1~2m를 촬영해 실시간 우회로를 재탐색하는 비현실적 UX (폐기)
>   - ⭕ **개선**:
>     1. **사전 진입 시: 공원 종합안내판 비전 판독 (`ParkBoardInspector`)** ➔ 흙길/잔디밭/반려견 출입 제한 구역 파싱 (`POST /api/walks/inspect-board`)
>     2. **완주 후: 커뮤니티 노면 제보 비전 검증 (`CommunityMapEnricher`)** ➔ 완주 후 제보 사진 검증 및 결측 지도 속성 영구 보정 (`POST /api/walks/verify-surface`)
> - **지도 데이터 파이프라인의 공공데이터 융합**:
>   - 원시 위성영상 직접 CV 분석(수관 차폐 및 10m 해상도 한계)을 배제하고, **환경부 토지피복지도(Land Cover Map) 세분류 벡터 데이터셋**을 OSM 도로망과 공간 결합(Spatial Join)하여 0.1초 만에 흙/잔디/포장 비율을 정밀 판정.
>   - 5인 CBT 시범 구역(반경 1.5km)에 대해 네이버/카카오 스카이뷰 육안 검증 시드(Seed) 데이터셋 구축.
> - **스토리 포인트 및 공수 유지**: 16개 스토리(62 pt), 54개 Task(330 h) 구조를 유지하면서 US-03, US-04, US-05의 구현 세부 내용을 현실적이고 고도화된 스펙으로 업그레이드합니다.

---

## Proposed Changes

### 1. [01_PawTrail_Project_Proposal.md](file:///d:/cody/PawTrail/docs/01_PawTrail_Project_Proposal.md)
- **2절 문제 정의 및 해결 방식**:
  - 실시간 현장 위험 해결 방식 ➔ "공원 입구 종합안내판 판독 사전 진입 최적화 & 산책 완주 후 커뮤니티 노면 사진 제보 검증 및 지도 영구 갱신"으로 갱신.
  - 노면 불확실성 ➔ "환경부 토지피복지도 세분류 공간 결합(Spatial Join) 및 시드 데이터 융합".
- **3.1절 아키텍처 다이어그램 & 3.2절 필수 기술 요소**:
  - Vision Inspector 역할에 공원 종합안내판 판독(`ParkBoardInspector`) 및 커뮤니티 제보 검증(`CommunityMapEnricher`) 명시.
  - Routing Engine에 토지피복 공간데이터 연동 명시.
- **4.3절 노면 출처 분류 체계**:
  - `surface_source` 속성 체계 도입: `land_cover_map`, `park_polygon`, `seed_verified`, `community_verified`, `estimated`.

---

### 2. [02_PawTrail_Team_building.md](file:///d:/cody/PawTrail/docs/02_PawTrail_Team_building.md)
- **핵심 요약 및 엔지니어링 전략**:
  - 1번 전략: 위성 영상 직접 CV 세그멘테이션 지양 ➔ 환경부 토지피복지도 벡터 공간 결합 채택.
  - 비전 전략: 산책 중 리드줄 잡고 실시간 촬영 지양 ➔ 공원 입구 종합안내판 판독 & 완주 후 제보 검증 루프 채택.

---

### 3. [03_PawTrail_Agile_User_Stories.md](file:///d:/cody/PawTrail/docs/03_PawTrail_Agile_User_Stories.md)
- **US-03 (코어 라우팅)**:
  - 인수조건에 OSM 보행로 + 환경부 토지피복지도(Land Cover Map) 세분류 Spatial Join 및 시범구역 시드 데이터셋 적용 명시.
- **US-04 (공원 종합안내판 판독)**:
  - *스토리 피벗*: 공원 입구 오프라인 종합안내판 사진 촬영 ➔ 산책로 범례(흙길, 잔디길, 반려견 출입 금지 구역) 판독 및 추천 코스 반영 (`POST /api/walks/inspect-board`).
- **US-05 (완주 후 커뮤니티 노면 제보 검증)**:
  - *스토리 피벗*: 완주 후 견주가 촬영한 노면 사진 제보 ➔ 비전 AI 안전도/재질 검증 ➔ 결측 지도 링크 속성 갱신 (`POST /api/walks/verify-surface`).

---

### 4. [04_PawTrail_Architecture_Design.md](file:///d:/cody/PawTrail/docs/04_PawTrail_Architecture_Design.md)
- **2절 전체 시스템 다이어그램**:
  - 외부 연동 서비스에 `환경부 EGIS: 토지피복지도 세분류 GeoJSON` 추가.
  - Vision 컴포넌트: `ParkBoardInspector` 및 `CommunityMapEnricher`.
- **3.2절 REST API 명세**:
  - `POST /api/walks/inspect-board` (공원 안내판 판독) 추가
  - `POST /api/walks/verify-surface` (커뮤니티 제보 노면 검증) 추가
- **3.3절 비전 파이프라인 & 3.4절 공간 비용 모델**:
  - `ParkBoardInspectionResult`, `SurfaceEnrichmentResult`, `RouteSegmentMetadata` Pydantic DTO 명세.
  - `LandCoverSpatialService` (토지피복 Spatial Join) 클래스 구조 추가.
- **4.2절 시퀀스 다이어그램**:
  - 공원 안내판 판독 및 완주 후 노면 제보 검증 시퀀스로 갱신.

---

### 5. [05_PawTrail_Detailed_Implementation_Plan.md](file:///d:/cody/PawTrail/docs/05_PawTrail_Detailed_Implementation_Plan.md) & [06_PawTrail_Task_Breakdown_and_Estimations.md](file:///d:/cody/PawTrail/docs/06_PawTrail_Task_Breakdown_and_Estimations.md)
- **Member B (Vision AI)**:
  - US-04: 공원 안내판 이미지셋 수집, 프롬프트 엔지니어링 및 `ParkBoardInspectionResult` 파서 구현.
  - US-05: 커뮤니티 노면 제보 검증 프롬프트 및 `SurfaceEnrichmentResult` 지도 링크 갱신 핸들러 구현.
- **Member C (Backend/GIS)**:
  - US-03: 환경부 토지피복지도 GeoJSON 로드 및 `geopandas` Spatial Join 모듈 구현, 시범구역 정사영상 육안 검증 시드 데이터셋 구축.

---

### 6. [README.md](file:///d:/cody/PawTrail/README.md)
- 2번 핵심 기능 및 3번 아키텍처 다이어그램/설명에 공원 안내판 비전 판독 및 토지피복지도 공간 결합 반영.

---

## Verification Plan

### Automated Verification
- 모든 마크다운 파일의 링크, 표 형식 및 Mermaid 다이어그램 구문 검증
- 수치 정합성 검증 (62 pt, 330 h, 54개 Task 일치 확인)
- API 엔드포인트(`POST /api/walks/inspect-board`, `POST /api/walks/verify-surface`) 및 DTO 명세 상호 일치 확인

### Manual Verification
- 01번~06번 문서와 README.md 전체에 걸쳐 비전 모델의 역할(안내판 판독 + 완주 후 제보 검증)과 토지피복지도 융합 전략이 빈틈없이 동기화되었는지 전수 확인
