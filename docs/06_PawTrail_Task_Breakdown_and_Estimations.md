# [작업 분할 명세서] PawTrail 사용자 스토리별 상세 구현 Task 및 작업량 추정

## 1. 개요 및 추정 기준

* **프로젝트명**: PawTrail (AI Native 반려견 안심 산책 에이전트 및 핸즈프리 모바일 플랫폼)
* **목적**: 18개 사용자 스토리(US-A1 ~ US-H1)를 실제 개발 가능한 세부 Task로 분할하고, 애자일 추정치(Story Points, 공수 Hours) 및 담당자를 지정하여 5주간의 명확한 실행 계획을 제공.
* **핵심 아키텍처 정책 반영**:
  - **React Native (Expo SDK 51+)**: Android Foreground Service 백그라운드 GPS + `expo-speech` TTS 핸즈프리 음성 길 안내.
  - **EAS Build & EAS Update OTA**: 1회 APK 패키징 후 모든 핫픽스는 무선 무점검 실시간 OTA 배포.
  - **프라이버시 로컬 보관 (Local-First)**: 자택 위치, 보행 궤적, 반려견 프로필은 폰(`AsyncStorage`)에만 저장하고 JSON 백업/복원 지원.
  - **간단한 이메일 가입 & 커뮤니티 보호**: Supabase Auth 기본 이메일 가입(Auto-confirm) 및 커뮤니티 공유 시 출발지 200m 마스킹.
* **팀 구성 (5인)**:
  - Member A: AI Agent / Product Logic Lead
  - Member B: Vision / Multimodal AI Lead
  - Member C: Backend / Routing / GIS Data Lead
  - Member D: Frontend / Mobile App Lead
  - Member E: Infra / Automation & QA Lead

---

## 2. 사용자 스토리별 세부 구현 Task 명세

### [Epic A] 산책 조건 입력 및 개인화

#### US-A1: 대화형 자연어 산책 요청 및 조건 구조화 (5 pt / 총 24h)
* **담당**: Member A (Sub: Member D) | **스프린트**: Sprint 1 (Week 1)
* **세부 Task**:
  * **TASK-A1-1**: LangGraph Agent 상태 그래프 스키마(`AgentState`) 설계 (4h / Member A)
  * **TASK-A1-2**: 자연어 발화에서 시간, 계단/경사/그늘 선호 엔티티를 추출하는 ReAct 프롬프트 작성 (6h / Member A)
  * **TASK-A1-3**: Pydantic V2 Strict Input Schema 및 요청 페이로드의 로컬 프로필 바인딩 모듈 (6h / Member A)
  * **TASK-A1-4**: FastAPI REST API 연동 및 모의 발화 10종 파싱 테스트 (8h / Member A)

#### US-A2: 반려견 프로필 로컬 등록 및 JSON 백업/복원 (3 pt / 총 14h)
* **담당**: Member D | **스프린트**: Sprint 1 (Week 1~2)
* **세부 Task**:
  * **TASK-A2-1**: `@react-native-async-storage/async-storage` 래퍼 모듈 개발 (4h / Member D)
  * **TASK-A2-2**: 반려견 프로필(견종, 체중, 연령, 관절 안심 케어) 입력/수정 폼 개발 (4h / Member D)
  * **TASK-A2-3**: 앱 재설치 대비 "프로필 JSON 파일 내보내기/가져오기" 백업 모듈 구현 (6h / Member D)

#### US-A3: 목표 산책 시간/거리 기반 환산 (3 pt / 총 16h)
* **담당**: Member A, C (Sub: Member D) | **스프린트**: Sprint 1 (Week 1~2)
* **세부 Task**:
  * **TASK-A3-1**: 플래너 UI 산책 시간 원터치 칩(15/30/45/60분) 및 슬라이더 바인딩 (4h / Member D)
  * **TASK-A3-2**: 체급 및 관절 상태별 보행 속도 기반 목표 거리 환산 모듈 구현 (6h / Member C)
  * **TASK-A3-3**: 목표 시간 대비 경로 소요 시간 수렴도($\pm 15\%$) 검증 테스트 (6h / Member C)

---

### [Epic B] 무계단·완만한 경사·그늘 우선 경로 생성

