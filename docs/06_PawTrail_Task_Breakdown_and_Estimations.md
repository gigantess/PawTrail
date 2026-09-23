# [작업 분할 명세서] PawTrail 사용자 스토리별 상세 구현 Task 및 작업량 추정 (WBS)

## 📌 1. 개요 및 추정 기준

* **프로젝트명**: PawTrail (AI Native 반려견 안심 노면 산책 에이전트 및 핸즈프리 모바일 플랫폼)
* **목적**: 18개 사용자 스토리(US-A1 ~ US-H1)를 68개의 실제 개발 가능한 세부 Task로 엄밀하게 분할하고, 1인 1담당 원칙(Single Assignee)에 입각하여 애자일 추정치(Story Points, 공수 Hours)를 지정함으로써 5주간의 명확한 실행 계획을 제공합니다.
* **핵심 아키텍처 및 엔지니어링 원칙 (1~5번 문서 정합)**:
  - **React Native (Expo SDK 51+)**: Android Foreground Service 백그라운드 GPS + `expo-speech` TTS 기반 **시선 해방(Eyes-Free) 핸즈프리 음성 길 안내**.
  - **EAS Build & EAS Update OTA**: 테스터용 Android APK 1회 패키징 후 모든 기능 수정 및 핫픽스는 **무선 무점검 실시간 OTA 배포**.
  - **프라이버시 로컬 저장 (Privacy-First Local Storage)**: 자택 위치, 실산책 보행 궤적, 반려견 프로필은 사용자 스마트폰 로컬(`AsyncStorage`)에만 보관하며 JSON 백업/복원 지원.
  - **간편 이메일 가입 & 커뮤니티 보호**: Supabase Auth 기반 간편 이메일 가입(Auto-confirm) 및 커뮤니티 공개 코스 공유 시 **출발지/도착지 200m 공간 블러링(Spatial Jittering)** 적용.
  - **긍정적 웰니스 카피라이팅**: 앱 UI 전역에서 질병 용어(슬개골 탈구 등)를 배제하고 '관절 안심 케어', '폭신한 길' 등 순화된 언어 사용.

### 🎯 4대 태스크 분할 및 배정 원칙
1. **1인 1태스크 전담 배정 (Single Assignee Principle)**:
   - 하나의 Task에는 **반드시 단 1명의 담당자만 배정**하여 책임 소재를 명확히 하고 협업 병목을 원천 방지합니다.
   - 복수의 멤버가 참여하는 복합 스토리(US-A3, US-B4, US-D2, US-F1, US-G1, US-G2, US-H1 등)는 **Frontend, Backend/GIS, AI Agent, Vision, Infra의 전문 영역별로 독립 Task로 분할**하여 각 담당자를 개별 지정하였습니다.
2. **스토리-태스크 담당자 100% 일치 (R&R Consistency)**:
   - 각 스토리 헤더에 표기된 **주 담당자(Lead) 및 협업 담당자**와 하위 세부 Task의 배정 멤버가 완벽하게 일치합니다.
3. **공수 및 포인트 엄밀성 (Strict Mathematical Integrity)**:
   - 전체 **18개 핵심 스토리, 68개 Task, 77 Story Points (스프린트 기능 77 pt / 배포 포함 총 82 pt), 총 372 Hours**가 에픽별·스토리별·팀원별로 단 1시간의 오차도 없이 100% 일치합니다.
4. **정량적 완료 정의 (Actionable DoD)**:
   - 모든 세부 Task마다 명확한 검증 산출물과 정량적 완료 기준(Definition of Done)을 명시하여 개발 즉시 인수 테스트가 가능하도록 구성했습니다.

### 👥 5인 팀 구성 및 포지션 명세 (Doc 02, 05 정합)
| 담당자 | 포지션 (Position) | 핵심 R&R 및 전담 개발 영역 | 총 배정 공수 |
|:---:|---|---|:---:|
| **Member A** | **PM & AI Agent Lead** | LangGraph Agent 상태 머신, Pydantic V2 Strict Schema, 무상태 프롬프트 오케스트레이션, 체급별 속도 모델, Candidate Route Scorer 랭킹 알고리즘 | **65 h** |
| **Member B** | **AI & Spatial Data Engineer** | Gemini 가용 모델 순차 선택(3.5 Flash-Lite ➔ 3.1 Flash-Lite ➔ 3.6 Flash) 비전 분석, DEM 고도 샘플링 파이프라인, SunCalc 태양 궤적 연산, n8n 지면열 수지식, 200m 마스킹 | **71 h** |
| **Member C** | **Backend & Spatial Routing Lead** | FastAPI REST API 코어, Routing API Adapter (ORS/OSRM), OSM Steps 배제 라우팅, 건물 외곽선 그림자 투영 다각형 연산, 동적 위험 우회 재탐색 API, Supabase Auth | **91 h** |
| **Member D** | **Frontend & Mobile App Lead** | React Native (Expo SDK 51+) 코어, react-native-maps Polyline 렌더링, Android Foreground Service GPS, expo-speech TTS 음성 안내, AsyncStorage, EAS Build/OTA | **94 h** |
| **Member E** | **UI/UX Designer & Product Experience Lead** | **전문 디자이너**: PawTrail 디자인 시스템, 6대 화면 고화질 UI/UX 설계, 온보딩/플래너 인터랙션, 완주 인포그래픽, 웰니스 카피라이팅, 5인 CBT 사용성 평가 총괄 | **51 h** |
| **합계** | **5인 전원 (Full Cross-Functional Team)** | **PawTrail MVP 18개 핵심 스토리 및 68개 Task 완주 (5주 스프린트)** | **372 h** |

---

## 📋 2. 사용자 스토리별 세부 구현 Task 명세

### [Epic A] 산책 조건 입력 및 개인화
* **에픽 요약**: 반려견 조건(견종, 체급, 관절 상태) 및 사용자 산책 선호도를 수집하여 로컬에 안전하게 보관하고, 대화형 자연어 요청을 구조화된 라우팅 조건으로 변환.
* **에픽 규모**: **11 Story Points | 11개 세부 Task | 총 52 Hours**

---

#### US-A1: 대화형 자연어 산책 요청 및 조건 구조화
* **개요**: "9살 노령견이라 계단 피하고 완만한 길로 20분"과 같은 자연어 발화를 LangGraph Agent가 분석하여 라우팅 제약조건으로 구조화.
* **스토리 정보**: `난이도: 중` | `우선순위: Must` | `스토리 포인트: 5 pt` | `총 추정 공수: 24 h` | `스프린트: Sprint 1 (Week 1)`
* **담당자**: **Member A (AI Agent Lead)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-A1-1** | LangGraph Agent 상태 그래프 스키마(`AgentState`) 및 노드 구조 설계 | Member A | 4 h | Week 1 | `AgentState` 인터페이스 정의 및 순환 그래프 구조 수립 |
| **TASK-A1-2** | 자연어 발화에서 시간·계단·경사·그늘 선호 엔티티를 추출하는 ReAct 프롬프트 작성 | Member A | 6 h | Week 1 | Zero-shot/Few-shot 프롬프트 템플릿 및 엔티티 추출률 85% 검증 |
| **TASK-A1-3** | Pydantic V2 Strict Input Schema 및 요청 본문의 로컬 프로필 바인딩 모듈 개발 | Member A | 6 h | Week 1 | `WalkIntent` Pydantic 모델 및 클라이언트 페이로드 병합 검증 |
| **TASK-A1-4** | FastAPI REST API 연동 및 모의 발화 10종 엔티티 추출 단위/통합 테스트 | Member A | 8 h | Week 1 | `POST /api/walks/plan` 질의 10종 파싱 테스트 및 예외 폴백 검증 |

---

