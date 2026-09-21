# [시스템 아키텍처 설계서] PawTrail (포트레일)

> **AI Native 반려견 안심(무계단·완만 경사·그늘 우선) 산책 플래너 및 기록 플랫폼**  
> 본 문서는 PawTrail의 기획서, 애자일 사용자 스토리, 기술적 정정사항 및 AI Native 엔지니어링 원칙을 기반으로 설계된 전체 시스템 아키텍처 사양서입니다.

---

## 1. 아키텍처 개요 및 설계 원칙

### 1.1 핵심 설계 철학 (Architecture Principles)
1. **AI Agent와 전문 라우팅 도구의 역할 분리 (Decoupled Agent-Routing Synergy)**:
   - AI Agent는 GIS 그래프 탐색 엔진 자체가 아닙니다. Agent는 자연어 이해, 반려견 컨텍스트 파악, 제약조건 구조화, 도구 선택, 후보 경로 평가 및 설명에 집중합니다.
   - 실제 도로망 지오메트리 연산은 전문 **Routing API(OpenRouteService, OSRM 등) Adapter**를 통해 위임하며, 직접 A* 엔진을 바닥부터 구현하지 않습니다.
2. **다요소 공간 데이터 계층화 분석 (Layered Spatial Analysis)**:
   - **Steps Detector**: OSM `highway=steps` 기반 확인된 계단 구간 우선 배제.
   - **Slope Analyzer**: DEM 고도 데이터를 통한 최대 경사도(`max_slope_percent`) 및 급경사 비율 분석.
   - **Shade Estimator**: 태양각(SunCalc)과 건물 형상 데이터를 결합한 예상 그늘(Level 1~2) 점수화.
   - **Candidate Route Scorer**: 수집된 후보 경로를 다요소 가중 평가하여 최적 경로 결정.
3. **데이터 투명성 및 신뢰도 체계 (Data Source & Confidence)**:
   - "100% 무계단 보장", "사진으로 실시간 지면온도 측정"과 같은 비과학적 설계를 배제합니다.
   - 모든 세그먼트와 경로 메타데이터에 `source`, `confidence`, `estimated` 필드를 명시합니다.
4. **실현 가능한 모바일 UX (Responsive Next.js PWA & Foreground Tracking)**:
   - OS 백그라운드 GPS 제약이 심한 모바일 환경에서 불안정한 백그라운드 트래킹을 핵심 전제로 두지 않고, 화면을 열어 산책 상태를 확인하는 **Foreground 위치 추적**을 기본 채택합니다.
   - 턴바이턴 도보 내비게이션은 **네이버 지도 및 카카오맵 딥링크**를 연계하여 안정성과 사용자 편의성을 확보합니다.
5. **예측 가능한 REST API & 경량 구조화 DB (Predictable REST & Relational Persistence)**:
   - 불필요한 WebSocket/SSE 복잡성을 배제하고 명확한 REST API 표준을 준수합니다.
   - 처음부터 복잡한 Vector DB를 강제하지 않고, **Supabase PostgreSQL**의 정형 관계형 데이터와 JSONB 필드를 기반으로 Context Memory를 구축합니다.

---

## 2. 전체 시스템 아키텍처 다이어그램 (End-to-End)

