# [요구사항 정의서] PawTrail 애자일 사용자 스토리 및 완료 정의 (DoD)

## 1. 개요 및 애자일 프레임워크 기준
* **프로젝트명**: PawTrail (반려견 맞춤형 안심 산책 에이전트 및 핸즈프리 모바일 플랫폼)
* **목표**: 5주간 스크럼(Scrum) 기반으로 AI Agent 기반 무계단·완만 경사·그늘 우선 순환 라우팅, 현장 Vision 위험 분석, **React Native Expo 기반 시선 해방 핸즈프리 음성 길 안내**, **개인정보 로컬 보관(Local-First) & 간편 이메일 가입**, **EAS Build 1회 배포 및 EAS Update 무중단 OTA 배포**, 최소 5인 실사용자 필드 테스트를 완수.
* **핵심 엔지니어링 원칙**:
  - **시선 해방(Eyes-Free) & 두 손 자유(Hands-Free)**: `expo-location` Foreground Service + `expo-speech` TTS로 스마트폰을 주머니에 넣은 채 귀로 안내 수신.
  - **무중단 OTA 배포**: `EAS Build`로 APK 1회 배포 후, 모든 수정사항은 `EAS Update (`expo-updates`)` 무선 OTA로 실시간 배포.
  - **프라이버시 중심 로컬 저장 (Local-First)**: 자택 위치, 보행 GPS 궤적, 반려견 프로필은 **사용자 폰(`AsyncStorage`)에만 저장**.
  - **웰니스 용어 정책**: 앱 UI/프롬프트 내 질병 용어(슬개골 탈구 등)를 전면 배제하고 "관절 안심 폭신한 길", "관절 케어"로 순화.
* **추정 기준**: MoSCoW, 난이도(상/중/하), 스토리 포인트(피보나치 1, 2, 3, 5, 8 pt).

---

## 2. 사용자 스토리 및 백로그 요약표 (Epic A ~ Epic H)