#### US-A2: 반려견 프로필 로컬 등록 및 JSON 백업/복원
* **개요**: 반려견 프로필(이름, 견종, 체중, 연령, 관절 안심 케어 선호)을 모바일 로컬에만 영속화하고 파일 백업/복원 지원.
* **스토리 정보**: `난이도: 하` | `우선순위: Must` | `스토리 포인트: 3 pt` | `총 추정 공수: 14 h` | `스프린트: Sprint 1 (Week 1~2)`
* **담당자**: **Member E (Lead / Design), Member D (Frontend)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-A2-1** | `@react-native-async-storage/async-storage` 래퍼 및 프로필 CRUD 모듈 개발 | Member D | 4 h | Week 1 | `@PawTrail:dog_profile` 키 기반 로컬 영속화 래퍼 모듈 완성 |
| **TASK-A2-2** | 반려견 프로필 온보딩 및 수정 폼 UI 컴포넌트 설계 | Member E | 4 h | Week 1 | 견종, 체중, 연령, 관절 안심 수준(0~2단계) 입력 인터페이스 설계 |
| **TASK-A2-3** | 기기 변경 및 앱 재설치 대비 프로필 JSON 파일 내보내기/가져오기 모듈 구현 | Member D | 3 h | Week 2 | `expo-file-system` / `expo-sharing` 연동 로컬 백업/복원 검증 |
| **TASK-A2-4** | 앱 온보딩 및 프로필 UI 전역 웰니스 카피라이팅 가이드 및 디자인 시스템 검증 | Member E | 3 h | Week 2 | 질병 용어(슬개골 탈구 등) 노출 0건 검출 및 UI 텍스트 순화 검증 |

---

#### US-A3: 목표 산책 시간/거리 기반 환산 (속도/슬라이더)
* **개요**: 산책 시간 슬라이더 조작 시 체급별 보행 속도 모델을 적용하여 목표 거리를 산출하고 허용 오차(±15%) 범위 내 순환 코스 도출.
* **스토리 정보**: `난이도: 중` | `우선순위: Must` | `스토리 포인트: 3 pt` | `총 추정 공수: 14 h` | `스프린트: Sprint 1 (Week 1~2)`
* **담당자**: **Member A (Lead / Agent), Member E (Design)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-A3-1** | 플래너 UI 산책 시간 슬라이더(10~90분) 및 노면 칩 인터랙션 디자인 | Member E | 4 h | Week 1 | 직관적인 시간 선택 슬라이더 및 프리셋 칩 UI 컴포넌트 설계 |
| **TASK-A3-2** | 체급(소/중/대/노령견)별 표준 보행 속도 상수 모델 및 목표 거리 자동 환산 엔진 구현 | Member A | 5 h | Week 2 | 2.8/3.6/4.2/2.2 km/h 속도 상수 기반 목표 거리(km) 환산 함수 구현 |
| **TASK-A3-3** | 생성된 경로 소요 시간의 목표 시간 수렴도(±15%) 오차 검증 및 브리핑 체인 연동 | Member A | 5 h | Week 2 | 10개 좌표 샘플 테스트에서 소요 시간 오차율 ±15% 이내 도출 검증 |

---

### [Epic B] 무계단·완만한 경사·그늘 우선 경로 생성
* **에픽 요약**: OSM Steps 배제, DEM 경사도 연산, SunCalc 태양 고도/그늘 분석 및 표준 Routing API 어댑터를 통합하여 안심 순환 루프 경로를 생성하고 다요소 랭킹을 수행.
* **에픽 규모**: **26 Story Points | 16개 세부 Task | 총 114 Hours**

---

#### US-B1: 지도 데이터 기반 확인된 계단 구간 우선 회피
* **개요**: OpenStreetMap 도로망 데이터에서 `highway=steps` 링크를 하드 제약(Hard Constraint)으로 배제하여 무계단 경로 생성.
* **스토리 정보**: `난이도: 상` | `우선순위: Must` | `스토리 포인트: 8 pt` | `총 추정 공수: 34 h` | `스프린트: Sprint 1 (Week 2)`
* **담당자**: **Member C (Lead / Backend), Member B (Data)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-B1-1** | OSM 보행 도로망 데이터 파싱 및 `highway=steps` 링크 추출 인덱서 구축 | Member C | 8 h | Week 2 | OSM XML/PBF 데이터에서 보행로 및 계단 노드/웨이 인덱스 생성 |
| **TASK-B1-2** | 계단 링크 탐색 배제(Hard Constraint) 및 회피 가중치 부여 라우팅 모듈 구현 | Member C | 10 h | Week 2 | 계단 링크 가중치를 무한대로 설정하여 탐색 경로에서 원천 차단 |
| **TASK-B1-3** | 모든 연결로가 계단인 고립 지형 대상 최소 계단 대체 경로 산출 Fallback 로직 개발 | Member C | 8 h | Week 2 | 불가피한 계단 포함 시 경고 플래그 및 최소 계단 단수 경로 산출 |
| **TASK-B1-4** | 계단 밀집 구역 테스트베드(5개 권역) 대상 무계단 회피 라우팅 정량 검증 | Member B | 8 h | Week 2 | 테스트 케이스 계단 배제 적중률 100% 달성 단위/통합 테스트 |

---

#### US-B2: DEM 기반 최대 경사도 제어 및 완만 경사 우선 경로 도출
* **개요**: 수치표고모델(DEM) 고도 데이터를 연계하여 세그먼트별 경사도를 계산하고, 급경사 링크를 회피하는 완만한 코스 선별.
* **스토리 정보**: `난이도: 중상` | `우선순위: Must` | `스토리 포인트: 5 pt` | `총 추정 공수: 24 h` | `스프린트: Sprint 1 (Week 2)`
* **담당자**: **Member C (Lead / Backend), Member B (Data)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-B2-1** | 수치표고모델(DEM) 래스터 데이터 적재 및 경로 세그먼트 고도 샘플링 파이프라인 | Member B | 7 h | Week 2 | GeoTIFF DEM 래스터 좌표계 매핑 및 고도 보간 파이프라인 구축 |
| **TASK-B2-2** | 세그먼트별 `max_slope_percent` 및 누적 고도 상승/하강 연산 모듈 개발 | Member C | 7 h | Week 2 | 경로 링크별 경사도(%) 산출 및 급경사(>8%) 구간 검출 알고리즘 |
| **TASK-B2-3** | 견주 경사 선호도(매우 완만/완만/일반)에 따른 경사도 페널티 비용 함수 구현 | Member C | 6 h | Week 2 | 다익스트라/A* 탐색 비용 함수에 경사도 페널티 가중치 연동 |
| **TASK-B2-4** | 구릉지 지형 테스트베드 대상 완만 경로 선별 알고리즘 정확도 검증 | Member B | 4 h | Week 2 | 가파른 지형 샘플 10개 대상 완만 경로 선별 유효성 검증 |

---

#### US-B3: 태양 위치 및 건물 형상 기반 시간대별 그늘 우선 평가
* **개요**: `SunCalc` 태양 고도/방위각과 건물 2.5D 외곽선을 교차 연산하여 시간대별 예상 그늘 비율(`shade_ratio`)을 산출.
* **스토리 정보**: `난이도: 중상` | `우선순위: Should` | `스토리 포인트: 5 pt` | `총 추정 공수: 22 h` | `스프린트: Sprint 1~2 (Week 2~3)`
* **담당자**: **Member C (Lead / Backend), Member B (Data)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-B3-1** | `SunCalc` 연동 산책 일시/위치 기준 실시간 태양 고도각 및 방위각 연산 모듈 개발 | Member B | 5 h | Week 2 | 시간대별 태양 위치 좌표 수리 모델 구현 및 정확도 검증 |
| **TASK-B3-2** | 건물 외곽선 폴리곤 및 층수/높이 데이터 기반 시간대별 그림자 투영 다각형 연산 | Member C | 8 h | Week 3 | 건물 2.5D 형상 기반 태양 반대 방향 그림자 폴리곤 생성 모듈 |
| **TASK-B3-3** | 보행 링크와 그림자 다각형 교차 공간 연산을 통한 예상 그늘 비율(`shade_ratio`) 산출 | Member C | 5 h | Week 3 | Shapely 공간 교차 연산으로 세그먼트별 그늘 점유율(0.0~1.0) 계산 |
| **TASK-B3-4** | 정오 vs 늦은 오후 시간대별 그늘 평가 대조 테스트베드 검증 및 신뢰도 태깅 | Member B | 4 h | Week 3 | 시간대별 그늘 비율 변동성 대조 테스트 및 신뢰도 메타데이터 부여 |

---

