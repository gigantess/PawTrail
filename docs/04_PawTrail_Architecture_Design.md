# [시스템 아키텍처 설계서] PawTrail (포트레일)

> **AI Native 반려견 안심(무계단·완만 경사·그늘 우선) 산책 플래너 및 핸즈프리 모바일 앱 플랫폼**  
> 본 문서는 PawTrail의 기획서, 애자일 사용자 스토리, 기술적 정정사항 및 AI Native 엔지니어링 원칙을 기반으로 설계된 전체 시스템 아키텍처 사양서입니다.

---

## 1. 아키텍처 개요 및 설계 원칙

### 1.1 핵심 설계 철학 (Architecture Principles)
1. **시선 해방(Eyes-Free) & 두 손 자유(Hands-Free) 백그라운드 음성 길 안내**:
   - 한 손에 리드줄을 잡고 다른 손으로 스마트폰을 계속 보며 걷는 위험한 시각 의존 UX를 탈피합니다.
   - **React Native (Expo SDK 51+) + Android Foreground Service**를 채택하여 스마트폰을 주머니나 가방에 넣고 화면을 꺼두어도 백그라운드 GPS를 수신하고, OSRM 스텝 및 경로 속성을 결합한 **`expo-speech` TTS 기반 실시간 음성 브리핑**을 제공합니다.
2. **배포 피로도 제로 (EAS Build & EAS Update OTA)**:
   - 복잡한 스토어 심사 대기나 잦은 APK 재설치 번거로움을 없애기 위해, **EAS Build로 테스터용 APK를 1회 배포**하고 이후 모든 UI/로직 수정은 **EAS Update (`expo-updates`) 무선 OTA**로 실시간 무점검 배포합니다.
3. **프라이버시 중심 로컬 저장 (Privacy-First Local Storage)**:
   - 견주의 자택 위치, 상세 보행 GPS 궤적, 반려견 프로필은 **사용자 폰 로컬(`AsyncStorage`)에만 보관**합니다.
   - 백엔드는 민감 정보를 저장하지 않는 **완전한 무상태(Stateless)** 구조로 운영됩니다.
4. **독립적이고 간결한 인증 (Simple Email Auth, No Social OAuth)**:
   - 외부 소셜 OAuth 연동 병목을 배제하고, `Supabase Auth` 기반의 **단순 이메일/비밀번호 가입 체계**로 단일화합니다. (개발/CBT 중 Auto-confirm 활성화)
   - 커뮤니티 코스 공유 시에만 **출발지/도착지 200m 마스킹 블러링**을 적용하여 업로드합니다.
5. **AI Agent와 전문 라우팅 도구의 분리**:
   - AI Agent는 조건 구조화와 다요소 채점에 집중하고, 도로망 지오메트리 연산은 전문 **Routing API(ORS/OSRM) Adapter**에 위임합니다.
6. **질병 용어 배제 및 긍정적 웰니스 UX 원칙 (Wellness Terminology Policy)**:
   - 앱 실행 화면, 온보딩, 음성 안내 스크립트, AI 프롬프트에서 '슬개골 탈구', '질환 단계' 등 임상적 용어를 전면 배제합니다.
   - 대신 *"폭신한 길"*, *"관절 안심 케어"*, *"부드러운 완만길"* 등 긍정적 웰니스 언어로 순화합니다. (의학 통계는 발표 자료에만 제한 활용)

---

## 2. 전체 시스템 아키텍처 다이어그램 (End-to-End)