```mermaid
flowchart TB
    subgraph Client["[Client Tier] Next.js / PWA 모바일 반응형 웹"]
        UI[UI Components & 조건 입력<br/>(시간/계단/경사/그늘/반려견)]
        MapView[Map Viewer & Polyline<br/>(안전/경사/그늘 색상 구분)]
        GPSModule[Foreground GPS Tracker<br/>HTML5 Geolocation]
        CameraModule[현장 위험 사진 촬영 모듈]
        DeepLink[외부 지도 딥링크 모듈<br/>네이버/카카오 지도 도보 길찾기]
    end

    subgraph Gateway["[API Gateway & Backend] FastAPI"]
        Router[REST API Router & CORS]
        Auth[Supabase Auth Guard]
        Validator[Pydantic V2 Strict Validator]
    end

    subgraph AI_Core["[AI & Intelligence Tier] LangGraph Agent"]
        Agent[Walk Planning ReAct Agent]
        State[LangGraph State Machine]
        MemoryManager[Canine Context Memory Injector]
    end

    subgraph Tool_Layer["[Agent Tool Layer] @tool"]
        Tool_Routing[Routing API Adapter<br/>ORS / OSRM]
        Tool_Steps[OSM Steps Detector]
        Tool_Slope[DEM Elevation & Slope Analyzer]
        Tool_Shade[Solar & Building Shade Estimator]
        Tool_Scorer[Candidate Route Scorer]
        Tool_Vision[Vision Hazard Inspector<br/>Gemini 1.5 Flash]
        Tool_Weather[Weather & Heat Risk Tool]
        Tool_Parking[Public Parking API Tool]
    end

    subgraph Data_Tier["[Data & Persistence Tier] Supabase"]
        PG[(PostgreSQL Relational DB)]
        Storage[(Supabase Storage - 현장 사진)]
    end

    subgraph External["[External Services & APIs]"]
        ORS_API[Routing Service: ORS / OSRM]
        OSM_DATA[OpenStreetMap Footway / Steps Data]
        DEM_DATA[DEM Elevation Data / SRTM]
        BUILDING_DATA[공공 건물 공간정보 / VWorld]
        KMA_API[기상청 단기예보 API]
        PARK_API[공공데이터포털 공영주차장 API]
        EXT_MAPS[네이버 / 카카오 지도 앱]
    end

    %% 연결 흐름
    UI --> Router
    MapView <--> Router
    GPSModule --> Router
    CameraModule --> Router
    DeepLink -.-> EXT_MAPS

    Router --> Validator --> Auth
    Auth --> Agent
    Auth --> Tool_Vision

    Agent <--> State
    Agent <--> MemoryManager
    MemoryManager <--> PG

    Agent --> Tool_Routing
    Agent --> Tool_Steps
    Agent --> Tool_Slope
    Agent --> Tool_Shade
    Agent --> Tool_Scorer
    Agent --> Tool_Weather
    Agent --> Tool_Parking

    Tool_Routing <--> ORS_API
    Tool_Steps <--> OSM_DATA
    Tool_Slope <--> DEM_DATA
    Tool_Shade <--> BUILDING_DATA
    Tool_Weather <--> KMA_API
    Tool_Parking <--> PARK_API
    Tool_Vision <--> Storage

    Tool_Scorer --> Agent
```

---

## 3. 계층별 상세 아키텍처

### 3.1 클라이언트 계층 (Frontend Tier)
* **기술 스택**: Next.js (App Router), TypeScript, Tailwind CSS, MapLibre GL JS / Leaflet, HTML5 Geolocation API, PWA Service Worker.
* **주요 구성요소**:
  1. **Planner Screen**:
     - 반려견 선택 드롭다운, 산책 목표 시간(15~60분), 계단 회피 토글, 경사도 선호 칩(매우 완만/완만/제한 없음), 그늘 우선 토글.
     - 대화형 자연어 입력창 ("10살 시츄, 계단 피하고 완만한 20분 그늘 코스").
  2. **Map & Preview Component**:
     - 추천 순환 경로 Polyline 렌더링:
       - 🌿 완만·그늘 안전 구간: `#10B981` (Green)
       - 🍂 일반 보행 구간: `#3B82F6` (Blue)
       - ⚠️ 급경사 주의 구간: `#F97316` (Orange)
       - ⛔ 계단 인접 경고 (불가피 시): `#EF4444` (Red)
     - 경로 요약 카드: 총 거리(km), 예상 시간(분), 최대 경사도(%), 예상 그늘 비율(%), 확인된 계단 수(개).
  3. **Foreground GPS Tracker**:
     - 사용자가 화면을 켜고 보행하는 동안 위치 좌표를 3~5초 간격으로 수집하여 실시간 보행 궤적 및 경과 시간을 지도 위에 갱신.
  4. **외부 지도 길찾기 연동 (DeepLink Engine)**:
     - 출발지와 주요 Waypoint 좌표를 네이버 지도 / 카카오맵 도보 길찾기 URL Scheme으로 원터치 전달.
  5. **Camera & Hazard Report Modal**:
     - 보행 중 높은 턱이나 계단 발견 시 사진 촬영 및 업로드 ➔ 판독 결과 확인 및 우회 재탐색 트리거.

---

### 3.2 백엔드 및 API 계층 (Backend Tier)
* **기술 스택**: Python 3.11+, FastAPI, Uvicorn, Pydantic V2, HTTPX, Shapely, SunCalc Python.
* **핵심 REST API 엔드포인트 명세**:

| Method | Endpoint | 설명 | 핵심 DTO (In / Out) |
|:---:|---|---|---|
| `POST` | `/api/v1/walk/plan` | 산책 조건 기반 최적 순환 코스 생성 및 평가 | In: `WalkPlanRequest` ➔ Out: `WalkPlanResponse` |
| `POST` | `/api/v1/walk/reroute` | 현장 위험 감지 시 해당 구간 우회 재탐색 | In: `RerouteRequest` ➔ Out: `WalkPlanResponse` |
| `POST` | `/api/v1/surface/inspect` | 현장 사진 업로드 기반 시각적 위험물/턱/계단 판독 | In: `UploadFile(Image)` ➔ Out: `HazardReport` |
| `POST` | `/api/v1/walk/checkin` | Foreground 실시간 위치 포인트 수집/체크인 | In: `WalkCheckinRequest` ➔ Out: `CheckinStatusResponse` |
| `POST` | `/api/v1/walk/finish` | 산책 완주 기록 저장 및 통계 산출 | In: `WalkFinishRequest` ➔ Out: `WalkHistoryResponse` |
| `POST` | `/api/v1/walk/feedback` | 산책 종료 후 보행 체감 만족도 및 피드백 저장 | In: `FeedbackRequest` ➔ Out: `FeedbackResponse` |
| `GET` | `/api/v1/walk/history` | 사용자 반려견별 과거 산책 기록 조회 | Out: `List[WalkHistorySummary]` |
| `GET` | `/api/v1/parking/nearby` | 출발지 반경 내 P&R 공영주차장 목록 조회 | In: `lat, lon, radius` ➔ Out: `List[ParkingLot]` |
| `GET` | `/api/v1/weather/heat-risk`| 기상청 예보 기반 시간대별 열 위험 지수 조회 | In: `lat, lon` ➔ Out: `HeatRiskResponse` |

---

### 3.3 AI 및 도구 계층 (AI & Tool Layer)

#### 1. Walk Planning Agent (LangGraph)
- **역할**: 사용자 발화 의도 파악, 제약조건 구조화, 도구 호출 시퀀스 제어, 후보 경로 평가 결과에 대한 친절한 설명 제공.
- **상태 관리 (`AgentState`)**:
  ```python
  class AgentState(TypedDict):
      messages: list[AnyMessage]
      dog_context: DogProfile
      plan_request: WalkPlanRequest
      candidate_routes: list[CandidateRoute]
      selected_route: WalkPlanResponse | None
      hazard_context: HazardReport | None
  ```

#### 2. 전문 도구 레지스트리 (Tool Registry)
- **`RoutingAdapter`**:
  - OpenRouteService / OSRM API 호출.
  - 출발지 중심 다각형 Waypoint 샘플링 기반 순환 후보 경로(Candidate Routes 2~3개) 생성.
- **`StepsDetector`**:
  - 도로망 링크 중 `highway=steps` 속성 식별.
  - `has_stairs`, `stairs_data_source`, `stairs_data_confidence` 메타데이터 부여.
- **`SlopeAnalyzer`**:
  - DEM 래스터/고도 프로파일을 통해 구간별 `max_slope_percent`, `steep_segment_ratio` 연산.
- **`ShadeEstimator`**:
  - `SunCalc`를 이용한 실시간 태양 고도/방위 계산.
  - 2.5D 건물 폴리곤 및 높이 기반 그림자 다각형 연산 ➔ 보행 경로 교차율(`shade_ratio`) 산출.
- **`CandidateRouteScorer`**:
  - 다요소 가중 비용 함수 적용:
    $$\text{Score} = w_1 \cdot \text{StairsPenalty} + w_2 \cdot \text{SlopePenalty} + w_3 \cdot \text{ShadeBonus} + w_4 \cdot \text{DurationFit}$$
- **`VisionHazardInspector`**:
  - Gemini 1.5 Flash를 호출하여 높은 턱, 야외 계단, 공사 구간 식별. (※ 지면 온도는 직접 측정하지 않음)
- **`WeatherHeatRiskTool`**:
  - 기상청 단기예보(기온, 운량, 습도) 기반 열 지수(Heat Index) 추정.

---

## 4. 핵심 데이터 모델 및 DTO 명세

### 4.1 DogProfile (반려견 프로필)
```json
{
  "id": "uuid",
  "name": "초코",
  "breed": "Maltese",
  "weight_kg": 3.5,
  "age_years": 8,
  "joint_caution": true,
  "speed_kmh": 2.8,
  "max_allowed_slope": 5.0,
  "avoid_stairs": true
}
```

### 4.2 WalkPlanRequest (산책 생성 요청)
```json
{
  "dog_id": "uuid",
  "origin": {"lat": 37.492, "lon": 126.923},
  "target_duration_minutes": 25,
  "avoid_stairs": true,
  "slope_preference": "gentle",
  "shade_priority": true,
  "preferred_surfaces": ["grass", "dirt"]
}
```