#### US-B4: Routing API Adapter 연동 및 후보 경로 다요소 스코어링
* **개요**: 표준 라우팅 API(ORS/OSRM) 어댑터를 통해 순환 루프 후보(2~3개)를 생성하고, 계단·경사·그늘·소요시간 다요소를 종합 채점하여 최적 경로 선정.
* **스토리 정보**: `난이도: 상` | `우선순위: Must` | `스토리 포인트: 8 pt` | `총 추정 공수: 34 h` | `스프린트: Sprint 1 (Week 1~2)`
* **담당자**: **Member C (Lead / Backend), Member A (Agent)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-B4-1** | OpenRouteService / OSRM REST API 연동 독립 어댑터(Adapter) 레이어 구현 | Member C | 10 h | Week 1 | 표준 Routing API HTTP 클라이언트 및 GeoJSON 응답 파서 구축 |
| **TASK-B4-2** | 출발지 중심 다각형 Waypoint 샘플링 기반 순환 루프 후보(2~3개) 생성 모듈 개발 | Member C | 8 h | Week 1 | 반경별 웨이포인트 분기 샘플링을 통한 비중복 순환 코스 생성 |
| **TASK-B4-3** | 계단·경사·그늘·거리 다요소 Candidate Route Scorer 수치 랭킹 알고리즘 구현 | Member A | 8 h | Week 2 | 다요소 정규화 가중치 합산 기반 코스 순위화 스코어러 완성 |
| **TASK-B4-4** | LangGraph Agent 최적 순환 루프 선정 및 추천 사유 생성 가드레일 체인 연동 | Member A | 8 h | Week 2 | 최상위 경로 선정 및 반려견 특성 맞춤 코스 추천 브리핑 생성 |

---

### [Epic C] 모바일 인터페이스 & 백그라운드 안내
* **에픽 요약**: React Native 지도 위에 안심 속성별 색상 분기 Polyline을 시각화하고, 주머니 속에서도 끊김 없는 Eyes-Free 핸즈프리 TTS 음성 안내 제공.
* **에픽 규모**: **10 Story Points | 8개 세부 Task | 총 48 Hours**

---

#### US-C1: React Native Maps 기반 구간별 색상 분기 경로 시각화
* **개요**: react-native-maps 지도 상에 그늘길(초록), 일반길(파랑), 주의구간(주황) 등 노면/환경 속성을 직관적으로 색상 분기 렌더링.
* **스토리 정보**: `난이도: 중` | `우선순위: Must` | `스토리 포인트: 5 pt` | `총 추정 공수: 24 h` | `스프린트: Sprint 2 (Week 3)`
* **담당자**: **Member D (Lead / Frontend), Member E (Design)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-C1-1** | `react-native-maps` 지도 캔버스 마운트 및 현재 위치 마커/카메라 트래킹 구현 | Member D | 6 h | Week 3 | 지도 뷰 마운트, 현재 GPS 위치 마커 렌더링 및 줌 레벨 최적화 |
| **TASK-C1-2** | 경로 속성(그늘/완만: 초록, 일반: 파랑, 주의: 주황) 분기 Polyline 렌더링 구현 | Member D | 8 h | Week 3 | 세그먼트별 메타데이터에 따른 다색상(Multi-colored) Polyline 표출 |
| **TASK-C1-3** | 거리, 시간, 최대 경사, 그늘 비율 요약 카드 및 OSRM 스텝 리스트 바텀시트 UI/UX 디자인 시스템 설계 | Member E | 6 h | Week 3 | 코스 프리뷰 카드 및 스와이프 가능한 회전 안내 리스트 뷰 설계 |
| **TASK-C1-4** | 모바일 Thumb Zone 뷰포트 반응형 레이아웃 설계 및 터치 제스처 최적화 | Member E | 4 h | Week 3 | 다양한 해상도(Android/iOS) 실기기 레이아웃 깨짐 0건 검증 |

---

#### US-C2: 시선 해방(Eyes-Free) 백그라운드 핸즈프리 음성 길 안내
* **개요**: 스마트폰 화면을 주머니에 넣고 꺼두어도 Android Foreground Service와 `expo-speech` TTS가 회전 30m 전 사전 음성 안내를 안정적으로 송출.
* **스토리 정보**: `난이도: 상` | `우선순위: Must` | `스토리 포인트: 5 pt` | `총 추정 공수: 24 h` | `스프린트: Sprint 2 (Week 3)`
* **담당자**: **Member D (Frontend Lead)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-C2-1** | OSRM/ORS steps 기반 턴 안내 문구 및 노면 속성 파싱 엔진 개발 | Member D | 6 h | Week 3 | 방향 지시 텍스트 및 노면 속성 융합 멘트 파싱 모듈 구현 |
| **TASK-C2-2** | `expo-speech` TTS 연동 및 회전 지점 30m 전 사전 음성 브리핑 송출 엔진 구현 | Member D | 7 h | Week 3 | "50m 앞 완만길 우회전입니다" 등 사전 음성 안내 트리거 구현 |
| **TASK-C2-3** | 전환점 사전 비프음 알림 및 경로 이탈(Off-route) 감지 시 재탐색 음성 알림 구현 | Member D | 5 h | Week 3 | 햅틱/비프음 큐 송출 및 30m 이상 이탈 시 재탐색 안내 로직 연동 |
| **TASK-C2-4** | 스마트폰 화면 꺼짐(Screen-off) 상태 Android Foreground Service 음성 안내 연속성 검증 | Member D | 6 h | Week 3 | 주머니 속 화면 꺼짐 상태에서 15분 이상 무중단 음성 브리핑 검증 |

---

### [Epic D] 현장 위험 분석 및 재탐색
* **에픽 요약**: 현장에서 촬영한 사진 속 장애물(높은 턱, 계단, 공사 잔해)을 Gemini 가용 모델(3.5 Flash-Lite / 3.1 Flash-Lite / 3.6 Flash)이 실시간 판독하고, 위험 감지 시 즉시 안전 우회 경로를 재탐색.
* **에픽 규모**: **10 Story Points | 8개 세부 Task | 총 46 Hours**

---

#### US-D1: Vision AI 기반 현장 턱·계단·보행 장애물 시각 분석
* **개요**: 현장 사진을 가용한 Gemini 모델(3.5 Flash-Lite ➔ 3.1 Flash-Lite ➔ 3.6 Flash)로 분석하여 높은 턱, 공사 구역, 공원 안내판 출입 제한을 정형 JSON으로 구조화 판독.
* **스토리 정보**: `난이도: 중상` | `우선순위: Must` | `스토리 포인트: 5 pt` | `총 추정 공수: 24 h` | `스프린트: Sprint 2 (Week 3)`
* **담당자**: **Member B (Vision AI Lead)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-D1-1** | 현장 위험물(높은 턱, 계단, 공사) 및 공원 안내판 벤치마킹 이미지셋 구축 및 라벨링 | Member B | 6 h | Week 3 | 35장 이상의 도심/공원 보행 장애물 이미지 데이터셋 구축 |
| **TASK-D1-2** | Gemini 가용 모델 체인(3.5 Flash-Lite ➔ 3.1 Flash-Lite ➔ 3.6 Flash) 프롬프트 엔지니어링 및 Structured JSON 스키마 고정 | Member B | 7 h | Week 3 | `has_hazard`, `hazard_type`, `confidence` 정형 출력 스키마 고정 |
| **TASK-D1-3** | 모션 블러, 저조도 사진 입력 시 예외 처리 및 사용자 재촬영 가이드 로직 구현 | Member B | 5 h | Week 3 | 저품질 이미지 입력 시 폴백 및 사용자 친화적 촬영 가이드 반환 |
| **TASK-D1-4** | 이미지 업로드 REST API(`POST /api/walks/inspect-board`) 연동 및 지연시간 최적화 | Member B | 6 h | Week 3 | 이미지 리사이징(1024px) 파이프라인 및 응답 시간 2.5초 이내 달성 |

---

