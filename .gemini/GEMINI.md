# Gemini Code Assist 준수 지침 (GEMINI.md)

본 문서는 **PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 에이전트 및 기록·공유 플랫폼)** 개발 프로젝트에서 VSCode의 Gemini Code Assist 확장이 코드를 분석, 제안, 생성 및 리팩토링할 때 반드시 준수해야 하는 엔지니어링 지침입니다. AI 모델은 모든 응답에서 아래 핵심 원칙과 세부 기술 요구사항을 엄격히 반영해야 합니다.

---

## [핵심 원칙 0] 감정 표현 배제, AI Native 집중 및 작업 태도

1. **[감정 표현 배제 및 언어]**: 코드 구현, 개선 및 결함 처리 시 감정적인 수사를 일절 배제하고, 명확하고 간결하며 논리적인 한국어로 답변합니다.
2. **[AI Native 관점의 선택과 집중 (핵심)]**:
   - **실제 동작 우선 (Working Software Over Mockups)**: 단순 목업이나 시연용 더미가 아니라, 실제 Supabase Cloud, FastAPI 백엔드, LangGraph ReAct Agent, Routing API Adapter, Gemini Vision을 E2E로 연결하여 실제 견주가 반복 사용 가능한 프로덕션 수준의 실행 가능한 서비스를 구축합니다. 백엔드와 연결되지 않은 껍데기 UI는 방치하지 않습니다.
   - **AI Native 도구 오케스트레이션 (`@tool` 표준화)**: 복잡한 C++ 수준의 GIS 엔진을 바닥부터 재발명하지 않고, 표준 라우팅 API Adapter와 외부 서비스를 Agent의 도구로 등록하여 자율 제어·호출하도록 구성합니다:
     - `get_dog_context`: 클라이언트 로컬 반려견 프로필 및 최근 산책 체감 피드백 수신
     - `generate_loop_route`: Routing API Provider(ORS/OSRM) 호출 및 최적 순환 경로 후보 도출
     - `analyze_surface_image`: 현장 노면 및 장애물(높은 턱, 계단, 공사구간) 시각적 위험 판독 (Gemini Flash 체인)
     - `search_parking`: 출발 거점 인근 공영주차장 P&R 거점 조회
   - **시선 해방(Eyes-Free) & 두 손 자유(Hands-Free) 백그라운드 음성 길 안내**: 한 손에 리드줄을 잡고 스마트폰 화면을 보며 걷는 위험을 배제하기 위해, **React Native (Expo SDK 51+) 및 Android Foreground Service(`expo-location`) + `expo-speech` TTS**를 기반으로 주머니 속(화면 꺼짐 상태)에서도 턴 30m 전 알림 및 노면 속성("50m 앞 완만한 흙길입니다. 우회전하세요"), 40m 경로 이탈 경고를 음성 브리핑합니다.
   - 테스터 재설치 피로를 없애기 위해 **단 1회 Android APK 빌드(EAS Build) 후 GitHub Actions 연계 EAS Update(`expo-updates` 무선 무점검 OTA)**를 통해 신속한 무선 패치를 지속 제공합니다.
   - 복잡한 양방향 SSE/웹소켓 스트리밍 디버깅에 갇히지 않고, **안정적이고 예측 가능한 REST API 구조**를 준수하여 5주 완결형 로드맵 및 5인 실사용자 CBT(클로즈드 베타 테스트) 피드백 튜닝에 집중합니다.
3. **[배포 및 외부 인프라 자율성 제한]**:
   - EAS Build, EAS Update, Supabase 프로덕션 DDL 배포, n8n 프로덕션 웹훅 트리거 등 외부 서비스 반영 명령어는 **사용자의 명시적 요청이나 사전 승인 없이 임의로 자동 실행하지 않으며**, 필요한 경우 안전한 스크립트나 가이드만 제공합니다.
4. **[검증 신뢰성]**: 가짜 테스트 통과 보고나 가정에 기반한 결과를 제공하지 않으며, 실제 실행 결과 및 반환 데이터를 기반으로 보고합니다.
5. **[YAGNI & No Spec Creep (요청하지 않은 기능 추가 절대 금지)]**:
   - 기획서(`docs/01_PawTrail_Project_Proposal.md`), 애자일 사용자 스토리(`docs/03_PawTrail_Agile_User_Stories.md`, **18개 핵심 스토리 / 77pt / 372h**), 작업 분할 명세서(`docs/06_PawTrail_Task_Breakdown_and_Estimations.md`, **68개 Task**)에 정의되지 않은 불필요한 기능, 더미 컴포넌트, 미확정 로직을 임의로 생성하지 않습니다.
   - 기능 개선 시에도 요구사항 범위 내에서 최소·최적의 코드를 작성하며, 불필요한 레거시 코드는 즉시 정리합니다.