### 4.3 RouteSegment (경로 세그먼트 메타데이터)
```json
{
  "segment_id": "seg_001",
  "geometry": [[126.923, 37.492], [126.925, 37.493]],
  "length_meters": 180.5,
  "has_stairs": false,
  "stairs_data_source": "osm_tag",
  "stairs_data_confidence": 0.92,
  "max_slope_percent": 3.2,
  "average_slope_percent": 1.8,
  "slope_data_source": "dem_raster",
  "slope_data_confidence": 0.85,
  "estimated_shade_ratio": 0.75,
  "shade_estimation_source": "solar_building_model",
  "shade_confidence": 0.78,
  "surface_type": "dirt",
  "surface_source": "land_cover_map"
}
```

### 4.4 WalkPlanResponse (최종 산책 플랜 응답)
```json
{
  "route_id": "route_987",
  "total_distance_meters": 1250,
  "estimated_duration_minutes": 24,
  "stairs_avoidance_applied": true,
  "stairs_detected_in_route": false,
  "max_slope_percent": 3.8,
  "average_shade_ratio": 0.68,
  "data_confidence_summary": {
    "stairs": 0.92,
    "slope": 0.85,
    "shade": 0.78
  },
  "segments": ["...RouteSegment list..."],
  "external_nav_links": {
    "naver_map": "nmap://route/walk?...",
    "kakao_map": "kakaomap://route?..."
  },
  "agent_comment": "초코의 관절을 위해 계단이 없고 경사가 완만한(최대 3.8%) 그늘길 위주 순환 코스를 준비했습니다."
}
```

### 4.5 HazardReport (현장 위험 분석 결과)
```json
{
  "hazard_id": "haz_123",
  "hazard_type": "high_curb",
  "severity": "high",
  "confidence": 0.89,
  "location": {"lat": 37.4931, "lon": 126.9242},
  "route_action": "avoid_recommended",
  "comment": "높이 약 25cm의 턱이 감지되었습니다. 슬개골에 무리가 갈 수 있으므로 우회를 권장합니다.",
  "analyzed_at": "2026-09-21T15:30:00Z"
}
```

---

## 5. 데이터베이스 스키마 설계 (Supabase PostgreSQL)

```sql
-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 반려견 프로필 테이블
CREATE TABLE dogs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    breed TEXT,
    weight_kg NUMERIC(4, 1),
    age_years INT,
    joint_caution BOOLEAN DEFAULT false,
    speed_kmh NUMERIC(3, 1) DEFAULT 3.0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 산책 계획 및 이력 테이블
CREATE TABLE walk_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dog_id UUID REFERENCES dogs(id) ON DELETE CASCADE,
    origin_lat NUMERIC(9, 6) NOT NULL,
    origin_lon NUMERIC(9, 6) NOT NULL,
    total_distance_m NUMERIC(7, 1),
    actual_duration_min INT,
    stairs_avoided BOOLEAN DEFAULT true,
    max_slope_percent NUMERIC(4, 1),
    average_shade_ratio NUMERIC(3, 2),
    actual_path_geojson JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 산책 피드백 테이블 (Context Memory Feedforward)
CREATE TABLE walk_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    walk_id UUID REFERENCES walk_history(id) ON DELETE CASCADE,
    satisfaction_score INT CHECK (satisfaction_score BETWEEN 1 AND 5),
    tags TEXT[], -- ['no_stairs', 'gentle_slope', 'cool_shade', 'too_steep']
    user_comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 현장 위험 제보 테이블
CREATE TABLE hazard_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id),
    lat NUMERIC(9, 6) NOT NULL,
    lon NUMERIC(9, 6) NOT NULL,
    hazard_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## 6. 비기능 아키텍처 및 보안 원칙

1. **API Key 보안**:
   - OpenAI/Gemini, OpenRouteService, Supabase Service Role 키는 프론트엔드에 절대 노출하지 않으며 FastAPI 서버 환경변수로만 관리.
2. **개인정보 보호 (Location Privacy)**:
   - 커뮤니티 공유 기능 사용 시 출발지/집 주소 노출 방지를 위해 출발지 기준 200m 구간 좌표 마스킹(Jittering/Blurring) 적용.
3. **오류 처리 및 Fallback**:
   - Routing API 장애 시 로컬 캐시된 주요 산책로 템플릿 반환.
   - 건물 높이 데이터 결측 지역은 기본 일사량 추정 모델(SunCalc 단독)로 Fallback.
   - OSM 계단 데이터 결측 가능성에 대비해 현장 Vision 제보와 연계.