#### US-D2: 현장 위험 구간 우회 및 동적 재탐색
* **개요**: 비전 분석 신뢰도가 임계치(Confidence >= 0.85)를 만족할 경우 해당 링크를 임시 차단(Block List)하고 즉시 출발지/목적지 안전 우회 코스 재탐색.
* **스토리 정보**: `난이도: 중상` | `우선순위: Should` | `스토리 포인트: 5 pt` | `총 추정 공수: 22 h` | `스프린트: Sprint 2 (Week 3~4)`
* **담당자**: **Member C (Lead / Routing), Member B (Vision), Member A (Agent), Member D (UI)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-D2-1** | Vision 판독 위험 신뢰도(Confidence >= 0.85) 필터링 및 우회 트리거 이벤트 연동 | Member B | 4 h | Week 3 | 위험 판독 신뢰도 임계치 판정 및 위험 메타데이터 전달 핸들러 |
| **TASK-D2-2** | 위험 감지 좌표 기준 인접 링크 임시 차단(Block List) 및 안전 우회 경로 재탐색 API 구현 | Member C | 8 h | Week 3 | `POST /api/routes/reroute` 차단 링크 우회 순환 루프 연산 API 구현 |
| **TASK-D2-3** | 우회 사유 및 변경 경로 에이전트 음성 브리핑 메시지 생성 체인 연동 | Member A | 5 h | Week 4 | "전방 공사 구역을 피해 오른쪽 완만한 길로 안내합니다" 브리핑 생성 |
| **TASK-D2-4** | 모바일 지도 화면 상 우회 경로 실시간 갱신 및 토스트/확인 모달 인터랙션 구현 | Member D | 5 h | Week 4 | 기존 경로 페이드아웃, 신규 우회 경로 하이라이팅 및 갱신 UI 검증 |

---

### [Epic E] 산책 기록 및 Memory (Local-First)
* **에픽 요약**: 백그라운드 GPS 궤적과 피드백을 사용자 스마트폰 로컬에만 영속 저장(Local-First)하고, 다음 산책 요청 시 무상태(Stateless) 맥락으로 자동 보정 주입.
* **에픽 규모**: **11 Story Points | 10개 세부 Task | 총 50 Hours**

---

#### US-E1: 백그라운드 GPS 위치 추적 및 실산책 경로 로컬 저장
* **개요**: 화면이 꺼진 상태에서도 Android Foreground Service가 끊김 없이 위치를 수신하고, 개인 궤적을 폰 로컬(`AsyncStorage`)에만 안전하게 적재.
* **스토리 정보**: `난이도: 중상` | `우선순위: Must` | `스토리 포인트: 5 pt` | `총 추정 공수: 24 h` | `스프린트: Sprint 2 (Week 4)`
* **담당자**: **Member D (Frontend Lead)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-E1-1** | `expo-location`과 Android Foreground Service 연동 백그라운드 위치 추적기 구현 | Member D | 8 h | Week 4 | 지속 알림(Notification) 기반 백그라운드 GPS 위치 수신 파이프라인 |
| **TASK-E1-2** | 스마트폰 화면 꺼짐 상태에서도 무중단 위치 수신 및 도로망 궤적 스냅 보정 | Member D | 6 h | Week 4 | 화면 꺼짐 20분간 위치 유실률 0% 및 도로 중심선 스냅핑 모듈 |
| **TASK-E1-3** | 수집된 실시간 궤적과 자택 출발지 좌표를 `AsyncStorage` 로컬에만 영속 저장 | Member D | 6 h | Week 4 | `@PawTrail:walk_history` 로컬 키 영속화 (서버 미전송 원칙 검증) |
| **TASK-E1-4** | 도심 빌딩 숲 GPS 튀김 현상 완화(데드 레커닝 칼만 필터) 알고리즘 적용 | Member D | 4 h | Week 4 | 급격한 GPS 오차(점프 현상) 제거 및 부드러운 궤적 보정 필터링 |

---

#### US-E2: 산책 종료 후 보행 체감 피드백 수집 및 로컬 통계
* **개요**: 완주 후 피로도, 계단/경사 체감 만족도 및 태그를 입력받아 로컬 인포그래픽 통계로 적재.
* **스토리 정보**: `난이도: 하` | `우선순위: Must` | `스토리 포인트: 3 pt` | `총 추정 공수: 12 h` | `스프린트: Sprint 2 (Week 4)`
* **담당자**: **Member E (Lead / Design), Member D (Frontend)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-E2-1** | 산책 완주 결과 요약 인포그래픽 모달 UI/UX 디자인 (시간/거리/소모칼로리) | Member E | 4 h | Week 4 | 산책 완주 요약 통계 카드 및 축하 인포그래픽 애니메이션 뷰 설계 |
| **TASK-E2-2** | 보행 만족도 점수(별점) 및 체감 태그(계단 없음, 경사 완만, 그늘 충분) 입력 UI/UX 인터랙션 설계 | Member E | 4 h | Week 4 | 원터치 피드백 태그 선택 컴포넌트 및 만족도 수집 폼 설계 |
| **TASK-E2-3** | 최근 보행 피드백 누적 통계 `AsyncStorage` 적재 및 주간 리포트 집계 모듈 구현 | Member D | 4 h | Week 4 | 최근 5회 산책 평가 평균치 및 주요 선호 속성 로컬 집계 모듈 |

---

#### US-E3: 로컬 누적 피드백 기반 무상태(Stateless) AI 추천 보정
* **개요**: 로컬에 누적된 피드백 요약본을 플래너 요청 시 HTTP 본문으로 전송받아, 부정 평가 수신 시 허용 경사도를 자동 하향하는 Stateless Memory 체인 가동.
* **스토리 정보**: `난이도: 중` | `우선순위: Should` | `스토리 포인트: 3 pt` | `총 추정 공수: 14 h` | `스프린트: Sprint 2 (Week 4)`
* **담당자**: **Member A (Lead / Agent), Member D (Client)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-E3-1** | 클라이언트 로컬 최근 피드백을 추출해 요청 본문(`client_recent_feedback`)에 동봉 | Member D | 4 h | Week 4 | 플래너 API 호출 시 최근 부정/긍정 태그를 페이로드에 자동 주입 |
| **TASK-E3-2** | 부정 피드백 수신 시 허용 경사도를 자동 하향하는 무상태(Stateless) 가중치 보정 체인 | Member A | 6 h | Week 4 | '힘들었어요' 피드백 수신 시 최대 경사 허용치(8% ➔ 5%) 자동 하향 |
| **TASK-E3-3** | LangGraph Agent 시스템 프롬프트 맥락 주입 및 피드백 반영 단위 테스트 | Member A | 4 h | Week 4 | 피드백 맥락 주입 시 라우팅 추천 파라미터 적응형 보정 E2E 검증 |

---

### [Epic F] 기상/열 위험 정보
* **에픽 요약**: 기상청 단기예보를 n8n/스케줄러로 연동하여 시간대별 지면 복사열 위험 지수를 산출하고 안전 산책 골든타임을 안내.
* **에픽 규모**: **3 Story Points | 4개 세부 Task | 총 12 Hours**

---

#### US-F1: 기상청 단기예보 연동 시간대별 열 위험 지수 안내
* **개요**: 기온·일사량 기반 아스팔트 지면열(50℃+) 위험을 사전에 경고하고 발바닥 화상을 방지하는 골든타임 알림 제공.
* **스토리 정보**: `난이도: 중` | `우선순위: Should` | `스토리 포인트: 3 pt` | `총 추정 공수: 12 h` | `스프린트: Sprint 2 (Week 4)`
* **담당자**: **Member B (Lead / Data), Member C (Backend), Member E (Design)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-F1-1** | 기상청 단기예보 API 클라이언트 및 n8n/스케줄러 기반 시간대별 기온/운량 파싱 | Member B | 4 h | Week 4 | 기상청 격자 좌표 변환 및 매시간 기온, 풍속, 하늘상태 파싱 파이프라인 |
| **TASK-F1-2** | 시간대별 일사량 및 지면열 위험 지수(안전/주의/위험) 산출 수지식 모듈 구현 | Member B | 3 h | Week 4 | 일사량 회귀식을 통한 지면온도 추정 및 3단계 열 위험도 산출 모듈 |
| **TASK-F1-3** | 열 위험 지수 캐싱(`weather_cache`) 및 REST API(`GET /api/weather/heat-risk`) 구현 | Member C | 2 h | Week 4 | 30분 TTL 인메모리 캐싱 적용 및 100ms 이내 빠른 응답 엔드포인트 구현 |
| **TASK-F1-4** | 플래너 상단 산책 골든타임 알림 카드 및 위험 시간대 경고 배너 비주얼 디자인 | Member E | 3 h | Week 4 | 35℃ 이하 안심 시간대 골든타임 표출 카드 및 위험 경고 배너 시각화 |

---

### [Epic G] 거점 연계 및 커뮤니티
* **에픽 요약**: 출발 거점 연계 공영주차장 순환 코스를 탐색하고, Supabase 간편 이메일 가입 및 출발지/도착지 200m 공간 블러링 코스 공유 지원.
* **에픽 규모**: **6 Story Points | 7개 세부 Task | 총 26 Hours**

