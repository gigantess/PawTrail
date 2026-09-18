# 📱 PawTrail 예상 사용 시나리오 스크린 명세서 (Screen Specifications)

본 문서는 **PawTrail (반려견 맞춤형 안심 노면 산책 플랫폼)**의 핵심 사용자 여정(User Journey)을 구현하기 위한 5대 주요 시나리오 화면의 UI 설계 및 기능 명세서입니다.

---

## 🗺️ 사용자 여정 흐름 (User Journey Flow)

```mermaid
graph LR
    S1["1. 산책 플래너<br/>(시간/노면 선택)"] -->|경로 생성| S2["2. 순환 경로 프리뷰<br/>(노면 Polyline & 딥링크)"]
    S2 -->|산책 시작| S3["3. 다크 포켓 모드<br/>(WakeLock & 슬라이드 언락)"]
    S3 -->|현장 촬영| S4["4. Gemini 노면 진단<br/>(안전 점수 & 우회)"]
    S4 -->|산책 완주| S5["5. 체크인 & 리포트<br/>(달성률 85% & 즐겨찾기)"]
```

---

## 1. 01_walk_planner.jpg (대화형 산책 플래너 & 시간/노면 선택)

![01_walk_planner](file:///d:/cody/final/docs/screens/01_walk_planner.jpg)

### 📌 화면 개요 및 목적
* **화면명**: 맞춤형 산책 플래너 (Walk Planner Screen)
* **연계 사용자 스토리**: **US-01** (대화형 조건 입력), **US-02** (선호 노면 선택), **US-06** (반려견 프로필 기억), **US-16** (목표 시간 맞춤형 코스)
* **핵심 기능**:
  1. **반려견 활성 프로필 카드**: 포메라니안 '코코' (슬개골 탈구 2기 주의 뱃지 표시).
  2. **목표 산책 시간(Target Duration) 선택**: 15분, 30분, 45분, 60분 원터치 칩 및 정밀 슬라이더 (US-16).
  3. **선호 노면 선택 칩**: 흙길(Dirt Trail), 잔디길(Grass Lawn), 탄성포장(Elastic Cushion), 보도블록(Paved Block).
  4. **AI 자연어 입력창**: *"슬개골 안 좋은 3살 코코 25분 폭신한 길로 짜줘"*와 같은 발화 지원.

---

## 2. 02_route_preview.jpg (지도 기반 안심 순환 경로 프리뷰)

![02_route_preview](file:///d:/cody/final/docs/screens/02_route_preview.jpg)

### 📌 화면 개요 및 목적
* **화면명**: 안심 순환 경로 프리뷰 (Route Preview Screen)
* **연계 사용자 스토리**: **US-03** (순환 루프 경로), **US-07** (지도 시각화 및 외부 길찾기 연동)
* **핵심 기능**:
  1. **노면별 색상 구분 Polyline**:
     - 초록색: 잔디길 (`#10B981`)
     - 갈색: 흙길 (`#92400E`)
     - 어두운 회색: 아스팔트 기피 구간
  2. **코스 요약 바텀시트**: 총 1.4km, 예상 25분, 푹신한 노면 비율 **82%** (흙길 60%, 잔디 22%).
  3. **원터치 산책 시작 버튼**: 한 손 조작을 고려한 화면 하단 40% 영역(Thumb Zone) 배치.
  4. **외부 네비게이션 딥링크**: 네이버 지도(`nmap://route/walk`), 카카오맵(`kakaomap://route`) 원터치 바로가기.

---

## 3. 03_pocket_mode.jpg (주머니 보관 초절전 다크 포켓 모드)

![03_pocket_mode](file:///d:/cody/final/docs/screens/03_pocket_mode.jpg)

### 📌 화면 개요 및 목적
* **화면명**: 초절전 다크 포켓 락스크린 (Dark Pocket Mode Screen)
* **연계 사용자 스토리**: **US-08** (주머니 보관 지속 GPS 트래킹), **UX 규칙 6장**
* **핵심 기능**:
  1. **Screen Wake Lock 활성화**: 산책 시작 시 화면 꺼짐 및 모바일 OS의 백그라운드 GPS 차단을 방지.
  2. **True Black (#000000) OLED 절전 UI**: 주머니 안에서 배터리 소모를 극소화.
  3. **실시간 보행 HUD**: 경과 시간(18:42), 이동 거리(1.15km), 현재 속도(3.6km/h) 고대비 텍스트 표시.
  4. **오터치 방지 '밀어서 잠금 해제(Slide to Unlock)'**: 주머니 속 옷감/피부 접촉에 의한 오작동을 차단하고, 한 손 엄지 슬라이드로 즉시 지도 화면 복귀.

---

## 4. 04_vision_inspection.jpg (Gemini Vision 현장 노면 실시간 진단)

![04_vision_inspection](file:///d:/cody/final/docs/screens/04_vision_inspection.jpg)

### 📌 화면 개요 및 목적
* **화면명**: Gemini Vision 노면 안전 진단 (Vision Safety Inspector)
* **연계 사용자 스토리**: **US-04** (비전 위험도 판독), **US-05** (위험 식별 시 우회 리라우팅)
* **핵심 기능**:
  1. **현장 카메라 뷰파인더**: 산책 중 마주친 바닥 사진 즉시 촬영/업로드.
  2. **안전 점수 원형 뱃지**: **88점 (SAFE)** 초록빛 HUD 렌더링.
  3. **위험물 태그 (Hazard Tags)**: `Small Gravel Detected (작은 파쇄석)`, `Dry Ground (건조한 바닥)`, `No Broken Glass (유리 파편 없음)`.
  4. **Gemini AI 진단 코멘트**: *"노면 가장자리에 작은 파쇄석이 관찰됩니다. 중앙의 부드러운 흙길로 유도하세요."*
  5. **원터치 조치 버튼**: 우회 경로 재탐색(`Reroute Path`) / 계속 걷기(`Continue Walk`).

---

## 5. 05_walk_report.jpg (산책 완료 체크인 & 안심 리포트)

![05_walk_report](file:///d:/cody/final/docs/screens/05_walk_report.jpg)

### 📌 화면 개요 및 목적
* **화면명**: 완주 체크인 및 산책 리포트 (Walk Completion & Check-In Report)
* **연계 사용자 스토리**: **US-08** (선호 노면 달성률), **US-09** (커뮤니티 피드 공유), **US-14** (나만의 코스 즐겨찾기)
* **핵심 기능**:
  1. **축하 헤더**: *"WALK COMPLETE! 코코가 푹신한 길을 걸었어요 🐾"*
  2. **선호 노면 달성률 게이지**: **85% 달성** (흙길 60%, 잔디 25%).
  3. **핵심 보행 통계**: 총 이동 거리 1.35km, 소요 시간 26분, 평균 속도 3.1km/h.
  4. **노면 만족도 평가**: 5점 만점 별점 평가 폼 (다음 산책 피드포워드 반영).
  5. **커뮤니티 피드 공유 버튼**: 견주 사생활 보호를 위한 **출발지/도착지 150m 안심 마스킹** 적용 락 아이콘.
  6. **나만의 안심 코스 즐겨찾기 (US-14)**: 검증된 코스를 원터치로 북마크에 저장.

---

> 🐾 **PawTrail Team**: 본 시나리오 스크린 명세는 프론트엔드 컴포넌트 개발(`components/`, `hooks/`) 및 5인 실사용자 CBT 현장 테스트의 기준 설계로 활용됩니다.