#### US-B1: 지도 데이터 기반 확인된 계단 구간 우선 회피 (8 pt / 총 34h)
* **담당**: Member C | **스프린트**: Sprint 1 (Week 2)
* **세부 Task**:
  * **TASK-B1-1**: OSM 보행 도로망 데이터 파싱 및 `highway=steps` 링크 추출 인덱서 구축 (8h / Member C)
  * **TASK-B1-2**: 계단 링크 탐색 배제(Hard Constraint) 및 신뢰도 메타데이터 부여 모듈 구현 (10h / Member C)
  * **TASK-B1-3**: 모든 경로가 계단을 포함할 때 최소 계단 대체 경로 산출 Fallback 로직 개발 (8h / Member C)
  * **TASK-B1-4**: 계단 밀집 구역 테스트베드 대상 회피 라우팅 단위/통합 테스트 (8h / Member C)

#### US-B2: DEM 기반 최대 경사도 제어 및 완만 경사 우선 경로 도출 (5 pt / 총 26h)
* **담당**: Member C | **스프린트**: Sprint 1 (Week 2)
* **세부 Task**:
  * **TASK-B2-1**: 수치표고모델(DEM) 래스터 데이터 적재 및 경로 세그먼트 고도 샘플링 파이프라인 (8h / Member C)
  * **TASK-B2-2**: 세그먼트별 `max_slope_percent` 및 급경사 비율 연산 모듈 개발 (8h / Member C)
  * **TASK-B2-3**: 사용자 경사 선호도(매우 완만/완만/제한 없음)에 따른 페널티 비용 함수 구현 (6h / Member C)
  * **TASK-B2-4**: 구릉지 지형 테스트 샘플 대상 완만 경로 선별 알고리즘 검증 (4h / Member C)

#### US-B3: 태양 위치 및 건물 형상 기반 시간대별 그늘 우선 평가 (5 pt / 총 28h)
* **담당**: Member C | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-B3-1**: `SunCalc` 연동 산책 일시/위치 기준 태양 고도각 및 방위각 계산 모듈 (6h / Member C)
  * **TASK-B3-2**: 가용 건물 2.5D/3D 외곽선 및 높이 데이터 기반 그림자 투영 다각형 연산 (10h / Member C)
  * **TASK-B3-3**: 보행 링크와 그림자 다각형 교차 연산을 통한 예상 그늘 비율(`shade_ratio`) 산출 (6h / Member C)
  * **TASK-B3-4**: 정오 vs 늦은 오후 시간대별 그늘 평가 대조 테스트 및 신뢰도 태깅 (6h / Member C)

#### US-B4: Routing API Adapter 연동 및 후보 경로 다요소 스코어링 (8 pt / 총 36h)
* **담당**: Member C, A | **스프린트**: Sprint 1 (Week 1~2)
* **세부 Task**:
  * **TASK-B4-1**: OpenRouteService / OSRM REST API 연동 독립 Adapter 레이어 구현 (10h / Member C)
  * **TASK-B4-2**: 출발지 중심 다각형 Waypoint 샘플링 기반 순환 루프 후보(2~3개) 생성 모듈 (8h / Member C)
  * **TASK-B4-3**: 계단, 경사, 그늘, 시간 오차를 종합 평가하는 Candidate Route Scorer 개발 (10h / Member C, A)
  * **TASK-B4-4**: Routing API 실패/장애 시 대체 템플릿 Fallback 및 지연시간 최적화 (8h / Member C)

---

### [Epic C] 모바일 인터페이스 & 백그라운드 안내

#### US-C1: React Native Maps 기반 구간별 색상 분기 경로 시각화 (5 pt / 총 24h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-C1-1**: `react-native-maps` 지도 캔버스 마운트 및 현재 위치 마커 렌더링 (6h / Member D)
  * **TASK-C1-2**: 경로 속성(그늘/완만: 초록, 일반: 파랑, 주의: 주황) 분기 Polyline 렌더링 (8h / Member D)
  * **TASK-C1-3**: 거리, 시간, 최대 경사, 그늘 비율 요약 카드 및 OSRM 스텝 리스트 UI (6h / Member D)
  * **TASK-C1-4**: 모바일 실기기 뷰포트 반응형 레이아웃 및 제스처 최적화 (4h / Member D)