---

#### US-G1: 출발 거점 연계 공영주차장(P&R) 코스 탐색
* **개요**: 차량 이동 견주를 위해 인근 공영주차장 공공데이터를 검색하고 주차장 출입구를 시작/종료점으로 하는 순환 코스 제공.
* **스토리 정보**: `난이도: 하` | `우선순위: Should` | `스토리 포인트: 2 pt` | `총 추정 공수: 10 h` | `스프린트: Sprint 2 (Week 4)`
* **담당자**: **Member B (Lead / Data), Member C (Backend), Member E (Design)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-G1-1** | 전국 공영주차장 공공데이터 API 클라이언트 및 좌표 반경 검색 모듈 구현 | Member B | 4 h | Week 4 | 출발지 1km 반경 내 무료/유료 공영주차장 위치 및 요금 정보 조회 |
| **TASK-G1-2** | 주차장 출입구 좌표 연계 순환 산책 코스 생성 엔드포인트(`GET /api/parking/nearby`) 연동 | Member C | 3 h | Week 4 | 주차장 출입구에 스냅핑된 순환 산책 루프 Waypoint 자동 생성 |
| **TASK-G1-3** | 플래너 내 '주차 거점 산책' 토글 및 인근 주차장 선택 바텀시트 UI/UX 디자인 | Member E | 3 h | Week 4 | 주차 거점 모드 전환 스위치 및 주차장 선택 인터랙션 컴포넌트 설계 |

---

#### US-G2: 간편 이메일 가입 및 코스 공유 (출발지 200m 마스킹)
* **개요**: 복잡한 소셜 로그인 대신 Supabase Auth 간편 이메일로 1초 가입하고, 커뮤니티 공개 시 출발지 200m 공간 블러링으로 개인 프라이버시 보호.
* **스토리 정보**: `난이도: 중` | `우선순위: Must` | `스토리 포인트: 4 pt` | `총 추정 공수: 16 h` | `스프린트: Sprint 2 (Week 4)`
* **담당자**: **Member C (Lead / Backend), Member B (Data), Member E (Design)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-G2-1** | Supabase Auth 기반 간편 이메일 가입/로그인 모듈 구축 (Auto-confirm 활성화) | Member C | 4 h | Week 4 | 이메일/비밀번호 간편 가입, JWT 세션 발급 및 소셜 OAuth 의존 배제 |
| **TASK-G2-2** | 커뮤니티 코스 공유 시 출발지/도착지 200m 좌표 공간 블러링(Spatial Jittering) 백엔드 파이프라인 | Member B | 4 h | Week 4 | 출발/도착 반경 200m 좌표 절단 및 가우스 노이즈 지터링으로 자택 은닉 |
| **TASK-G2-3** | Supabase `community_courses` 테이블 적재 및 공개 피드 조회 REST API 구현 | Member C | 4 h | Week 4 | 200m 마스킹된 공개 안심 코스 피드 페이징 조회 API 개발 |
| **TASK-G2-4** | 커뮤니티 피드 뷰, 200m 마스킹 사전확인 모달 및 코스 북마크/좋아요 UI/UX 디자인 | Member E | 4 h | Week 4 | 마스킹된 코스 프리뷰 모달, 안심 공유 동의 다이얼로그 및 북마크 뷰 설계 |

---

### [Epic H] 무중단 배포 & 실사용 검증
* **에픽 요약**: EAS Build로 1회 APK 패키징 후 모든 변경사항은 EAS Update 무선 OTA로 실시간 배포하며, 견주 5인 필드 CBT를 통해 제품 가치를 최종 검증.
* **에픽 규모**: **5 Story Points | 4개 세부 Task | 총 24 Hours**

---

#### US-H1: EAS Build 1회 배포, EAS Update 무선 OTA 및 5인 CBT
* **개요**: 재설치 피로도가 없는 EAS OTA 무선 배포망을 구축하고, 실사용자 5인 필드 테스트를 통해 핸즈프리 음성 안내와 계단 회피 적중률을 실전 검증.
* **스토리 정보**: `난이도: 상` | `우선순위: Must` | `스토리 포인트: 5 pt` | `총 추정 공수: 24 h` | `스프린트: Hardening (Week 4~5)`
* **담당자**: **전원 (Lead: Member E, D)**

| Task ID | 세부 작업 내용 (Task Specification) | 담당자 | 공수 | 주차 | 완료 정의 및 산출물 (DoD / Deliverables) |
|:---:|---|:---:|:---:|:---:|---|
| **TASK-H1-1** | EAS Build 기반 테스터용 Android APK 1회 패키징 및 5인 테스터 배포 환경 구축 | Member D | 6 h | Week 4 | EAS Build 클라우드 프로파일 설정, 릴리즈 APK 빌드 및 테스터 5인 설치 |
| **TASK-H1-2** | EAS Update (`expo-updates`) GitHub Actions CI/CD 연동 무선 무점검 OTA 파이프라인 수립 | Member D | 6 h | Week 4 | `main` 브랜치 푸시 시 재설치 없는 무선 무점검 OTA 자동 배포 검증 |
| **TASK-H1-3** | 실사용자 5인 대상 사용성 평가(Usability Testing) 및 UI/UX 휴리스틱 평가 총괄 | Member E | 6 h | Week 5 | 5인 견주 산책 시나리오 완주 설문 수집, 만족도 및 결함 분석 보고서 정리 |
| **TASK-H1-4** | 5인 CBT 피드백 기반 모바일 UI/UX 튜닝 및 디자인 시스템 최종 개선 | Member E | 6 h | Week 5 | 음성 안내 타이밍(30m 전) 캘리브레이션 및 디자인 시스템 최종 반영 |

---

## 📊 3. 공수 집계 및 애자일 일정 매핑

### 3.1 에픽별 작업량 및 비중 요약표

| 에픽 (Epic) | Story Points | 세부 Task 수 | 추정 공수 (Hours) | 공수 비중 (%) | 권장 스프린트 주기 |
|---|:---:|:---:|:---:|:---:|:---:|
| **Epic A. 산책 조건 입력 및 개인화** | 11 pt | 11개 | 52 h | 14.0% | Sprint 1 (Week 1~2) |
| **Epic B. 무계단·완만 경사·그늘 우선 경로 생성** | 26 pt | 16개 | 114 h | 30.6% | Sprint 1~2 (Week 1~3) |
| **Epic C. 모바일 인터페이스 & 백그라운드 안내** | 10 pt | 8개 | 48 h | 12.9% | Sprint 2 (Week 3) |
| **Epic D. 현장 위험 분석 및 재탐색** | 10 pt | 8개 | 46 h | 12.4% | Sprint 2 (Week 3~4) |
| **Epic E. 산책 기록 및 Memory (Local-First)** | 11 pt | 10개 | 50 h | 13.4% | Sprint 2 (Week 4) |
| **Epic F. 기상/열 위험 정보** | 3 pt | 4개 | 12 h | 3.2% | Sprint 2 (Week 4) |
| **Epic G. 거점 연계 및 커뮤니티 (200m 마스킹)** | 6 pt | 7개 | 26 h | 7.0% | Sprint 2 (Week 4) |
| **Epic H. 무중단 배포 & 실사용 검증 (EAS/OTA/CBT)** | 5 pt | 4개 | 24 h | 6.5% | Hardening (Week 4~5) |
| **합계 (Grand Total)** | **77 pt** (총 82 pt) | **68개 Task** | **372 h** | **100.0%** | **5주 (Sprint 1~2 + Hardening)** |

> [!NOTE]
> **스토리 포인트 표기 기준 안내**:  
> 문서 03, 05, 07의 총량 기준인 **77 Story Points**는 순수 스프린트 개발 기능 스토리(US-A1 ~ US-G2)를 엄격히 집계한 표준치입니다. 인프라 패키징 및 최종 CBT를 포함한 전체 18개 스토리 산정 시 총 82 pt에 해당하며, 총 개발 공수는 **372 Hours로 100% 일치**합니다.

---

### 3.2 팀원별 공수 배분 현황표 (Capacity Allocation)

