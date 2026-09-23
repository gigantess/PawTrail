# 📋 [Member D] Frontend & Mobile App Lead — AI Pair Programming 체크리스트

## 1. 역할 개요 및 미션
- **역할 (Role)**: Frontend & Mobile App Lead
- **핵심 목표**: React Native (Expo SDK 51+) 기반 모바일 네이티브 앱 코어 아키텍처 구축, 스마트폰 주머니 속 화면 꺼짐 상태에서도 무중단 작동하는 **Android Foreground Service + expo-speech 기반 시선 해방(Eyes-Free) 핸즈프리 음성 길 안내 엔진**, react-native-maps 구간별 색상 분기 Polyline 렌더링, Local-First AsyncStorage 로컬 영속화 및 EAS Build/Update 무선 OTA 배포 체계를 총괄한다.
- **배정 공수 및 스토리**: 총 **94 Hours (17개 Task)** | **US-A2, US-C1, US-C2, US-D2, US-E1, US-E2, US-E3, US-H1**

---

## 2. AI Pair Programming 기본 원칙 & 프롬프팅 가이드

### 2.1 모바일 네이티브 & UX 엔지니어링 가이드라인
- **모바일 웹(PWA) 코드 혼입 차단**: AI가 브라우저 DOM API(`window`, `document`, HTML `<video>` 등)를 생성하지 않도록 사전에 `React Native Expo SDK 51+` 네이티브 컴포넌트(`View`, `Text`, `StyleSheet`)를 엄격히 지정한다.
- **시선 해방(Eyes-Free) 백그라운드 무중단 보장**: 산책 중 견주가 스마트폰을 주머니에 넣고 화면을 끈 상태에서도 OS에 의해 GPS/TTS 프로세스가 킬(Kill)되지 않도록 Android Foreground Service 및 Notification 채널을 필수 구현하도록 유도한다.
- **Local-First 프라이버시 바이 디자인**: 반려견 신체 정보(`@PawTrail:dog_profile`) 및 실시간 GPS 궤적(`@PawTrail:walk_history`)은 반드시 로컬 `AsyncStorage`에만 저장하고 서버로 무단 전송하는 코드를 원천 차단한다.

---

## 3. 단계별 AI Pair Programming 체크리스트

### 1단계: 작업 착수 전 준비 (Pre-Coding)
- [ ] **스토리 및 인수 조건(AC) 재확인**: `docs/03_PawTrail_Agile_User_Stories.md`의 US-C1, US-C2, US-A2, US-E1, US-H1 명세 확인.
- [ ] **테스트 스위트 참조**: `test_case/test_mobile_and_voice_navigation.py`, `test_case/test_walk_tracking_and_feedback.py` 로직 및 상수 확인.
- [ ] **디자인 시스템 토큰 연계**: Member E(디자이너)가 정의한 컬러 팔레트(완만 초록, 흙길 갈색, 탄성 주황, 일반 파랑, 위험 빨강) 및 컴포넌트 명세 파악.

### 2단계: AI 코드 생성 및 페어링 (During Coding)
- [ ] **시선 해방(Eyes-Free) 핸즈프리 음성 길 안내 (TASK-C2-1~4)**:
  - [ ] `expo-location` TaskManager가 Android Foreground Service 상에서 화면 꺼짐(Screen-off) 상태에도 1초 간격으로 GPS를 안정 수신하는가?
  - [ ] OSRM 턴바이턴 스텝 파싱을 거쳐 교차로/회전 **30m 전**에 `expo-speech` TTS 브리핑(*"50m 앞 완만한 흙길입니다. 우회전하세요"*)이 적시에 송출되는가?
  - [ ] 계획된 경로에서 **40m 이상 이탈** 시 이탈 감지 알림 및 재탐색 안내가 음성으로 송출되는가?