6. **[코드 무결성 및 사후 정리 의무]**:
   - 디버깅용 임시 로그나 목(Mock) 데이터는 문제 해결 즉시 완전히 제거하여 프로덕션 코드베이스의 100% 무결성을 회복합니다.
7. **[사용자 스토리 및 Task 변경 시 테스트케이스 동기화 의무 (필수)]**:
   - 구현 과정에서 사용자 스토리(**US-A1 ~ US-H1**), 인수 조건(Acceptance Criteria), 완료 정의(DoD) 또는 하위 구현 Task의 요구사항, 비즈니스 룰, 파라미터가 변경·추가·조정될 경우, **반드시 이에 대응하는 테스트케이스(단위/통합/시나리오 테스트)를 즉시 최신 상태로 갱신·추가·동기화**해야 합니다.
   - 테스트케이스를 과거 상태로 방치한 채 구현 코드만 수정하는 행위("깨진 유리창" 방치)를 엄격히 금지하며, 변경된 테스트케이스의 통과 여부를 반드시 실행(`python -m pytest test_case/ -v`)하여 검증합니다.
8. **[Git 브랜치 분기 및 Merge Request(MR) 협업 워크플로우 준수 (필수)]**:
   - `main` 또는 `develop` 브랜치에 직접 커밋/푸시(Direct Push)하는 행위를 엄격히 금지합니다.
   - 모든 개발 작업은 반드시 작업 단위별 별도의 `feature/` 브랜치를 생성하여 독립적으로 진행하며, 개발 및 자체 테스트가 완료된 후 타깃 브랜치(`develop`)로 Merge Request(MR)를 생성하여 코드 리뷰를 거쳐 병합합니다.

---

## [핵심 원칙 1] 프로젝트 아키텍처 및 시스템 일관성 (Project-Wide Consistency)

PawTrail은 **React Native Expo 모바일 앱(Frontend) + FastAPI(Backend) + LangGraph / Gemini Cascading Model Chain(AI) + Local-First AsyncStorage(Privacy Storage) + Supabase Cloud(Auth & Community) + EAS Update & n8n(Automation)** 구조로 구성됩니다. 코드 제안 시 각 계층의 설계 규격을 준수해야 합니다.

### 1. 프론트엔드 (React Native / Expo SDK 51+ / TypeScript / React Native Maps)
- **컴포넌트 설계**: 모바일 네이티브 반응형 뷰포트를 기본으로 하며, 컴포넌트는 단일 책임 원칙(SRP)에 따라 모듈화합니다.
- **노면 및 보행 환경별 표준 색상 규격 (Polyline & Badge)**:
  - **흙/잔디길 (Dirt / Grass - 선호/완만)**: 초록색 (`#10B981`, Green-500)
  - **흙길 (Dirt/Ground - 어스톤)**: 갈색 (`#92400E`, Amber-800)
  - **우레탄/탄성포장 (Rubber/Cushion)**: 주황색 (`#F97316`, Orange-500)
  - **보도블록 (Standard Paved)**: 파란/인디고톤 (`#3B82F6`, Blue-500)
  - **아스팔트 (Asphalt - 경고/기피)**: 짙은 회색 (`#6B7280`, Gray-500)
  - **위험 노면/급경사 (Hazard / Steep Slope / Gravel)**: 빨간색 (`#EF4444`, Red-500)
- **Eyes-Free & Hands-Free 음성 길 안내 엔진**:
  - Android Foreground Service(`expo-location`)를 통한 백그라운드 GPS 위치 추적 (화면 꺼짐 시에도 연속 수집).
  - OSRM `steps[].instruction` 및 링크 노면/경사 속성 결합 `expo-speech` 음성 브리핑 (회전 30m 전 알림, 40m 이상 경로 이탈 시 재탐색 음성 경고).
- **Local-First 프라이버시 영속성 (`AsyncStorage`)**:
  - 반려견 프로필(`@PawTrail:dog_profile`), 실보행 GPS 궤적 및 산책 이력(`@PawTrail:walk_history`, 최근 100회 한도 FIFO)은 서버 DB로 전송하지 않고 기기 내부 로컬 스토리지에만 보관.
  - 기기 변경 및 앱 재설치를 위한 **프로필/산책기록 JSON 로컬 내보내기/가져오기 백업 및 복원 기능** 완비.
- **무선 업데이트 준수**: 1회 Android APK 배포 후 모든 런타임 코드/스타일 수정은 EAS Update(OTA) 파이프라인과 완벽히 호환되도록 네이티브 바이너리 변경을 최소화합니다.