#### US-C2: 시선 해방(Eyes-Free) 백그라운드 핸즈프리 음성 길 안내 (5 pt / 총 26h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-C2-1**: OSRM/ORS steps 기반 턴 안내 문구 및 노면 속성 파싱 모듈 구현 (6h / Member D)
  * **TASK-C2-2**: `expo-speech` TTS 엔진 연동 및 회전 30m 전 사전 음성 브리핑 송출 ("50m 앞 완만길 우회전") (8h / Member D)
  * **TASK-C2-3**: 소프트 비프음 알림 및 경로 이탈(Off-route) 감지 시 재탐색 음성 알림 구현 (6h / Member D)
  * **TASK-C2-4**: 스마트폰 화면 꺼짐 상태 실기기 음성 안내 연속성 테스트 (6h / Member D)

---

### [Epic D] 현장 위험 분석 및 재탐색

#### US-D1: Vision AI 기반 현장 턱·계단·보행 장애물 시각 분석 (5 pt / 총 26h)
* **담당**: Member B | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-D1-1**: 현장 위험물(높은 턱, 계단, 공사 잔해) 벤치마킹 이미지셋 구축 및 라벨링 (6h / Member B)
  * **TASK-D1-2**: Gemini 1.5 Flash Vision 프롬프트 엔지니어링 및 Structured JSON 스키마 고정 (8h / Member B)
  * **TASK-D1-3**: 모션 블러, 저조도 사진 입력 시 예외 처리 및 가이드 로직 구현 (6h / Member B)
  * **TASK-D1-4**: 이미지 업로드 REST API(`POST /api/v1/surface/inspect`) 연동 및 최적화 (6h / Member B)

#### US-D2: 현장 위험 구간 우회 및 동적 재탐색 (5 pt / 총 22h)
* **담당**: Member A, C | **스프린트**: Sprint 2 (Week 3~4)
* **세부 Task**:
  * **TASK-D2-1**: 위험 감지 좌표 기준 인접 링크 임시 차단(Block List) 핸들러 구현 (6h / Member C)
  * **TASK-D2-2**: 현재 위치에서 출발지 복귀 안전 우회 경로 재탐색 API 구현 (8h / Member C)
  * **TASK-D2-3**: 우회 사유 및 변경 사항 에이전트 브리핑 메시지 생성 체인 연동 (4h / Member A)
  * **TASK-D2-4**: 모바일 UI 상 우회 경로 갱신 인터랙션 E2E 검증 (4h / Member D, A)

---

### [Epic E] 산책 기록 및 Memory (Local-First)

#### US-E1: 백그라운드 GPS 위치 추적 및 실산책 경로 로컬 저장 (5 pt / 총 24h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-E1-1**: `expo-location`과 Android Foreground Service 연동 백그라운드 위치 추적기 구현 (8h / Member D)
  * **TASK-E1-2**: 스마트폰 화면을 끈 상태에서도 무중단 위치 수신 및 궤적 스냅 보정 (6h / Member D)
  * **TASK-E1-3**: 수집된 궤적과 자택 출발지 좌표를 `AsyncStorage` 로컬에만 저장 (6h / Member D)
  * **TASK-E1-4**: GPS 튀김 현상 완화(데드 레커닝 필터) 적용 (4h / Member D)

#### US-E2: 산책 종료 후 보행 체감 피드백 수집 및 로컬 통계 (3 pt / 총 12h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-E2-1**: 완주 결과 요약 인포그래픽 모달 컴포넌트 개발 (4h / Member D)
  * **TASK-E2-2**: 보행 만족도 점수 및 태그(계단 없음, 경사 편함 등) 입력 UI (4h / Member D)
  * **TASK-E2-3**: 최근 보행 피드백 누적 통계 `AsyncStorage` 적재 모듈 (4h / Member D)

#### US-E3: 로컬 누적 피드백 기반 무상태(Stateless) AI 추천 보정 (3 pt / 총 14h)
* **담당**: Member A, D | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-E3-1**: 클라이언트 로컬 최근 피드백을 추출해 요청 본문(`client_recent_feedback`)에 동봉 (4h / Member D)
  * **TASK-E3-2**: 부정 평가 수신 시 허용 경사도를 자동 하향하는 무상태 보정 체인 (6h / Member A)
  * **TASK-E3-3**: LangGraph Agent 시스템 프롬프트 맥락 주입 및 단위 검증 (4h / Member A)

---

### [Epic F & G] 기상/열 위험 및 커뮤니티

#### US-F1: 기상청 단기예보 연동 시간대별 열 위험 지수 안내 (3 pt / 총 14h)
* **담당**: Member E (Sub: Member C) | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-F1-1**: 기상청 단기예보 API 클라이언트 및 시간대별 기온/운량 파싱 (6h / Member E)
  * **TASK-F1-2**: 일사량 및 열 위험 지수(안전/주의/위험) 산출 모듈 개발 (4h / Member E)
  * **TASK-F1-3**: 플래너 상단 산책 골든타임 알림 카드 UI 렌더링 (4h / Member D)