- [ ] **React Native Maps 구간별 색상 분기 렌더링 (TASK-C1-1, C1-2)**:
  - [ ] GeoJSON FeatureCollection 데이터를 파싱하여 노면 속성별로 정확한 색상 Polyline을 렌더링하는가?
    - 🌿 완만/그늘길: 초록 (`#10B981`)
    - 🍂 흙길: 갈색 (`#B45309`)
    - 🏃 탄성포장: 주황 (`#F97316`)
    - 🏢 보도블록/일반길: 파랑 (`#3B82F6`)
    - ⚠️ 높은 턱/주의구간: 빨강 (`#EF4444`)
  - [ ] 사용자 실시간 위치 마커 회전 및 부드러운 카메라 트래킹(Smoothing)이 적용되었는가?
- [ ] **Local-First 영속성 및 백업/복원 매니저 (TASK-A2-1, A2-3, E1-1~4)**:
  - [ ] `@PawTrail:dog_profile` 및 `@PawTrail:walk_history` 키 기반 `AsyncStorage` CRUD 모듈이 무결성을 보장하는가?
  - [ ] 기기 변경에 대비한 프로필 및 산책 기록의 **JSON 파일 내보내기/가져오기(Export/Import)** 기능이 정상 작동하는가?
  - [ ] 백그라운드 GPS 로깅 시 도심 빌딩 숲 GPS 튀김 완화 칼만 필터 및 도로망 스냅 보정이 적용되었는가?
- [ ] **EAS Build 및 EAS Update OTA 파이프라인 (TASK-H1-1, H1-2)**:
  - [ ] `eas.json` 설정에 따라 테스터용 APK 빌드가 1회 패키징되는가?
  - [ ] `expo-updates` 연동으로 앱 재설치 없이 실시간 무선 OTA 핫픽스 반영이 가능한가?
- [ ] **클린코드 가드레일 준수**:
  - [ ] 단일 컴포넌트/파일 250줄 이하, 커스텀 훅(`useVoiceNavigation`, `useLocationTracker` 등)으로 로직이 분리되었는가?
  - [ ] 인라인 스타일을 지양하고 `StyleSheet.create`로 스타일 토큰이 캡슐화되었는가?

### 3단계: 단위 테스트 및 검증 (Testing & Verification)
- [ ] **TDD 테스트 스위트 실행**:
  ```bash
  python -m pytest test_case/test_mobile_and_voice_navigation.py -v
  python -m pytest test_case/test_walk_tracking_and_feedback.py -v
  ```
- [ ] **Foreground Service 백그라운드 지속성 검증**:
  - 모바일 실기기 또는 에뮬레이터에서 화면을 잠근 상태로 5분간 GPS 좌표 수신 및 TTS 음성 발화 유지 검증.
- [ ] **JSON 내보내기/가져오기 무결성 검증**: Export된 JSON 파일 재로드 시 원본 데이터와 100% 일치 확인.

### 4단계: 산출물 동기화 및 형상 관리 (Post-Coding & Review)
- [ ] **디자인 시스템 일관성 검사**: Member E와 협업하여 다크 포켓 모드 및 UI 컴포넌트 스타일 규격 일치 확인.
- [ ] **웰니스 카피라이팅 전수 검사**: UI 텍스트 및 TTS 음성 스크립트 전역에서 임상 질병 단어(슬개골 탈구 등) 검출 0건 확인 ("관절 안심 케어", "폭신한 길" 통일).

---

## 4. 핵심 안티패턴 (주의해야 할 금기사항)
1. ❌ **웹 브라우저 Geolocation API 사용 금지**: `navigator.geolocation` 대신 반드시 `expo-location` Foreground Service를 사용할 것.
2. ❌ **메인 스레드 블로킹 연산 금지**: 지도 Polyline 대량 좌표 렌더링 시 메모이제이션(`useMemo`) 없이 리렌더링을 유발하지 말 것.
3. ❌ **화면 켜짐 강제(Screen-Always-On) 방치 금지**: 배터리 방전과 눈부심을 유발하지 않도록 주머니 보관용 **다크 포켓 모드(Dark Pocket Mode)**를 반드시 지원할 것.