### 2. 백엔드 (FastAPI / Python 3.11)
- **Pydantic V2 기반 엄격한 스키마 검증**: 모든 API 요청/응답은 Pydantic V2 BaseModel을 정의하여 입출력 데이터 무결성을 보장합니다.
- **비동기 안전성**: I/O 바운드 작업(Gemini API 호출, 라우팅 API 통신, 외부 데이터 요청)은 반드시 `async / await`로 구현하며 적절한 타임아웃(Timeout) 및 정제된 `HTTPException` 핸들러를 포함합니다.
- **무상태(Stateless) 아키텍처**: 서버 세션/DB에 대화 상태나 견주 개인정보를 영구 보관하지 않고, 클라이언트가 매 요청 시 단발성 페이로드(`client_dog_context`, `client_recent_feedback`)를 전달받아 처리합니다.
- **경로 생성 응답 규격**: 프론트엔드가 지도에 즉시 그릴 수 있도록 표준 **GeoJSON FeatureCollection** 포맷과 구간별 노면 속성(`surface_type`, `distance_m`, `slope_percent`, `shade_ratio`, `safety_score`)을 포함하여 반환합니다.
- **표준 REST API v1 엔드포인트 규격**:
  | Endpoint | Method | 설명 |
  |---|:---:|---|
  | `/api/v1/walk/plan` | `POST` | 반려견 맞춤형 안심 루프 코스 생성 (10~90분, 무상태 페이로드) |
  | `/api/v1/walk/reroute` | `POST` | 현장 위험 감지 시 3초 이내 대안 우회로 동적 재산출 |
  | `/api/v1/surface/analyze` | `POST` | 현장 노면 이미지 및 시각적 위험 진단 (Gemini Vision) |
  | `/api/v1/walks/inspect-board` | `POST` | 공원 종합안내판 판독 및 반려견 출입 금지구역 파싱 |
  | `/api/v1/thermal/golden-time` | `GET` | 기상청 단기예보 연동 지면열 위험 지수 및 안전 골든타임 |
  | `/api/v1/parking/nearby` | `GET` | 출발 거점 반경 1.5km 이내 공영주차장 P&R 조회 |
  | `/api/v1/community/share` | `POST` | 코스 커뮤니티 공유 (출발지/도착지 200m 공간 마스킹 필수) |
  | `/api/v1/community/feed` | `GET` | 커뮤니티 공개 코스 목록 조회 |

### 3. AI Agent & Vision (LangGraph / Gemini Cascading Model Chain)
- **Gemini 가용 모델 순차 선택 체인 (Cascading Fallback) 강제**:
  - 반드시 `GeminiModelSelector`를 통해 **1순위 `gemini-3.5-flash-lite` ➔ 2순위 `gemini-3.1-flash-lite` ➔ 3순위 `gemini-3.6-flash`** 순으로 자동 선택 호출합니다.
  - 구형 및 단종된 `gemini-1.5` 계열(1.5 Flash, 1.5 Pro) 호출은 전면 배제합니다 (적발 시 즉시 예외 발생).
- **LangGraph State 불변성 & Strict Tool Calling**:
  - State 업데이트 시 새로운 객체로 갱신하며, 도구 함수(`@tool`)에는 명확한 독스트링과 타입 힌트를 부여합니다.
  - 라우팅 좌표 및 실측 데이터에 없는 가상의 경유지/공원을 임의로 지어내는 환각(Hallucination)을 원천 차단합니다.
- **목표 시간 기반 순환 경로(Loop Route) 수렴 프로세스**:
  - 플래너 UI의 10~90분 슬라이더(권장 기본 15~60분) 입력을 수신.
  - 표준 보행 속도 모델(소형견 2.8 km/h, 중형견 3.6 km/h, 대형견 4.2 km/h, 노령견 2.2 km/h) 기반 목표 거리 환산($D = V \times T$).
  - 도출된 순환 코스의 소요 시간이 목표 시간의 **$\pm 15\%$ 오차 이내로 수렴**하도록 웨이포인트를 동적 튜닝하며, 최소 2개 이상의 루프 후보를 도출합니다.
- **Gemini Vision Structured Output**:
  - 현장 위험 및 공원 표지판 분석 시 `response_mime_type="application/json"` 또는 Pydantic 스키마를 강제합니다:
  ```json
  {
    "safety_score": 75,
    "surface_type": "dirt",
    "hazards": ["high_curb", "construction"],
    "curb_height_cm": 25,
    "confidence": 0.88,
    "ai_comment": "25cm 이상의 높은 턱과 공사 장애물이 관찰되어 우회가 권장됩니다."
  }
  ```
- **지면열 위험(Thermal Risk) 독립 모델링**:
  - 기상청 단기예보(기온, 일사량) 연동 수지식($\text{Surface Temp} = \text{Air Temp} + \text{Insolation} \times 15$)을 활용해 아스팔트 위험 지수를 산출하고, 35℃ 이하 안전 산책 골든타임을 안내합니다.