#### US-G1: 출발 거점 연계 공영주차장(P&R) 코스 탐색 (2 pt / 총 10h)
* **담당**: Member C | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-G1-1**: 전국 공영주차장 공공데이터 API 클라이언트 및 좌표 검색 모듈 구현 (5h / Member C)
  * **TASK-G1-2**: 주차장 출입구 좌표 연계 순환 산책 코스 생성 엔드포인트 연동 (5h / Member C)

#### US-G2: 간편 이메일 가입 및 코스 공유 (출발지 200m 마스킹) (4 pt / 총 20h)
* **담당**: Member E, D | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-G2-1**: Supabase Auth 기반 간편 이메일 가입/로그인 모듈 (Auto-confirm) (4h / Member E)
  * **TASK-G2-2**: 커뮤니티 코스 공유 시 **출발지/도착지 200m 좌표 자동 마스킹(절단/블러링)** 파이프라인 (6h / Member D, E)
  * **TASK-G2-3**: `community_courses` 테이블 적재 및 공개 피드 조회 REST API 구현 (5h / Member E)
  * **TASK-G2-4**: 커뮤니티 피드 뷰 및 코스 좋아요(북마크) UI 컴포넌트 개발 (5h / Member D)

---

### [Epic H] 무중단 배포 & 실사용 검증

#### US-H1: EAS Build 1회 배포, EAS Update 무선 OTA 및 5인 CBT (5 pt / 총 32h)
* **담당**: Member E, 전원 | **스프린트**: Hardening (Week 4~5)
* **세부 Task**:
  * **TASK-H1-1**: **EAS Build 기반 테스터용 Android APK 1회 패키징 및 테스터 5인 배포** (8h / Member E)
  * **TASK-H1-2**: **EAS Update (`expo-updates`) GitHub Actions 연동 무선 OTA 배포 파이프라인 구축 및 실시간 핫픽스 검증** (8h / Member E)
  * **TASK-H1-3**: 실사용자 5인 대상 필드 테스트 수행 (주머니 속 핸즈프리 음성 안내, 계단 회피 적중률 검증) (10h / 전원)
  * **TASK-H1-4**: 수집된 설문 분석 및 핫픽스 OTA 배포, 최종 CBT 완료 보고서 작성 (6h / Member E, A)

---

## 3. 공수 집계 및 애자일 일정 매핑

### 3.1 에픽별 작업량 요약표

| 에픽 (Epic) | Story Points | 세부 Task 수 | 추정 공수 (Hours) | 비중 (%) |
|---|:---:|:---:|:---:|:---:|
| **Epic A. 산책 조건 입력 및 개인화** | 11 pt | 10개 | 54h | 14.5% |
| **Epic B. 무계단·완만 경사·그늘 우선 경로 생성** | 26 pt | 16개 | 124h | 33.3% |
| **Epic C. 모바일 인터페이스 & 백그라운드 음성 안내** | 10 pt | 8개 | 50h | 13.4% |
| **Epic D. 현장 위험 분석 및 재탐색** | 10 pt | 8개 | 48h | 12.9% |
| **Epic E. 산책 기록 및 Memory (Local-First)** | 11 pt | 10개 | 50h | 13.4% |
| **Epic F. 기상/열 위험 정보** | 3 pt | 3개 | 14h | 3.8% |
| **Epic G. 주차 및 커뮤니티 (이메일 Auth/마스킹)** | 6 pt | 6개 | 30h | 8.1% |
| **Epic H. 무중단 배포 & 실사용 검증 (EAS/OTA)** | 5 pt | 4개 | 32h | 8.6% |
| **합계** | **82 pt** | **65개 Task** | **372h** | **100.0%** |

### 3.2 팀원별 공수 배분 현황

| 담당자 | 주요 역할 | 담당 Task 공수 (Hours) | 주당 평균 공수 (5주 기준) |
|---|---|:---:|:---:|
| **Member A** | AI Agent / Product Logic Lead | 70h | 약 14.0h / 주 |
| **Member B** | Vision / Multimodal AI Lead | 52h | 약 10.4h / 주 |
| **Member C** | Backend / Routing / GIS Data Lead | 112h | 약 22.4h / 주 |
| **Member D** | Frontend / Mobile App Lead | 86h | 약 17.2h / 주 |
| **Member E** | Infra / Automation & QA Lead | 52h | 약 10.4h / 주 |
| **합계** | **5인 전원** | **372h** | **약 74.4h / 주 (팀 전체)** |

