# [시스템 아키텍처 설계서] PawTrail (포트레일)

> **AI Native 반려견 안심(무계단·완만 경사·그늘 우선) 산책 플래너 및 프라이버시 우선(Local-First) 플랫폼**  
> 본 문서는 PawTrail의 기획서, 애자일 사용자 스토리, 기술적 정정사항 및 AI Native 엔지니어링 원칙을 기반으로 설계된 전체 시스템 아키텍처 사양서입니다.

---

## 1. 아키텍처 개요 및 설계 원칙

### 1.1 핵심 설계 철학 (Architecture Principles)
1. **프라이버시 중심 로컬 저장 (Privacy-First & Local-First Architecture)**:
   - 견주의 거주지(자택 좌표), 상세 보행 이동 궤적, 반려견 신체 정보 등 민감한 개인 데이터는 **사용자 휴대폰(로컬 스토리지/IndexedDB)에만 보관**합니다.
   - 서버는 민감 정보를 영구 수집하지 않으며, 산책 생성 시 클라이언트가 보낸 일회성 페이로드로 연산 후 즉시 폐기하는 **완전한 무상태(Stateless) 백엔드**로 동작합니다.
2. **독립적이고 간결한 인증 (Simple Email Auth, No Social OAuth)**:
   - 외부 소셜 플랫폼(카카오, 구글)의 복잡한 등록 및 승인 병목을 배제하고, `Supabase Auth` 기반의 **단순 이메일/비밀번호 가입 체계**로 단일화합니다. (개발/CBT 중 Auto-confirm 활성화)
   - 커뮤니티 코스 공유나 위험 제보 시에만 최소한의 계정 식별자로 연동됩니다.
3. **AI Agent와 전문 라우팅 도구의 역할 분리 (Decoupled Agent-Routing Synergy)**:
   - AI Agent는 GIS 그래프 탐색 엔진 자체가 아닙니다. 자연어 파싱, 제약조건 구조화, 도구 선택, 후보 경로 평가에 집중합니다.
   - 실제 도로망 지오메트리 연산은 전문 **Routing API(OpenRouteService, OSRM 등) Adapter**를 통해 위임하며, 직접 A* 엔진을 바닥부터 구현하지 않습니다.
4. **다요소 공간 데이터 계층화 분석 (Layered Spatial Analysis)**:
   - **Steps Detector**: OSM `highway=steps` 기반 확인된 계단 구간 우선 배제.
   - **Slope Analyzer**: DEM 고도 데이터를 통한 최대 경사도(`max_slope_percent`) 및 급경사 비율 분석.
   - **Shade Estimator**: 태양각(SunCalc)과 건물 형상 데이터를 결합한 예상 그늘(Level 1~2) 점수화.
   - **Candidate Route Scorer**: 수집된 후보 경로를 다요소 가중 평가하여 최적 경로 결정.
5. **실현 가능한 모바일 UX (Next.js PWA & Foreground Tracking & DeepLink)**:
   - OS 절전 정책으로 끊기기 쉬운 모바일 웹 백그라운드 GPS 대신 **Foreground 위치 추적**을 기본 채택하고, 정밀 도보 길안내는 **네이버 지도 및 카카오맵 딥링크**를 원터치로 연동합니다.

---

## 2. 전체 시스템 아키텍처 다이어그램 (End-to-End)