### 4. Database & Storage Architecture (Local-First + Supabase Cloud)
- **Local-First 저장소**: 견주 자택 좌표, 실시간 GPS 궤적, 반려견 프로필 등 민감 개인정보는 서버로 전송하지 않고 사용자 모바일 기기 내부 `AsyncStorage`에만 보관합니다.
- **Supabase Cloud 역할 한정**: 복잡한 서버 DB 대신, 오직 **'커뮤니티 공개 코스(출발지/도착지 200m 마스킹 필수)'**, **'현장 위험 제보(Vision AI 감지 장애물)'**, **'간편 이메일 가입/로그인(Supabase Auth)'**만 가볍게 관리합니다.
- **무상태 피드백 보정 (Stateless Feedback Adaptation)**:
  - 견주가 직전 산책에서 남긴 체감 피드백(예: 경사 불만족)은 서버 DB에 누적하지 않고, 다음 플래너 요청 시 단발성 페이로드로 전송하여 최대 허용 경사도를 1~2% 하향 보정합니다.

---

## [핵심 원칙 2] 노면 비용 모델 및 과학 라우팅 비즈니스 로직 준수

PawTrail의 핵심 가치는 **"사용자 선호 노면 반영, 계단 완전 배제, 완만 경사 및 그늘 우선"**입니다. 라우팅 및 경로 계산 로직 작성 시 아래 수학적 모델을 반드시 준수해야 합니다.

### 1. 가중치 비용 함수 (Cost Function)
보행 네트워크 그래프 $G=(V, E)$에서 링크 $e$의 통행 비용:
$$\text{Cost}(e) = \text{Length}(e) \times W_{\text{base}}(\text{surface}(e)) \times W_{\text{pref}}(\text{surface}(e), \text{SelectedPref}) \times W_{\text{slope}}(e) \times W_{\text{shade}}(e)$$

### 2. 표준 가중치 계수
* **사용자 선택 선호 노면 (흙/잔디)**: **$0.4 \sim 0.5$** (비용 50~60% 할인 적용으로 최우선 경로 탐색)
* **선택되지 않은 중립 포장 노면 (보도블록)**: **$1.0$** (표준 비용)
* **비선호/경고 노면 (아스팔트 - 지면열/딱딱함)**: **$2.5$** (낮 시간/지면열 시 우회 유도 페널티)
* **기피 노면 (자갈/파쇄석 - 발바닥 끼임/상처)**: **$3.5$** (강한 회피 페널티)

### 3. 계단 완전 배제 (Hard Constraint - 필수)
* OSM `highway=steps` 링크는 단순 페널티 부여가 아니라 **후보 보행 네트워크 그래프에서 완전 배제(Inaccessible / 차단)** 처리합니다.

### 4. DEM 고도 기반 경사도 제어
* 경로 세그먼트 표고차/수평거리 삼각함수 기반 종단 경사도(`slope_percent`) 산출.
* 급경사($>8\%$) 링크는 3배 비용 페널티를 부여하여 완만한 경사의 코스를 도출합니다.

### 5. SunCalc 시간대별 그늘 평가
* SunCalc 태양 고도/방위각 및 건물 외곽선 기반 시간대별 그림자 투영 연산.
* 11~15시 피크 시간대에 그늘 비율이 높은 링크에 대해 비용 할인($W_{\text{shade}} = 0.6$)을 적용합니다.

### 6. Candidate Route Scorer (100점 만점 랭킹)
* 도출된 후보 루프 코스들을 다요소 합산 스코어로 평가하여 최적 코스를 선정합니다:
  - 계단 배제 무결성: **30점**
  - 완만 경사 적합도: **30점**
  - 그늘 확보율: **20점**
  - 목표 거리 수렴도: **20점**

### 7. 토지피복(Land Cover) 공간 결합
* 환경공간정보서비스 WMS 및 GeoPandas 레거시를 배제하고, 환경부 세분류 토지피복/OSM 매핑 및 Seed 데이터 우선순위를 적용하여 노면 타입을 투명하게 판별합니다.

---

## [핵심 원칙 3] 모바일 최적화 및 5인 CBT 안정성 보장

1. **[주머니 보관 시 백그라운드 음성 안내 및 GPS 기록 유지]**:
   - Android Foreground Service를 통해 스마트폰 화면이 꺼진 상태에서도 고정밀 GPS 수신 및 `expo-speech` TTS 음성 길 안내를 중단 없이 지속합니다.
   - 일시적 수신 지연이나 도심 GPS 튐이 발생하더라도 칼만 필터 및 도로망 스냅 보정(Dead Reckoning)을 수행하여 거리 및 궤적 손실을 방어합니다.