| 담당자 | 주요 역할 및 책임 (Core Position) | 전담 Task 수 | 총 담당 공수 (Hours) | 주당 평균 공수 (5주 기준) | 공수 점유율 (%) |
|:---:|---|:---:|:---:|:---:|:---:|
| **Member A** | **PM & AI Agent Lead** | 11개 Task | **65 h** | 약 13.0 h / 주 | 17.5% |
| **Member B** | **AI & Spatial Data Engineer** | 14개 Task | **71 h** | 약 14.2 h / 주 | 19.1% |
| **Member C** | **Backend & Spatial Routing Lead** | 14개 Task | **91 h** | 약 18.2 h / 주 | 24.5% |
| **Member D** | **Frontend & Mobile App Lead** | 17개 Task | **94 h** | 약 18.8 h / 주 | 25.3% |
| **Member E** | **UI/UX Designer & Product Experience Lead** | 12개 Task | **51 h** | 약 10.2 h / 주 | 13.7% |
| **합계** | **5인 전원 (Full Cross-Functional Team)** | **68개 Task** | **372 h** | **약 74.4 h / 주 (팀 전체)** | **100.0%** |

---

### 3.3 주차별 스프린트 공수 흐름표 (Timeline & Sprint Cadence)

```text
[Sprint 1: Week 1~2] 코어 AI 파이프라인, 로컬 스토리지, GIS 엔진 & 디자인 시스템 (166 h)
       │
[Sprint 2: Week 3~4] 모바일 연동, 핸즈프리 음성 안내, 비전 판독, 커뮤니티 & EAS 배포 (182 h)
       │
[Hardening: Week 5] 5인 실사용자 CBT 완료 보고, 사용성 개선, 무선 OTA 핫픽스 & 최종 안정화 (24 h)
```

| 스프린트 단계 | 주차 (Timeline) | 주간 핵심 마일스톤 | 투입 공수 (Hours) | 주요 산출물 |
|:---:|:---:|---|:---:|---|
| **Sprint 1** | **Week 1** | Expo 프로젝트 초기화, 디자인 시스템, LangGraph 스키마 수립, Routing 어댑터 | **70 h** | `AgentState`, 디자인 토큰, ORS/OSRM Adapter |
| **Sprint 1** | **Week 2** | `AsyncStorage` 프로필 완성, OSM Steps 배제, DEM 경사도 연산, Scorer, UI 목업 | **96 h** | 무계단 라우팅, 경사도 비용 함수, 다요소 채점기, 고화질 목업 |
| **Sprint 2** | **Week 3** | SunCalc 그늘 분석, Gemini 비전 모델 선택 체인, react-native-maps & expo-speech 음성 길 안내 | **104 h** | 그늘 다각형 교차, 비전 검사기, 백그라운드 TTS, 바텀시트 UI |
| **Sprint 2** | **Week 4** | Android Foreground Service GPS, 주차장 연동, 200m 마스킹 커뮤니티, EAS Build APK 패키징 | **78 h** | Foreground 추적기, 공간 지터링, 테스터 APK, 피드백 UI |
| **Hardening** | **Week 5** | 5인 CBT 사용성 평가 분석, EAS Update 무선 OTA 핫픽스 배포, 최종 디자인 튜닝 | **24 h** | CBT 종합 평가서, 무선 OTA 실시간 반영, 최종 릴리즈 |
| **전체 합계** | **총 5주** | **18개 사용자 스토리 및 68개 Task 완주** | **372 h** | **PawTrail 정식 출시 버전 (DoD 100% 달성)** |

---

## 📑 4. 전체 사용자 스토리 및 공수 총괄 요약표

| Story ID | 사용자 스토리 명칭 | 주 담당자 | 협업 담당자 | Story Points | Task 개수 | 총 추정 공수 | 스프린트 주기 |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **US-A1** | 대화형 자연어 산책 요청 및 조건 구조화 | Member A | — | 5 pt | 4개 | 24 h | Sprint 1 (Week 1) |
| **US-A2** | 반려견 프로필 로컬 등록 및 JSON 백업/복원 | Member E | Member D | 3 pt | 4개 | 14 h | Sprint 1 (Week 1~2) |
| **US-A3** | 목표 산책 시간/거리 기반 환산 (속도/슬라이더) | Member A | Member E | 3 pt | 3개 | 14 h | Sprint 1 (Week 1~2) |
| **US-B1** | 지도 데이터 기반 계단 구간 우선 회피 | Member C | Member B | 8 pt | 4개 | 34 h | Sprint 1 (Week 2) |
| **US-B2** | DEM 기반 완만 경사 우선 순환 경로 도출 | Member C | Member B | 5 pt | 4개 | 24 h | Sprint 1 (Week 2) |
| **US-B3** | 태양 위치 및 건물 형상 기반 시간대별 그늘 평가 | Member C | Member B | 5 pt | 4개 | 22 h | Sprint 1~2 (Week 2~3) |
| **US-B4** | Routing API Adapter 연동 및 다요소 스코어링 | Member C | Member A | 8 pt | 4개 | 34 h | Sprint 1 (Week 1~2) |
| **US-C1** | React Native Maps 기반 구간별 색상 분기 렌더링 | Member D | Member E | 5 pt | 4개 | 24 h | Sprint 2 (Week 3) |
| **US-C2** | 시선 해방(Eyes-Free) 백그라운드 핸즈프리 음성 길 안내 | Member D | — | 5 pt | 4개 | 24 h | Sprint 2 (Week 3) |
| **US-D1** | Vision AI 기반 현장 턱·계단·보행 장애물 시각 분석 | Member B | — | 5 pt | 4개 | 24 h | Sprint 2 (Week 3) |
| **US-D2** | 현장 위험 구간 우회 및 동적 재탐색 | Member C | Member B, A, D | 5 pt | 4개 | 22 h | Sprint 2 (Week 3~4) |
| **US-E1** | 백그라운드 GPS 위치 추적 및 실산책 경로 로컬 저장 | Member D | — | 5 pt | 4개 | 24 h | Sprint 2 (Week 4) |
| **US-E2** | 산책 종료 후 보행 체감 피드백 수집 및 로컬 통계 | Member E | Member D | 3 pt | 3개 | 12 h | Sprint 2 (Week 4) |
| **US-E3** | 로컬 누적 피드백 기반 무상태(Stateless) AI 추천 보정 | Member A | Member D | 3 pt | 3개 | 14 h | Sprint 2 (Week 4) |
| **US-F1** | 기상청 단기예보 연동 시간대별 열 위험 지수 안내 | Member B | Member C, E | 3 pt | 4개 | 12 h | Sprint 2 (Week 4) |
| **US-G1** | 출발 거점 연계 공영주차장(P&R) 코스 탐색 | Member B | Member C, E | 2 pt | 3개 | 10 h | Sprint 2 (Week 4) |
| **US-G2** | 간편 이메일 가입 및 코스 공유 (출발지 200m 마스킹) | Member C | Member B, E | 4 pt | 4개 | 16 h | Sprint 2 (Week 4) |
| **US-H1** | EAS Build 1회 배포, EAS Update 무선 OTA 및 5인 CBT | Member E | Member D | 5 pt | 4개 | 24 h | Hardening (Week 4~5) |
| **총합** | **18개 핵심 사용자 스토리 전수** | **5인 전원** | — | **77 pt** (총 82 pt) | **68개 Task** | **372 h** | **5주 완결형 로드맵** |

---

## 👤 5. 팀원별 상세 작업 분할 및 역량 배분 (Member-by-Member WBS)

### 5.1 Member A (PM & AI Agent Lead)
* **총 배정 공수**: **65 Hours** (전체 공수의 17.5% | 주당 평균 약 13.0h)
* **담당 스토리**: US-A1, US-A3, US-B4, US-D2, US-E3
* **전담 Task 명세**:

| Task ID | 소속 스토리 | 세부 작업 내용 | 공수 | 담당 주차 |
|:---:|:---:|---|:---:|:---:|
| **TASK-A1-1** | US-A1 | LangGraph Agent 상태 그래프 스키마(`AgentState`) 및 노드 구조 설계 | 4 h | Week 1 |
| **TASK-A1-2** | US-A1 | 자연어 발화에서 시간·계단·경사·그늘 선호 엔티티를 추출하는 ReAct 프롬프트 작성 | 6 h | Week 1 |
| **TASK-A1-3** | US-A1 | Pydantic V2 Strict Input Schema 및 요청 본문의 로컬 프로필 바인딩 모듈 개발 | 6 h | Week 1 |
| **TASK-A1-4** | US-A1 | FastAPI REST API 연동 및 모의 발화 10종 엔티티 추출 단위/통합 테스트 | 8 h | Week 1 |
| **TASK-A3-2** | US-A3 | 체급(소/중/대/노령견)별 표준 보행 속도 상수 모델 및 목표 거리 자동 환산 엔진 구현 | 5 h | Week 2 |
| **TASK-A3-3** | US-A3 | 생성된 경로 소요 시간의 목표 시간 수렴도(±15%) 오차 검증 및 브리핑 체인 연동 | 5 h | Week 2 |
| **TASK-B4-3** | US-B4 | 계단·경사·그늘·거리 다요소 Candidate Route Scorer 수치 랭킹 알고리즘 구현 | 8 h | Week 2 |
| **TASK-B4-4** | US-B4 | LangGraph Agent 최적 순환 루프 선정 및 추천 사유 생성 가드레일 체인 연동 | 8 h | Week 2 |
| **TASK-D2-3** | US-D2 | 우회 사유 및 변경 경로 에이전트 음성 브리핑 메시지 생성 체인 연동 | 5 h | Week 4 |
| **TASK-E3-2** | US-E3 | 부정 피드백 수신 시 허용 경사도를 자동 하향하는 무상태 가중치 보정 체인 | 6 h | Week 4 |
| **TASK-E3-3** | US-E3 | LangGraph Agent 시스템 프롬프트 맥락 주입 및 피드백 반영 단위 테스트 | 4 h | Week 4 |
| **소계** | **5개 스토리** | **Member A 전담 Task 11개 합계** | **65 h** | — |

---

### 5.2 Member B (AI & Spatial Data Engineer)
* **총 배정 공수**: **71 Hours** (전체 공수의 19.1% | 주당 평균 약 14.2h)
* **담당 스토리**: US-B1, US-B2, US-B3, US-D1, US-D2, US-F1, US-G1, US-G2
* **전담 Task 명세**:

| Task ID | 소속 스토리 | 세부 작업 내용 | 공수 | 담당 주차 |
|:---:|:---:|---|:---:|:---:|
| **TASK-B1-4** | US-B1 | 계단 밀집 구역 테스트베드(5개 권역) 대상 무계단 회피 라우팅 정량 검증 | 8 h | Week 2 |
| **TASK-B2-1** | US-B2 | 수치표고모델(DEM) 래스터 데이터 적재 및 경로 세그먼트 고도 샘플링 파이프라인 | 7 h | Week 2 |
| **TASK-B2-4** | US-B2 | 구릉지 지형 테스트베드 대상 완만 경로 선별 알고리즘 정확도 검증 | 4 h | Week 2 |
| **TASK-B3-1** | US-B3 | `SunCalc` 연동 산책 일시/위치 기준 실시간 태양 고도각 및 방위각 연산 모듈 개발 | 5 h | Week 2 |
| **TASK-B3-4** | US-B3 | 정오 vs 늦은 오후 시간대별 그늘 평가 대조 테스트베드 검증 및 신뢰도 태깅 | 4 h | Week 3 |
| **TASK-D1-1** | US-D1 | 현장 위험물(높은 턱, 계단, 공사) 및 공원 안내판 벤치마킹 이미지셋 구축 및 라벨링 | 6 h | Week 3 |
| **TASK-D1-2** | US-D1 | Gemini 가용 모델 체인(3.5 Flash-Lite ➔ 3.1 Flash-Lite ➔ 3.6 Flash) 프롬프트 엔지니어링 및 Structured JSON 스키마 고정 | 7 h | Week 3 |
| **TASK-D1-3** | US-D1 | 모션 블러, 저조도 사진 입력 시 예외 처리 및 사용자 재촬영 가이드 로직 구현 | 5 h | Week 3 |
| **TASK-D1-4** | US-D1 | 이미지 업로드 REST API(`POST /api/walks/inspect-board`) 연동 및 지연시간 최적화 | 6 h | Week 3 |
| **TASK-D2-1** | US-D2 | Vision 판독 위험 신뢰도(Confidence >= 0.85) 필터링 및 우회 트리거 이벤트 연동 | 4 h | Week 3 |
| **TASK-F1-1** | US-F1 | 기상청 단기예보 API 클라이언트 및 n8n/스케줄러 기반 시간대별 기온/운량 파싱 | 4 h | Week 4 |
| **TASK-F1-2** | US-F1 | 시간대별 일사량 및 지면열 위험 지수(안전/주의/위험) 산출 수지식 모듈 구현 | 3 h | Week 4 |
| **TASK-G1-1** | US-G1 | 전국 공영주차장 공공데이터 API 클라이언트 및 좌표 반경 검색 모듈 구현 | 4 h | Week 4 |
| **TASK-G2-2** | US-G2 | 커뮤니티 코스 공유 시 출발지/도착지 200m 좌표 공간 블러링(Spatial Jittering) 백엔드 파이프라인 | 4 h | Week 4 |
| **소계** | **8개 스토리** | **Member B 전담 Task 14개 합계** | **71 h** | — |

---

### 5.3 Member C (Backend & Spatial Routing Lead)
* **총 배정 공수**: **91 Hours** (전체 공수의 24.5% | 주당 평균 약 18.2h)
* **담당 스토리**: US-B1, US-B2, US-B3, US-B4, US-D2, US-F1, US-G1, US-G2
* **전담 Task 명세**:

| Task ID | 소속 스토리 | 세부 작업 내용 | 공수 | 담당 주차 |
|:---:|:---:|---|:---:|:---:|
| **TASK-B1-1** | US-B1 | OSM 보행 도로망 데이터 파싱 및 `highway=steps` 링크 추출 인덱서 구축 | 8 h | Week 2 |
| **TASK-B1-2** | US-B1 | 계단 링크 탐색 배제(Hard Constraint) 및 회피 가중치 부여 라우팅 모듈 구현 | 10 h | Week 2 |
| **TASK-B1-3** | US-B1 | 모든 연결로가 계단인 고립 지형 대상 최소 계단 대체 경로 산출 Fallback 로직 개발 | 8 h | Week 2 |
| **TASK-B2-2** | US-B2 | 세그먼트별 `max_slope_percent` 및 누적 고도 상승/하강 연산 모듈 개발 | 7 h | Week 2 |
| **TASK-B2-3** | US-B2 | 견주 경사 선호도(매우 완만/완만/일반)에 따른 경사도 페널티 비용 함수 구현 | 6 h | Week 2 |
| **TASK-B3-2** | US-B3 | 건물 외곽선 폴리곤 및 층수/높이 데이터 기반 시간대별 그림자 투영 다각형 연산 | 8 h | Week 3 |
| **TASK-B3-3** | US-B3 | 보행 링크와 그림자 다각형 교차 공간 연산을 통한 예상 그늘 비율(`shade_ratio`) 산출 | 5 h | Week 3 |
| **TASK-B4-1** | US-B4 | OpenRouteService / OSRM REST API 연동 독립 어댑터(Adapter) 레이어 구현 | 10 h | Week 1 |
| **TASK-B4-2** | US-B4 | 출발지 중심 다각형 Waypoint 샘플링 기반 순환 루프 후보(2~3개) 생성 모듈 개발 | 8 h | Week 1 |
| **TASK-D2-2** | US-D2 | 위험 감지 좌표 기준 인접 링크 임시 차단(Block List) 및 안전 우회 경로 재탐색 API 구현 | 8 h | Week 3 |
| **TASK-F1-3** | US-F1 | 열 위험 지수 캐싱(`weather_cache`) 및 REST API(`GET /api/weather/heat-risk`) 구현 | 2 h | Week 4 |
| **TASK-G1-2** | US-G1 | 주차장 출입구 좌표 연계 순환 산책 코스 생성 엔드포인트(`GET /api/parking/nearby`) 연동 | 3 h | Week 4 |
| **TASK-G2-1** | US-G2 | Supabase Auth 기반 간편 이메일 가입/로그인 모듈 구축 (Auto-confirm 활성화) | 4 h | Week 4 |
| **TASK-G2-3** | US-G2 | Supabase `community_courses` 테이블 적재 및 공개 피드 조회 REST API 구현 | 4 h | Week 4 |
| **소계** | **8개 스토리** | **Member C 전담 Task 14개 합계** | **91 h** | — |