---

## 4. 전체 사용자 스토리 및 공수 총괄 요약표

| Story ID | 사용자 스토리 요약 | 담당자 | Story Points | Task 개수 | 총 추정 공수 (Hours) |
|:---:|---|:---:|:---:|:---:|:---:|
| **US-A1** | 대화형 자연어 산책 요청 및 조건 구조화 | Member A | 5 pt | 4개 | 24 h |
| **US-A2** | 반려견 프로필 로컬 등록 및 JSON 백업/복원 | Member D | 3 pt | 4개 | 14 h |
| **US-A3** | 목표 산책 시간/거리 기반 환산 (속도/슬라이더) | Member A, C | 3 pt | 3개 | 16 h |
| **US-B1** | 지도 데이터 기반 계단 구간 우선 회피 | Member C | 8 pt | 4개 | 34 h |
| **US-B2** | DEM 기반 완만 경사 우선 순환 경로 도출 | Member C | 5 pt | 4개 | 26 h |
| **US-B3** | 태양 위치 및 건물 형상 기반 시간대별 그늘 우선 평가 | Member C | 5 pt | 4개 | 28 h |
| **US-B4** | Routing API Adapter 연동 및 후보 경로 다요소 스코어링 | Member C, A | 8 pt | 4개 | 36 h |
| **US-C1** | React Native Maps 기반 구간별 색상 분기 경로 시각화 | Member D | 5 pt | 4개 | 24 h |
| **US-C2** | 시선 해방(Eyes-Free) 백그라운드 핸즈프리 음성 길 안내 | Member D | 5 pt | 4개 | 26 h |
| **US-D1** | Vision AI 기반 현장 턱·계단·보행 장애물 시각 분석 | Member B | 5 pt | 4개 | 26 h |
| **US-D2** | 현장 위험 구간 우회 및 동적 재탐색 | Member B, C | 5 pt | 4개 | 22 h |
| **US-E1** | 백그라운드 GPS 위치 추적 및 실산책 경로 로컬 저장 | Member D | 5 pt | 4개 | 24 h |
| **US-E2** | 산책 종료 후 보행 체감 피드백 수집 및 로컬 통계 | Member D | 3 pt | 3개 | 12 h |
| **US-E3** | 로컬 누적 피드백 기반 무상태(Stateless) AI 추천 보정 | Member A | 3 pt | 3개 | 14 h |
| **US-F1** | 기상청 단기예보 연동 시간대별 열 위험 지수 안내 | Member E | 3 pt | 4개 | 14 h |
| **US-G1** | 출발 거점 연계 공영주차장(P&R) 코스 탐색 | Member C, D | 2 pt | 3개 | 10 h |
| **US-G2** | 간편 이메일 가입 및 코스 공유 (출발지 200m 마스킹) | Member E, D | 4 pt | 4개 | 20 h |
| **US-H1** | EAS Build 1회 배포, EAS Update 무선 OTA 및 5인 CBT | 전원 (Lead: E) | 5 pt | 4개 | 32 h |
| **합계** | **18개 핵심 스토리** | **5인 전원** | **77 pt** | **68개 Task** | **372 h** |

---

## 5. 팀원별 총 개발 공수 요약 (Team Capacity Allocation)

* **Member A (AI Agent & Product Logic Lead)**: 78 h (US-A1, US-A3 일부, US-B4 일부, US-E3, US-H1)
* **Member B (Vision AI Lead)**: 56 h (US-D1, US-D2 일부, US-H1)
* **Member C (Backend / Routing / GIS Lead)**: 126 h (US-A3, US-B1, US-B2, US-B3, US-B4, US-D2 일부, US-G1 일부, US-H1)
* **Member D (Frontend / Mobile UX Lead)**: 96 h (US-A2, US-C1, US-C2, US-E1, US-E2, US-G1 일부, US-G2 일부, US-H1)
* **Member E (Infra / DevOps & QA Lead)**: 66 h (US-F1, US-G2, US-H1 총괄, CI/CD 자동화)
* **총 개발 공수 합계**: **372 Hours** (18개 스토리 완수, 5인 5주 일정 정합)