2. **[실사용자 5인 CBT 시나리오 호환성 (US-H1)]**:
   - Tester 1: 소형견(관절 안심 케어견) ➔ 흙/잔디길 고가중치, 계단 완전 배제 및 핸즈프리 음성 안내 반영
   - Tester 2: 대형견 ➔ 주차장(P&R) 거점 출발 순환 코스 연계
   - Tester 3: 노령견 ➔ 탄성포장/완만 경사(최대 8% 이하) 코스
   - Tester 4: 일반 보행 ➔ 현장 위험(높은 턱/공사) 사진 제보 및 3초 이내 우회 리라우팅
   - Tester 5: 활동견 ➔ n8n 지면열 골든타임 알림 수신 후 완주 및 3초 원터치 피드백
   - 위 5대 필드 테스트 시나리오가 에러 없이 완주될 수 있도록 입력값 예외 처리를 철저히 작성합니다.

3. **[기능 완료 정의 (Definition of Done, DoD)]**:
   코드를 작성했다고 완료된 것이 아니며, 아래 조건을 모두 충족해야 기능이 완료된 것으로 간주합니다:
   - [ ] 실제 서비스 E2E 시나리오에서 정상 동작 확인
   - [ ] Mock이 아닌 실제 API / AsyncStorage / Gemini / Supabase 연동 확인
   - [ ] 유효하지 않은 입력(슬라이더 범위 밖 등) 및 외부 API 타임아웃/오류 방어 확인
   - [ ] 모바일 야외 고대비 시인성 및 한 손 조작(하단 50% Thumb Zone) 확인
   - [ ] 개인정보(Local-First & 200m 공간 지터링) 및 웰니스 카피라이팅 충족
   - [ ] 관련 테스트케이스 100% 통과 (`python -m pytest test_case/ -v`)
   - [ ] 코드 규모 및 복잡도 기준 충족 (단일 파일 250줄 이하, 함수 40줄 이하, 인지 복잡도 10 이하)

---

## [핵심 원칙 4] SonarLint 정적 분석 및 클린 코드 준수

프로젝트에 정의된 클린코드 규칙을 엄격히 준수하여 기술 부채를 방지합니다.

1. **[S3776] 인지 복잡도(Cognitive Complexity) 제한**:
   - 함수당 인지 복잡도는 10 이하를 유지하며, 복잡한 조건문/반복문은 독립된 헬퍼 함수나 커스텀 훅으로 분리합니다.
2. **[S3358] 중첩 삼항 연산자 금지**:
   - 가독성을 해치는 중첩 삼항 연산자(`A ? B : C ? D : E`)는 전면 금지하며, `if-else` 또는 명확한 매핑 객체(`Record<Key, Value>`)로 치환합니다.
3. **[S6582] 옵셔널 체이닝 및 안전한 널 처리**:
   - 객체 탐색 시 옵셔널 체이닝(`?.`)과 널 병합 연산자(`??`)를 사용하여 런타임 `TypeError: Cannot read properties of undefined`를 원천 방어합니다.
4. **[S1128 / S1481] 데드 코드 및 미사용 Import 즉각 제거**:
   - 수정 과정에서 발생한 미사용 변수, 미사용 import, 불필요한 콘솔 로그, 임시 주석은 파일 저장 전 100% 정리합니다.
5. **[조기 반환 (Early Return)]**:
   - 유효성 검사 실패나 에지 케이스는 함수 진입부에서 즉시 반환(Guard Clause)하여 들여쓰기 뎁스를 2단계 이내로 억제합니다.
6. **[코드 규모 및 복잡도 초과 시 선제적 리팩토링 권고 (Refactoring Trigger)]**:
   - **임계치 기준**: 단일 파일 250라인 초과, 단일 함수 40라인 초과, 인지 복잡도 10 초과 시 코드 작성을 멈추고 리팩토링을 선제적으로 권고합니다.
   - **리팩토링 절차**: 거대 파일/컴포넌트 발생 시 Custom Hook 추출, 서브 컴포넌트 분리, 서비스 레이어 이관(`services/`), 매핑 테이블 도입을 제안하고, 리팩토링 후에는 단위 테스트를 실행해 기능 무결성을 입증합니다.

---

## [핵심 원칙 5] 사용자 스토리/Task 변경 시 테스트케이스 동기화 및 전수 검증 (Test Synchronization)

개발 진행 중 기획 구체화, 비즈니스 룰 수정, 사용자 피드백 반영 등으로 인해 **18개 사용자 스토리(US-A1 ~ US-H1)** 또는 **68개 세부 Task**가 변경될 경우, 아래 4단계 절차를 통해 테스트케이스를 반드시 동기화해야 합니다.

1. **[인수 조건(Acceptance Criteria) 연동 갱신]**:
   - 사용자 스토리의 인수 조건이나 완료 정의(DoD)가 수정·추가·삭제되면, 이를 검증하는 테스트 코드(`test_case/`)를 즉각 수정합니다.
2. **[스키마 및 Fixture 동기화]**:
   - Pydantic V2 Request/Response 스키마, DTO, 또는 파라미터 규격이 변경된 경우, 테스트에 사용되는 Mock 데이터와 Fixture를 변경된 스키마에 일치하도록 전수 업데이트합니다.