```mermaid
flowchart TB
    subgraph Client["[Client Tier] Next.js / PWA 모바일 반응형 웹"]
        UI[UI Components & 조건 입력]
        MapView[Map Viewer & Polyline]
        GPSModule[Foreground GPS Tracker]
        CameraModule[현장 위험 사진 촬영 모듈]
        DeepLink[외부 지도 딥링크 모듈]
        
        subgraph LocalStore["[📱 Local-First Storage] IndexedDB"]
            DogProfile[반려견 프로필<br/>(체급, 연령, 관절 주의)]
            WalkTrack[개인 산책 궤적 & 자택 좌표<br/>(서버 절대 미전송)]
            FeedbackStore[최근 보행 피드백 누적]
            BackupManager[JSON 백업/가져오기]
        end
    end

    subgraph Gateway["[API Gateway & Backend] FastAPI"]
        Router[Stateless REST API Router]
        Validator[Pydantic V2 Strict Validator]
    end

    subgraph AI_Core["[AI & Intelligence Tier] LangGraph Agent"]
        Agent[Walk Planning ReAct Agent]
        State[LangGraph State Machine]
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

    subgraph Supabase_Cloud["[Cloud Persistence Tier] Supabase Cloud (최소 관리)"]
        Users[(auth.users<br/>간편 이메일/비밀번호 계정)]
        Courses[(community_courses<br/>출발지 200m 마스킹 공개 코스)]
        Hazards[(hazard_reports<br/>현장 턱/공사 제보 좌표 및 사진)]
        Storage[(Supabase Storage - 위험 사진)]
    end

    subgraph External["[External Services & APIs]"]
        ORS_API[Routing Engine: ORS / OSRM]
        OSM_DATA[OSM Footway / Steps Data]
        DEM_DATA[DEM Elevation Data]
        BUILDING_DATA[공공 건물 공간정보]
        KMA_API[기상청 단기예보 API]
        EXT_MAPS[네이버 / 카카오 지도 앱]
    end

    %% 연결 흐름
    UI --> Router
    MapView <--> Router
    GPSModule -.-> WalkTrack
    CameraModule --> Router
    DeepLink -.-> EXT_MAPS

    LocalStore -.->|산책 요청 시 일회성 페이로드 동봉| UI
    Router --> Validator --> Agent
    Router --> Tool_Vision

    Agent <--> State
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
    Tool_Vision <--> Storage

    Tool_Scorer --> Agent

    UI -.->|커뮤니티 코스 공유 시에만| Courses
    UI -.->|간편 이메일 가입/로그인| Users
    CameraModule -.->|위험 제보 시| Hazards
```

---

## 3. 계층별 상세 아키텍처

### 3.1 클라이언트 계층 (Frontend Tier)
* **프레임워크**: Next.js (App Router), TypeScript, Tailwind CSS, MapLibre GL JS, HTML5 Geolocation API, LocalForage / IndexedDB.
* **주요 구성요소**:
  1. **IndexedDB Local Storage Manager**:
     - `dog_profile`: 체급, 연령, 관절 상태, 기본 보행 속도 영구 로컬 보관.
     - `private_walks`: 자택 좌표가 포함된 개인 보행 궤적 및 개인 피드백 로컬 보관.
     - `backup_service`: 브라우저 캐시 삭제에 대비한 **"내 데이터 JSON 파일 내보내기/가져오기"** 지원.
  2. **Planner Screen**:
     - 로컬에 저장된 반려견 프로필을 자동으로 읽어와 기본 조건 세팅.
     - 목표 산책 시간(15~60분), 계단 회피, 완만 경사, 그늘 우선 토글.
  3. **Map Route Viewer**:
     - 추천 순환 경로 Polyline 분기 렌더링 (그늘/완만: 초록, 일반: 파랑, 주의: 주황).
     - 외부 지도(네이버/카카오 지도) 도보 길찾기 딥링크 버튼.
  4. **Foreground GPS Tracker**:
     - 사용자가 화면을 켜고 보행하는 동안 위치 좌표를 3~5초 간격으로 수집하여 브라우저 로컬에 궤적 갱신.
  5. **간편 이메일 로그인 모달**:
     - 소셜 OAuth 없이 이메일과 비밀번호 입력만으로 1초 만에 회원가입/로그인 완료 (`supabase.auth.signUp`).

---

### 3.2 백엔드 및 API 계층 (FastAPI Backend)
* **무상태(Stateless) API 원칙**:
  - 백엔드는 특정 사용자의 개인정보 세션을 보관하지 않습니다.
  - 산책 플랜 요청 시 클라이언트가 로컬 프로필과 피드백 요약을 전달하면, 이를 바탕으로 라우팅을 수행하고 결과만 응답합니다.

| Method | Endpoint | 설명 | 핵심 DTO (In / Out) |
|:---:|---|---|---|
| `POST` | `/api/v1/walk/plan` | 로컬 프로필+조건 기반 최적 코스 생성 (무상태) | In: `WalkPlanRequest` ➔ Out: `WalkPlanResponse` |
| `POST` | `/api/v1/walk/reroute` | 현장 위험 감지 시 안전 우회 재탐색 | In: `RerouteRequest` ➔ Out: `WalkPlanResponse` |
| `POST` | `/api/v1/surface/inspect` | 현장 사진 업로드 기반 시각적 위험물 판독 | In: `UploadFile(Image)` ➔ Out: `HazardReport` |
| `POST` | `/api/v1/community/share` | 완주 코스 공유 (출발지 200m 마스킹 적용) | In: `CourseShareRequest` ➔ Out: `CommunityCourse` |
| `GET` | `/api/v1/community/feed` | 다른 견주들의 공유 코스 피드 조회 | Out: `List[CommunityCourseSummary]` |
| `POST` | `/api/v1/hazards` | 현장 위험 제보 등록 (공공 안전용) | In: `HazardCreateRequest` ➔ Out: `HazardReport` |
| `GET` | `/api/v1/parking/nearby` | 출발지 반경 내 P&R 공영주차장 목록 조회 | In: `lat, lon, radius` ➔ Out: `List[ParkingLot]` |
| `GET` | `/api/v1/weather/heat-risk`| 기상청 예보 기반 시간대별 열 위험 지수 조회 | In: `lat, lon` ➔ Out: `HeatRiskResponse` |