| Story ID | 에픽 (Epic) | 사용자 스토리 요약 | 우선순위 | 난이도 | Story Points | 스프린트 | 담당 |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|
| **US-A1** | Epic A. 산책 조건 입력 및 개인화 | 대화형 자연어 산책 요청 및 조건 구조화 | Must | 중 | 5 pt | Sprint 1 | Member A |
| **US-A2** | Epic A. 산책 조건 입력 및 개인화 | 반려견 프로필 로컬 등록 및 JSON 백업/복원 (`AsyncStorage`) | Must | 하 | 3 pt | Sprint 1 | Member D |
| **US-A3** | Epic A. 산책 조건 입력 및 개인화 | 목표 산책 시간/거리 기반 환산 및 프리셋 설정 | Must | 중 | 3 pt | Sprint 1 | Member A, C |
| **US-B1** | Epic B. 안심 순환 경로 생성 | 지도 데이터 기반 확인된 계단 구간 우선 회피 | Must | 상 | 8 pt | Sprint 1 | Member C |
| **US-B2** | Epic B. 안심 순환 경로 생성 | DEM 기반 최대 경사도 제어 및 완만한 경사 우선 경로 도출 | Must | 상 | 5 pt | Sprint 1 | Member C |
| **US-B3** | Epic B. 안심 순환 경로 생성 | 태양 위치 및 건물 형상 기반 시간대별 그늘 우선 코스 평가 | Should | 상 | 5 pt | Sprint 2 | Member C |
| **US-B4** | Epic B. 안심 순환 경로 생성 | Routing API Adapter 연동 및 후보 경로 다요소 스코어링 | Must | 상 | 8 pt | Sprint 1 | Member C, A |
| **US-C1** | Epic C. 모바일 인터페이스 & 안내 | React Native Maps 기반 구간별 색상 분기 경로 시각화 | Must | 중 | 5 pt | Sprint 2 | Member D |
| **US-C2** | Epic C. 모바일 인터페이스 & 안내 | **시선 해방(Eyes-Free) 백그라운드 핸즈프리 음성 길 안내** | Must | 중상 | 5 pt | Sprint 2 | Member D |
| **US-D1** | Epic D. 현장 위험 분석 및 재탐색 | Vision AI 기반 현장 턱·계단·보행 장애물 시각 분석 | Must | 중 | 5 pt | Sprint 2 | Member B |
| **US-D2** | Epic D. 현장 위험 분석 및 재탐색 | 현장 위험 구간 우회 및 동적 재탐색(Reroute) | Should | 중상 | 5 pt | Sprint 2 | Member A, C |
| **US-E1** | Epic E. 산책 기록 및 Memory | 백그라운드 GPS 위치 추적 및 **실산책 경로 로컬 저장** | Must | 중 | 5 pt | Sprint 2 | Member D |
| **US-E2** | Epic E. 산책 기록 및 Memory | 산책 종료 후 보행 체감 피드백 수집 및 로컬 통계 | Must | 하 | 3 pt | Sprint 2 | Member D |
| **US-E3** | Epic E. 산책 기록 및 Memory | **로컬 누적 피드백 기반 무상태(Stateless) AI 추천 보정** | Must | 중 | 3 pt | Sprint 2 | Member A, D |
| **US-F1** | Epic F. 기상/열 위험 정보 | 기상청 단기예보 연동 시간대별 열 위험 지수 안내 | Should | 하 | 3 pt | Sprint 2 | Member E |
| **US-G1** | Epic G. 주차 및 커뮤니티 | 출발 거점 연계 공영주차장(P&R) 코스 탐색 | Should | 하 | 2 pt | Sprint 2 | Member C |
| **US-G2** | Epic G. 주차 및 커뮤니티 | **간편 이메일 가입 및 코스 공유 (출발지 200m 마스킹)** | Should | 중하 | 4 pt | Sprint 2 | Member E, D |
| **US-H1** | Epic H. 무중단 배포 & 실사용 검증 | **EAS Build 1회 배포, EAS Update 무선 OTA 및 5인 CBT** | Must | 중 | 5 pt | Hardening | Member E, 전원 |

* **총 Story Points**: **77 pt** (5인 팀 5주 완수)

---

## 3. 에픽별 상세 사용자 스토리 및 완료 정의 (DoD)

### [Epic A] 산책 조건 입력 및 개인화

#### US-A1: 대화형 자연어 산책 요청 및 조건 구조화
* **사용자 스토리**:  
  *견주로서*, 나는 "9살 노령견이라 계단은 피하고 완만한 길로 20분 정도 가볍게 산책하고 싶어"와 같이 자연어로 조건을 입력하고 싶다.
* **우선순위**: Must | **난이도**: 중 | **Story Points**: 5 pt | **담당**: Member A (AI Agent)
* **인수 조건**:
  1. LangGraph Agent가 사용자 발화에서 `TargetDuration`, `AvoidStairs`, `SlopePreference`, `ShadePriority` 엔티티를 85% 이상 정확도로 추출한다.
  2. 클라이언트 로컬에 저장된 반려견 프로필을 요청 본문에 실어 보내면 에이전트가 이를 즉시 병합하여 해석한다.
* **DoD**: 자연어 입력 10종에 대한 엔티티 추출 단위 테스트 통과.

#### US-A2: 반려견 프로필 로컬 등록 및 JSON 백업/복원
* **사용자 스토리**:  
  *견주로서*, 개인정보 유출 걱정 없이 우리 아이의 신체 정보를 내 폰에만 안전하게 보관하고 싶다.
* **우선순위**: Must | **난이도**: 하 | **Story Points**: 3 pt | **담당**: Member D (Frontend)
* **인수 조건**:
  1. 견종, 체중, 연령, 관절 안심 케어 선호도를 입력받아 **모바일 앱 로컬 스토리지(`AsyncStorage`)에만 저장**한다 (서버 DB 미전송).
  2. 앱 재설치나 기기 변경에 대비하여 **"프로필 JSON 파일 내보내기/가져오기"** 백업 기능을 제공한다.
  3. 앱 UI 및 온보딩 폼에서 "슬개골 탈구" 등 질병 용어 대신 "관절 안심 케어" 등 긍정적 웰니스 용어를 사용한다.