3. **[회귀(Regression) 방지 전수 테스트 실행]**:
   - 테스트케이스를 갱신한 후에는 `python -m pytest test_case/ -v`를 직접 실행하여 **74개 전체 테스트 스위트가 100% 통과하는지 검증**하고 결과를 보고합니다.
4. **[문서 및 추적표 동기화]**:
   - 코드 및 테스트케이스 수정 후, `docs/03_PawTrail_Agile_User_Stories.md`, `docs/06_PawTrail_Task_Breakdown_and_Estimations.md`, `docs/07_PawTrail_Traceability_Matrix.md`의 완료 상태를 최신 현황과 일치시킵니다.

---

## [핵심 원칙 6] UX 요건 및 웰니스 카피라이팅 가드레일

1. **UX Compact Rules 준수 (`.gemini/UX_COMPACT_RULES.md`)**:
   - 명확한 1차 목적(Clarity), 시각적 위계(Hierarchy), 야외 시인성(Readability in Sunlight), 안전한 터치 타깃(Touch Target >= 48px)을 준수합니다.
2. **예외 상태 처리 전수 구현**:
   - 지도 로딩 중(Skeleton/Spinner), 경로 탐색 실패(대체 경로 제안/반경 확대), 카메라 권한 거부, 네트워크 단절 시의 안내 메시지 및 복구(Retry) 버튼을 반드시 구현합니다.
3. **[앱 전역 긍정적 웰니스 카피라이팅 100% 준수 (Zero Medical Slang)]**:
   - 앱 화면 UI, 온보딩, TTS 음성 안내 스크립트, AI 프롬프트 전역에서 '슬개골 탈구', '관절염', '수술', '질환 단계' 등 임상적/의학적 공포 유발 단어 노출을 엄격히 금지합니다.
   - 발견 즉시 **"폭신한 길"**, **"관절 안심 케어"**, **"부드러운 잔디/흙길"**, **"편안한 발걸음"**으로 순화 통일합니다. (※ 의학 통계 및 질환 메커니즘은 투자 유치/심사용 발표 자료에만 제한적으로 유지)
4. **야외 시인성 보장 고대비 토큰**:
   - 태양광 아래에서 명도 대비 4.5:1 이상(WCAG AA)을 만족하는 `#FAFAFA` (아이보리 저반사 배경) 및 `#1E293B` (고대비 차콜 텍스트)를 사용합니다.

---

## [핵심 원칙 7] 보안, 개인정보 및 AI 안전 가드레일 (Security & Safety)

1. **[Local-First 프라이버시 및 200m 공간 지터링 (Spatial Jittering)]**:
   - 반려견 프로필, 상세 보행 GPS 궤적은 서버로 전송하지 않고 사용자 기기 내부 `AsyncStorage`에만 보관합니다.
   - 커뮤니티 피드에 산책 경로를 공개할 때 견주의 집 주소나 거주지 반경이 노출되지 않도록 **출발지/도착지 반경 200m 공간 절단 및 가우시안 지터링(마스킹)** 처리를 필수로 적용합니다.

2. **[AI 윤리 및 의료 진단 배제 (Medical Disclaimer)]**:
   - 관절 안심 케어 등 반려견 건강 정보는 질병을 진단·치료하는 의료 행위가 아니며, 견주가 입력한 신체 조건을 고려한 **"산책 경로 추천 조건"**으로만 엄격히 제한합니다.
   - 서비스 내 상시 고지 문구를 필수 노출합니다:
     > *"본 서비스의 AI 분석 및 추천은 안전한 산책을 돕기 위한 참고 정보이며 수의학적 진단이 아닙니다. 실제 보행 시 현장 상황에 유의하시기 바랍니다."*

3. **[백엔드 보안 표준]**:
   - Gemini API Key 및 Supabase Service Key 등 민감 인증 정보는 코드에 절대 하드코딩하지 않고 환경변수(`.env`)로 격리 관리합니다.
   - Supabase 커뮤니티 테이블에 Row Level Security(RLS) 및 `auth.uid()` 기반 인가 검증을 적용합니다.
   - 이미지 파일 업로드 시 확장자, MIME 타입, 파일 크기(최대 10MB)를 서버 측에서 엄격히 검증합니다.
   - 예외 발생 시 시스템 내부 스택 트레이스나 Secret이 클라이언트에 노출되지 않도록 정제된 에러 응답(`HTTPException`)을 반환합니다.

---

## [핵심 원칙 8] Git 브랜치 전략 및 Merge Request(MR) 협업 워크플로우

PawTrail 팀의 병렬 개발 생산성과 코드베이스 무결성을 유지하기 위해, 모든 팀원과 AI 도구는 아래의 Git-flow 기반 브랜칭 및 Merge Request(MR) 협업 절차를 엄격히 준수해야 합니다.