---

## 4. 핵심 데이터 모델 및 DTO 명세

### 4.1 WalkPlanRequest (클라이언트 로컬 데이터 동봉)
```json
{
  "origin": {"lat": 37.492, "lon": 126.923},
  "target_duration_minutes": 25,
  "avoid_stairs": true,
  "slope_preference": "gentle",
  "shade_priority": true,
  "client_dog_context": {
    "breed": "Maltese",
    "age_years": 9,
    "speed_kmh": 2.6,
    "joint_caution": true
  },
  "client_recent_feedback": [
    {"tag": "too_steep", "count": 2},
    {"tag": "cool_shade", "count": 3}
  ]
}
```

### 4.2 WalkPlanResponse (생성된 경로 응답)
```json
{
  "route_id": "route_local_123",
  "total_distance_meters": 1150,
  "estimated_duration_minutes": 24,
  "stairs_avoidance_applied": true,
  "stairs_detected_in_route": false,
  "max_slope_percent": 3.5,
  "average_shade_ratio": 0.71,
  "data_confidence_summary": {
    "stairs": 0.92,
    "slope": 0.85,
    "shade": 0.78
  },
  "external_nav_links": {
    "naver_map": "nmap://route/walk?...",
    "kakao_map": "kakaomap://route?..."
  },
  "agent_comment": "로컬에 저장된 초코의 관절 케어와 지난 산책 피드백을 반영해 계단 없이 완만한(최대 3.5%) 그늘 코스를 생성했습니다."
}
```

---

## 5. 데이터베이스 스키마 설계 (Supabase Cloud)

서버 DB는 개인정보를 일체 저장하지 않으며, **이메일 계정과 커뮤니티 데이터만 관리**합니다.

```sql
-- 1. 사용자 계정 (Supabase Auth 기본 연동)
-- auth.users 에 이메일/비밀번호 해시 자동 보관

-- 2. 커뮤니티 공개 코스 (자택 노출 방지: 출발지 200m 마스킹 적용)
CREATE TABLE community_courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    total_distance_m NUMERIC(7, 1) NOT NULL,
    estimated_duration_min INT NOT NULL,
    has_stairs BOOLEAN DEFAULT false,
    max_slope_percent NUMERIC(4, 1),
    average_shade_ratio NUMERIC(3, 2),
    masked_path_geojson JSONB NOT NULL, -- 출발/도착지 200m 마스킹된 지오메트리
    likes_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. 현장 위험 제보 테이블 (공공 안전 목적)
CREATE TABLE hazard_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    lat NUMERIC(9, 6) NOT NULL,
    lon NUMERIC(9, 6) NOT NULL,
    hazard_type TEXT NOT NULL, -- 'high_curb', 'unregistered_stairs', 'construction'
    severity TEXT NOT NULL,    -- 'low', 'medium', 'high'
    image_url TEXT,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. 코스 좋아요(북마크) 테이블
CREATE TABLE course_likes (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES community_courses(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, course_id)
);
```

---

## 6. 보안 및 프라이버시 원칙 (Privacy by Design)

1. **개인정보 제로 원칙 (Zero PII on Server)**:
   - 서버 PostgreSQL에는 견주의 실명, 전화번호, 자택 주소, 반려견 건강 정보가 전혀 존재하지 않습니다.
2. **공유 시 공간 마스킹 (Spatial Jittering & Truncation)**:
   - 사용자가 완주 코스를 커뮤니티에 업로드할 때, 클라이언트가 출발점과 도착점 기준 200m 반경의 좌표를 자동으로 절단하거나 무작위 오프셋(마스킹)을 적용하여 업로드합니다.
3. **간편 이메일 보안**:
   - 비밀번호는 Supabase의 강력한 bcrypt/argon2 알고리즘으로 자동 해싱 보관되며, 소셜 OAuth 연동 취약점 리스크가 원천 차단됩니다.