* **DoD**: 로컬 스토리지 CRUD 및 JSON 백업/가져오기 모듈 테스트 완료.

#### US-A3: 목표 산책 시간/거리 기반 환산 및 프리셋 설정
* **인수 조건**: 체급별 보행 속도(2.4 ~ 4.2 km/h)에 따라 목표 보행 거리를 자동 환산하고, 예상 소요 시간이 목표 시간의 $\pm 15\%$ 내로 수렴한다. (3 pt / Member A, C)

---

### [Epic B] 무계단·완만한 경사·그늘 우선 경로 생성

#### US-B1: 지도 데이터 기반 확인된 계단 구간 우선 회피 (8 pt / Member C)
* **인수 조건**: OSM `highway=steps` 링크를 감지해 배제(Hard Constraint)하며, `has_stairs: false`, `stairs_data_source: "osm"`, `stairs_confidence: 0.90` 메타데이터를 반환한다. (100% 무계단 보장 과장 배제)

#### US-B2: DEM 기반 최대 경사도 제어 및 완만한 경사 우선 경로 도출 (5 pt / Member C)
* **인수 조건**: DEM 고도 데이터를 통해 `max_slope_percent`를 산출하고 급경사($> 8\%$) 포함 링크를 페널티 처리한다. UI는 "매우 완만", "완만", "제한 없음"으로 추상화한다.

#### US-B3: 태양 위치 및 건물 형상 기반 시간대별 그늘 우선 평가 (5 pt / Member C)
* **인수 조건**: SunCalc 태양각과 건물 2.5D 높이 데이터를 결합하여 예상 그늘 비율(`shade_ratio`)을 계산하고 `shade_confidence`를 제공한다.

#### US-B4: Routing API Adapter 연동 및 후보 경로 다요소 스코어링 (8 pt / Member C, A)
* **인수 조건**: OpenRouteService / OSRM API Adapter를 통해 복수 순환 후보 경로(2~3개)를 수집하고 Candidate Route Scorer에서 최적 경로를 선정한다.

---

### [Epic C] 모바일 인터페이스 & 백그라운드 안내

#### US-C1: React Native Maps 기반 구간별 색상 분기 경로 시각화
* **사용자 스토리**:  
  *모바일 앱 사용자로서*, 생성된 산책로의 구간별 상태(완만/그늘, 일반, 급경사)를 지도 위에서 명확한 색상으로 확인하고 싶다.
* **우선순위**: Must | **난이도**: 중 | **Story Points**: 5 pt | **담당**: Member D (Frontend)
* **인수 조건**:
  1. `react-native-maps` 위에서 Polyline 색상 분기 렌더링 (그늘/완만: 초록, 일반: 파랑, 주의: 주황).
  2. 코스 요약 카드 및 OSRM 회전 안내 스텝 목록 뷰 제공.
* **DoD**: 모바일 실기기 지도 렌더링 검증 완료.

#### US-C2: 시선 해방(Eyes-Free) 백그라운드 핸즈프리 음성 길 안내
* **사용자 스토리**:  
  *하네스 줄을 잡고 걷는 견주로서*, 스마트폰을 주머니에 넣고 화면을 끈 채 귀로 음성 안내를 들으며 걷고 싶다. *그리하여* 시선과 두 손을 오롯이 반려견 안전에만 집중하기를 원한다.
* **우선순위**: Must | **난이도**: 중상 | **Story Points**: 5 pt | **담당**: Member D (Frontend)
* **인수 조건**:
  1. **Android Foreground Service**를 통해 화면이 꺼진 상태에서도 고정밀 GPS 위치 추적을 유지한다.
  2. `expo-speech` TTS 기반으로 회전 30m 전 사전 음성 브리핑(*"50m 앞 부드러운 완만길입니다. 우회전하세요"*) 및 노면 변화, 전방 턱 주의를 음성 송출한다.
  3. 경로 이탈 감지 시 부드러운 알림음과 함께 재탐색 안내를 송출한다.