```mermaid
flowchart TB
    subgraph Client["[Client Tier] React Native Mobile App (Expo SDK 51+)"]
        UI[UI Components & 웰니스 조건 입력]
        MapModule[React Native Maps & Polyline]
        NaviEngine[Hands-Free Voice Navi Engine<br/>expo-location Foreground Service + expo-speech]
        CameraModule[현장 위험 사진 촬영 (expo-camera)]
        EASModule[EAS Update OTA 클라이언트]
        
        subgraph LocalStore["[📱 Local Storage] AsyncStorage"]
            DogProfile[반려견 프로필<br/>(체급, 연령, 관절 안심 케어)]
            WalkTrack[개인 산책 궤적 & 자택 좌표<br/>(서버 절대 미전송)]
            FeedbackStore[최근 보행 피드백 누적]
            BackupManager[JSON 백업/가져오기]
        end
    end

    subgraph Gateway["[API Gateway & Backend] FastAPI (Render / Cloud Run)"]
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
        EAS_CLOUD[Expo EAS Update CDN]
    end

    %% 연결 흐름
    UI --> Router
    MapModule <--> Router
    NaviEngine <--> MapModule
    CameraModule --> Router
    EASModule <--> EAS_CLOUD

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

### 3.1 클라이언트 계층 (React Native Expo App)
* **프레임워크**: React Native (Expo SDK 51+), TypeScript, react-native-maps, expo-location, expo-speech, expo-camera, `@react-native-async-storage/async-storage`.
* **주요 구성요소**:
  1. **Hands-Free Voice Navigation Engine**:
     - **Android Foreground Service**로 백그라운드 GPS 위치를 지속 수신.
     - OSRM/ORS `steps` 정보(회전각, 거리)와 경로 속성을 결합해 30m 전 `expo-speech` 사전 브리핑 송출 (*"50m 앞 부드러운 완만길입니다. 우회전하세요"*).
  2. **EAS Update 무중단 OTA 모듈**:
     - 앱 시작 시 Expo CDN에서 최신 JS 번들 체크 및 무선 무점검 핫픽스 즉시 적용.
  3. **AsyncStorage Local Storage Manager**:
     - `dog_profile`: 체급, 연령, 관절 안심 케어 수준 로컬 보관.
     - `private_walks`: 자택 좌표가 포함된 개인 보행 궤적 및 개인 피드백 로컬 보관.
     - `backup_service`: JSON 파일 내보내기/가져오기 지원.
  4. **Map Route Viewer**:
     - GeoJSON Polyline 색상 분기 렌더링 (그늘/완만: 초록, 일반: 파랑, 주의: 주황).
  5. **간편 이메일 로그인 모달**:
     - `supabase.auth.signUp` 기반 간편 이메일/비밀번호 가입 및 로그인.

---

### 3.2 백엔드 및 API 계층 (FastAPI Backend)
* **무상태(Stateless) API 원칙**: 백엔드는 특정 사용자의 개인정보 세션을 저장하지 않고, 산책 요청 시 클라이언트가 보낸 일회성 페이로드로 연산 후 즉시 응답.

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
    "joint_care_level": "high"
  },
  "client_recent_feedback": [
    {"tag": "too_steep", "count": 2},
    {"tag": "cool_shade", "count": 3}
  ]
}
```

### 4.2 WalkPlanResponse (생성된 경로 및 음성 스텝 응답)
```json
{
  "route_id": "route_local_123",
  "total_distance_meters": 1150,
  "estimated_duration_minutes": 24,
  "stairs_avoidance_applied": true,
  "stairs_detected_in_route": false,
  "max_slope_percent": 3.5,
  "average_shade_ratio": 0.71,
  "navigation_steps": [
    {"distance_m": 120, "instruction": "직진 후 50m 앞 우회전하세요", "voice_brief": "50m 앞 부드러운 완만길입니다. 우회전하세요"},
    {"distance_m": 350, "instruction": "그늘 산책로 진입", "voice_brief": "지금부터 300m 동안 시원한 그늘길이 이어집니다"}
  ],
  "agent_comment": "초코의 편안한 보행을 위해 계단 없이 완만한(최대 3.5%) 그늘 코스를 준비했습니다."
}
```

---

## 5. 데이터베이스 스키마 설계 (Supabase Cloud)

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

## 6. 비기능 아키텍처 및 웰니스 정책

1. **시선 해방 안전성**: `expo-location`과 `expo-speech`의 유기적 결합으로 스마트폰 화면 주시를 원천 차단.
2. **배포 효율성**: EAS Update 기반으로 1회 APK 설치 후 무선 OTA 핫픽스 실시간 적용.
3. **개인정보 제로 원칙 (Zero PII on Server)**: 자택 주소 및 상세 궤적은 폰에만 저장, 공유 시 200m 자동 마스킹.
4. **웰니스 용어 준수**: 앱 내에서 질병 용어를 배제하고 긍정적인 감성 케어 언어 사용.