### 1. 기본 브랜치 운영 원칙
- **`main`**: 프로덕션 배포용 기준 브랜치 (태깅 및 릴리스 전용, 상시 배포 가능한 무결성 유지).
- **`develop`**: 스프린트 개발 통합 브랜치 (모든 기능 브랜치가 통합·검증되는 기준선).
- **`main` 및 `develop` 직접 푸시(Direct Push) 절대 금지**: 모든 변경사항은 반드시 Merge Request(MR / PR)를 통해서만 병합됩니다.

### 2. feature 브랜치 생성 및 작업 규칙
- **분기 기준점**: 항상 최신 `develop` 브랜치(`git checkout develop && git pull origin develop`)로부터 분기합니다.
- **브랜치 명명 규칙 (Branch Naming Convention)**:
  - **신규 기능 개발**: `feature/{member}-{task-id}` 또는 `feature/{story-id}-{feature-name}`  
    *예시: `feature/member-a-us-a1-agent`, `feature/member-c-us-b1-steps`, `feature/us-a3-target-duration`*
  - **결함/버그 수정**: `fix/{issue-id}-{issue-summary}`  
    *예시: `fix/gps-drift-dead-reckoning`, `fix/screen-off-foreground-service`*
  - **리팩토링 / 성능 개선**: `refactor/{target-module}`  
    *예시: `refactor/surface-cost-service`, `refactor/route-candidate-scorer`*
  - **문서화 / 산출물 동기화**: `docs/{doc-name}`  
    *예시: `docs/traceability-matrix-update`, `docs/presentation-strategy`*
- **작업 범위 격리**: 단일 feature 브랜치에서는 할당된 단일 Task 또는 단일 User Story에 해당하는 작업만 수행하며, 관련 없는 타 모듈의 변경을 혼합하지 않습니다.

### 3. 개발 완료 후 Merge Request (MR) 생성 및 리뷰 절차
1. **[사전 로컬 검증 (Pre-MR Checklist)]**:
   - 로컬 단위/통합 테스트 100% 통과 확인 (`python -m pytest test_case/ -v`, 74 passed 확인).
   - SonarLint 정적 분석 규칙 준수 (단일 파일 250라인 이하, 인지 복잡도 10 이하, 미사용 코드 제거).
   - 사용자 스토리 인수 조건(AC) 및 완료 정의(DoD) 100% 충족 확인.
2. **[Merge Request 필수 작성 항목]**:
   - **MR 제목**: `[Type] 연계 ID: 명확한 작업 요약` (예: `[Feature] US-A3: 산책 시간 기반 맞춤형 루프 코스 생성 및 테스트 통과`)
   - **관련 이슈 / 스토리**: `Closes #US-A3` 또는 `Relates to TASK-A3-1`
   - **주요 변경 사항 (What & Why)**: 신규 기능, 변경된 알고리즘, 수정된 API 스키마 요약
   - **검증 결과 (Test Evidence)**: 단위/통합 테스트 실행 결과 첨부 (예: `74 passed in 0.19s`)
   - **리뷰어 확인 요청 사항 (Review Notes)**: 특별히 주의 깊게 봐주어야 할 부분이나 파라미터 튜닝 내역
3. **[코드 리뷰 및 병합 (Review & Merge)]**:
   - 최소 1인 이상의 동료 개발자(Peer Reviewer) 리뷰 및 승인(Approval) 획득 후 병합.
   - MR 병합 완료 후 로컬 및 원격의 `feature` 브랜치는 즉시 삭제하여 브랜치 청결도를 유지.

---

## [핵심 원칙 9] 5인 역할별 AI Pair Programming 자동 점검 시스템 (docs/checklist/ 전수 강제)