* **DoD**: 화면 꺼짐 상태에서 턴 지점 도달 시 음성 TTS 정상 송출 실기기 검증 완료.

---

### [Epic D] 현장 위험 분석 및 재탐색

#### US-D1: Vision AI 기반 현장 턱·계단·보행 장애물 시각 분석 (5 pt / Member B)
* **인수 조건**: 현장 사진 업로드 시 Gemini 1.5 Flash가 높은 턱, 야외 계단, 공사 자재를 3초 이내에 시각 분석하여 구조화 JSON 스키마(`hazard_type`, `severity`, `route_action`)를 반환한다.

#### US-D2: 현장 위험 구간 우회 및 동적 재탐색 (5 pt / Member A, C)
* **인수 조건**: 위험 지점을 임시 차단 링크로 설정하고 안전 우회로를 3초 이내에 재탐색한다.

---

### [Epic E] 산책 기록 및 Memory (Local-First)

#### US-E1: 백그라운드 GPS 위치 추적 및 실산책 경로 로컬 저장 (5 pt / Member D)
* **인수 조건**: 주머니 속 화면 꺼짐 상태에서도 백그라운드 GPS 위치를 안정적으로 수집하며, **상세 궤적과 자택 좌표는 서버로 보내지 않고 폰 로컬(`AsyncStorage`)에만 저장**한다.

#### US-E2: 산책 종료 후 보행 체감 피드백 수집 및 로컬 통계 (3 pt / Member D)
* **인수 조건**: 완주 요약 카드 제공, 만족도 점수 및 간편 태그(계단 없음, 경사 편함 등)를 로컬에 저장.

#### US-E3: 로컬 누적 피드백 기반 무상태(Stateless) AI 추천 보정 (3 pt / Member A, D)
* **인수 조건**: 산책 요청 시 클라이언트가 로컬 최근 피드백 요약을 요청 바디에 담아 보내며, AI Agent는 서버 DB 조회 없이 요청 페이로드만으로 경사 허용 기준을 자동 보정한다.

---

### [Epic F & G] 기상/열 위험 및 커뮤니티

#### US-F1: 기상청 단기예보 연동 시간대별 열 위험 지수 안내 (3 pt / Member E)
* 기상청 예보 기반 열 위험 지수(안전/주의/위험) 산출 및 골든타임 카드 제공.

#### US-G1: 출발 거점 연계 공영주차장(P&R) 코스 탐색 (2 pt / Member C)
* 전국 공영주차장 출입구 좌표 연계 순환 코스 생성.

#### US-G2: 간편 이메일 가입 및 코스 공유 (출발지 200m 마스킹) (4 pt / Member E, D)
* **인수 조건**: Supabase Auth 간편 이메일 가입 지원 (Auto-confirm 적용). 커뮤니티 공유 시 **출발지/도착지 200m 구간 좌표 자동 마스킹(절단/블러링)** 적용 후 업로드.

---

### [Epic H] 무중단 배포 & 실사용 검증

#### US-H1: EAS Build 1회 배포, EAS Update 무선 OTA 및 5인 CBT (5 pt / Member E, 전원)
* **인수 조건**:
  1. React Native (Expo) 기반 **EAS Build로 테스터용 Android APK 1회 패키징 및 배포**.
  2. 이후 코드 수정 및 핫픽스는 **EAS Update (`expo-updates`) 무선 OTA**로 실시간 배포하여 재설치 없이 최신 버전 반영.
  3. 소형견/노령견 견주 5인 대상 필드 테스트 수행 (핸즈프리 음성 안내 및 무계단 코스 만족도 설문 수집).
* **DoD**: EAS Build APK 생성, EAS Update 무선 핫픽스 검증 및 5인 CBT 완료 보고서 작성.