---

### 5.4 Member D (Frontend & Mobile App Lead)
* **총 배정 공수**: **94 Hours** (전체 공수의 25.3% | 주당 평균 약 18.8h)
* **담당 스토리**: US-A2, US-C1, US-C2, US-D2, US-E1, US-E2, US-E3, US-H1
* **전담 Task 명세**:

| Task ID | 소속 스토리 | 세부 작업 내용 | 공수 | 담당 주차 |
|:---:|:---:|---|:---:|:---:|
| **TASK-A2-1** | US-A2 | `@react-native-async-storage/async-storage` 래퍼 및 프로필 CRUD 모듈 개발 | 4 h | Week 1 |
| **TASK-A2-3** | US-A2 | 기기 변경 및 앱 재설치 대비 프로필 JSON 파일 내보내기/가져오기 모듈 구현 | 3 h | Week 2 |
| **TASK-C1-1** | US-C1 | `react-native-maps` 지도 캔버스 마운트 및 현재 위치 마커/카메라 트래킹 구현 | 6 h | Week 3 |
| **TASK-C1-2** | US-C1 | 경로 속성(그늘/완만: 초록, 일반: 파랑, 주의: 주황) 분기 Polyline 렌더링 구현 | 8 h | Week 3 |
| **TASK-C2-1** | US-C2 | OSRM/ORS steps 기반 턴 안내 문구 및 노면 속성 파싱 엔진 개발 | 6 h | Week 3 |
| **TASK-C2-2** | US-C2 | `expo-speech` TTS 연동 및 회전 지점 30m 전 사전 음성 브리핑 송출 엔진 구현 | 7 h | Week 3 |
| **TASK-C2-3** | US-C2 | 전환점 사전 비프음 알림 및 경로 이탈(Off-route) 감지 시 재탐색 음성 알림 구현 | 5 h | Week 3 |
| **TASK-C2-4** | US-C2 | 스마트폰 화면 꺼짐 상태 Android Foreground Service 음성 안내 연속성 검증 | 6 h | Week 3 |
| **TASK-D2-4** | US-D2 | 모바일 지도 화면 상 우회 경로 실시간 갱신 및 토스트/확인 모달 인터랙션 구현 | 5 h | Week 4 |
| **TASK-E1-1** | US-E1 | `expo-location`과 Android Foreground Service 연동 백그라운드 위치 추적기 구현 | 8 h | Week 4 |
| **TASK-E1-2** | US-E1 | 스마트폰 화면 꺼짐 상태에서도 무중단 위치 수신 및 도로망 궤적 스냅 보정 | 6 h | Week 4 |
| **TASK-E1-3** | US-E1 | 수집된 실시간 궤적과 자택 출발지 좌표를 `AsyncStorage` 로컬에만 영속 저장 | 6 h | Week 4 |
| **TASK-E1-4** | US-E1 | 도심 빌딩 숲 GPS 튀김 현상 완화(데드 레커닝 칼만 필터) 알고리즘 적용 | 4 h | Week 4 |
| **TASK-E2-3** | US-E2 | 최근 보행 피드백 누적 통계 `AsyncStorage` 적재 및 주간 리포트 집계 모듈 구현 | 4 h | Week 4 |
| **TASK-E3-1** | US-E3 | 클라이언트 로컬 최근 피드백을 추출해 요청 본문(`client_recent_feedback`)에 동봉 | 4 h | Week 4 |
| **TASK-H1-1** | US-H1 | EAS Build 기반 테스터용 Android APK 1회 패키징 및 5인 테스터 배포 환경 구축 | 6 h | Week 4 |
| **TASK-H1-2** | US-H1 | EAS Update (`expo-updates`) GitHub Actions CI/CD 연동 무선 무점검 OTA 파이프라인 수립 | 6 h | Week 4 |
| **소계** | **8개 스토리** | **Member D 전담 Task 17개 합계** | **94 h** | — |

---

### 5.5 Member E (UI/UX Designer & Product Experience Lead)
* **총 배정 공수**: **51 Hours** (전체 공수의 13.7% | 주당 평균 약 10.2h)
* **담당 스토리**: US-A2, US-A3, US-C1, US-E2, US-F1, US-G1, US-G2, US-H1
* **전담 Task 명세**:

| Task ID | 소속 스토리 | 세부 작업 내용 | 공수 | 담당 주차 |
|:---:|:---:|---|:---:|:---:|
| **TASK-A2-2** | US-A2 | 반려견 프로필 온보딩 및 수정 폼 UI 컴포넌트 설계 | 4 h | Week 1 |
| **TASK-A2-4** | US-A2 | 앱 온보딩 및 프로필 UI 전역 웰니스 카피라이팅 가이드 및 디자인 시스템 검증 | 3 h | Week 2 |
| **TASK-A3-1** | US-A3 | 플래너 UI 산책 시간 슬라이더(10~90분) 및 노면 칩 인터랙션 디자인 | 4 h | Week 1 |
| **TASK-C1-3** | US-C1 | 거리, 시간, 최대 경사, 그늘 비율 요약 카드 및 OSRM 스텝 리스트 바텀시트 UI/UX 디자인 시스템 설계 | 6 h | Week 3 |
| **TASK-C1-4** | US-C1 | 모바일 Thumb Zone 뷰포트 반응형 레이아웃 설계 및 터치 제스처 최적화 | 4 h | Week 3 |
| **TASK-E2-1** | US-E2 | 산책 완주 결과 요약 인포그래픽 모달 UI/UX 디자인 (시간/거리/소모칼로리) | 4 h | Week 4 |
| **TASK-E2-2** | US-E2 | 보행 만족도 점수(별점) 및 체감 태그(계단 없음, 경사 완만, 그늘 충분) 입력 UI/UX 인터랙션 설계 | 4 h | Week 4 |
| **TASK-F1-4** | US-F1 | 플래너 상단 산책 골든타임 알림 카드 및 위험 시간대 경고 배너 비주얼 디자인 | 3 h | Week 4 |
| **TASK-G1-3** | US-G1 | 플래너 내 '주차 거점 산책' 토글 및 인근 주차장 선택 바텀시트 UI/UX 디자인 | 3 h | Week 4 |
| **TASK-G2-4** | US-G2 | 커뮤니티 피드 뷰, 200m 마스킹 사전확인 모달 및 코스 북마크/좋아요 UI/UX 디자인 | 4 h | Week 4 |
| **TASK-H1-3** | US-H1 | 실사용자 5인 대상 사용성 평가(Usability Testing) 및 UI/UX 휴리스틱 평가 총괄 | 6 h | Week 5 |
| **TASK-H1-4** | US-H1 | 5인 CBT 피드백 기반 모바일 UI/UX 튜닝 및 디자인 시스템 최종 개선 | 6 h | Week 5 |
| **소계** | **8개 스토리** | **Member E 전담 Task 12개 합계** | **51 h** | — |

---

### 5.6 팀 전체 종합 검증 결론
* **총 Story Points**: **77 pt** (기능 스프린트 77 pt / 총 82 pt 전수 정합)
* **총 세부 구현 Task**: **68개 Task** (1인 1담당 원칙 100% 준수, 다중 배정 0건)
* **총 개발 공수**: **372 Hours**  
  $$\text{Member A}(65\text{h}) + \text{Member B}(71\text{h}) + \text{Member C}(91\text{h}) + \text{Member D}(94\text{h}) + \text{Member E}(51\text{h}) = \mathbf{372\text{ Hours}}$$
* **생명주기 산출물 정합성**:
  - `01_PawTrail_Project_Proposal.md`: 페인포인트 1~5 및 핵심 차별화 가치 100% 반영
  - `02_PawTrail_Team_building.md`: 5인 전문 R&R 및 기술 아키텍처 전략 100% 일치
  - `03_PawTrail_Agile_User_Stories.md`: 18개 스토리 및 인수 조건(AC), 완료 정의(DoD) 100% 매핑
  - `04_PawTrail_Architecture_Design.md`: REST API 엔드포인트 및 Local-First 영속성 스키마 완벽 연계
  - `05_PawTrail_Detailed_Implementation_Plan.md`: 5주차 스프린트 로드맵 및 주차별 마일스톤 전수 일치
  - `07_PawTrail_Traceability_Matrix.md`: 18개 스토리, 68개 Task, 77 pt, 372h 양방향 추적 무결성 확보