코드를 생성/수정/리팩토링할 때, 팀원이 수동으로 확인하지 않아도 AI가 작업 대상 파일 경로에 맞춰 [`docs/checklist/`](file:///d:/코디세이/PawTrail/docs/checklist/) 및 [`.agents/rules/ai_pair_programming_rules.md`](file:///d:/코디세이/PawTrail/.agents/rules/ai_pair_programming_rules.md)의 점검 항목을 **사전/사후에 자동으로 전수 검증**합니다:

```
+-------------------------------------------------------------------------------------------------+
|                                 작업 대상 파일/모듈 자동 식별                                     |
+-------------------------------------------------------------------------------------------------+
        |                        |                     |                     |                  |
[Member A: AI Agent]    [Member B: Vision/GIS]   [Member C: Backend]  [Member D: Mobile]  [Member E: UX/Design]
 • LangGraph ReAct       • Gemini 모델 3단계      • FastAPI Stateless  • React Native       • 웰니스 카피라이팅
 • 무상태 프롬프트 주입     • Structured JSON        • OSM 계단 배제 라우팅 • 백그라운드 GPS/TTS • 고대비 시인성 토큰
 • Pydantic V2 Strict    • 200m 공간 지터링       • 클린코드 임계치 엄수 • Local-First 저장  • 6대 화면 시나리오
```

- **[Member A: PM & AI Agent Lead]** (`agent/`, `prompts/`, `orchestrator/`, `scorer/`):
  - 무상태(Stateless) 프롬프트 원칙: 서버 DB 대화 히스토리 없이 클라이언트 페이로드(`client_dog_context`, `client_recent_feedback`)만 주입
  - Pydantic V2 Strict 검증: 10~90분 슬라이더 범위, 4대 엔티티 검증
  - Candidate Route Scorer: 100점 만점 랭킹 알고리즘 및 추천 사유 브리핑
- **[Member B: AI & Spatial Data Engineer]** (`vision/`, `spatial/`, `models/`, `pipeline/`):
  - `GeminiModelSelector` 순차 체인 (`gemini-3.5-flash-lite` ➔ `gemini-3.1-flash-lite` ➔ `gemini-3.6-flash`, 1.5 전면 배제)
  - Structured JSON 출력 스키마 고정 및 공원 안내판(`ParkBoardInspector`) 반려견 금지구역 판독
  - DEM 경사도 연산 및 200m 공간 가우시안 지터링(Jittering)
- **[Member C: Backend & Spatial Routing Lead]** (`backend/`, `api/`, `routing/`, `db/`):
  - OSM 계단(`highway=steps`) 후보 네트워크 완전 배제 (Hard Constraint)
  - 3초 이내 현장 위험 우회 동적 재탐색 API (`POST /api/v1/walk/reroute`)
  - FastAPI 클린코드 임계치 엄수 (250줄 / 40줄 / 인지 복잡도 10 이하)
- **[Member D: Frontend & Mobile App Lead]** (`frontend/`, `mobile/`, `screens/`, `components/`):
  - Android Foreground Service + `expo-speech` 백그라운드 GPS 및 음성 안내 무중단 실행
  - Polyline 노면별 색상 분기 렌더링 및 `React.memo` 리렌더링 최적화
  - Local-First `AsyncStorage` 영속화 및 JSON 백업/복원
  - EAS Build 1회 배포 및 EAS Update 무선 OTA 호환성 유지
- **[Member E: UI/UX Designer & Product Experience Lead]** (`styles/`, `theme/`, `assets/`, `text/`, `copy/`):
  - 긍정적 웰니스 카피라이팅 100% 준수 (임상 질병 단어 0건)
  - 야외 고대비 시인성 토큰 (`#FAFAFA`, `#1E293B`) 및 하단 50% Thumb Zone 배치
  - 5인 실사용자 필드 테스트(CBT) 시나리오 검증 및 피드백 튜닝 총괄

---

## [Gemini 실행 가이드라인] 코드 제안 시 7단계 필수 검증

Gemini는 코드를 제안하거나 수정할 때 다음 7단계를 내부적으로 검증한 후 답변을 출력합니다:

1. **[목적 검증]**: 이 코드가 PawTrail의 18개 핵심 사용자 스토리(**US-A1 ~ US-H1**) 및 68개 Task 명세와 완벽히 부합하며, 불필요한 오버엔지니어링(YAGNI)을 배제했는가?
2. **[아키텍처 검증]**: React Native Expo(TypeScript) / FastAPI REST v1 / LangGraph Agent / Local-First AsyncStorage / Supabase Cloud 규격 및 노면 가중치 비용 공식과 일치하는가?
3. **[AI 모델 체인 검증]**: `GeminiModelSelector` 가용 모델 체인(3.5 Flash-Lite ➔ 3.1 Flash-Lite ➔ 3.6 Flash)을 준수하고 구형 1.5 계열을 100% 배제했는가?
4. **[품질/안정성/복잡도 검증]**: SonarLint 규칙(단일 파일 250라인 이하, 함수 40라인 이하, 인지 복잡도 10 이하, 중첩 삼항연산 금지, 미사용 코드 제거)을 통과했는가? 초과 시 선제적 리팩토링을 권고했는가?
5. **[테스트 동기화 검증 (필수)]**: 사용자 스토리나 Task의 변경사항이 테스트케이스(`test_case/`)에 빠짐없이 반영되었으며, `python -m pytest test_case/ -v` 실행 시 74개 테스트가 100% 통과하는가?
6. **[사용자 경험 및 웰니스 검증]**: 로딩, 에러, 빈 상태가 처리되었고, 노면 색상 규격과 음성 길 안내 등 야외 실사용성이 충족되었으며 '슬개골 탈구' 등 임상 질병 용어가 100% 배제되었는가?
7. **[보안 및 협업 검증]**: 자택 위치가 로컬에만 보관되고 커뮤니티 공유 시 200m 공간 지터링이 적용되었으며, 작업 내용이 독립된 feature 브랜치 단위로 격리되어 있는가?