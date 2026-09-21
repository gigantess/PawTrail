# 🐾 PawTrail 팀 빌딩 & 핵심 프로젝트 전략

> **"AI Native 관점의 선택과 집중"**  
> 5주라는 제한된 일정 내에 실제 사용 가능한 완성도 높은 제품을 구현하고 가치를 증명하기 위해 반드시 준수해야 할 팀 R&R 및 엔지니어링 실행 원칙입니다.

---

## 📌 1. 핵심 요약 (Executive Summary)

* **과정의 본질 증명**: 바닥부터 복잡한 GIS 알고리즘을 짜는 것이 아닌, **"사용자 문제를 정의하고 AI Agent가 외부 도구(Routing API, Steps, DEM, Shade, Vision)를 자율 제어해 해결하는 역량"**에 집중합니다.
* **4대 집중 전략**:
  1. **직접 A* 엔진 및 위성 CV 지양** ➔ **표준 Routing API Adapter 제어 & Steps/Slope/Shade 다요소 분석 결합**
  2. **화면 주시형 보행 위험 탈피** ➔ **React Native (Expo) 기반 시선 해방(Eyes-Free) 핸즈프리 음성 안내 & EAS 무중단 OTA 배포**
  3. **소셜 로그인 및 복잡한 서버 개인정보 축적 배제** ➔ **간단한 이메일 회원가입 & 개인정보 로컬 저장(Privacy-First Local Storage)**
  4. **과도한 스트리밍(SSE/WS) 인프라 지양** ➔ **안정적인 REST API + 5주 점진적 개발 및 5인 실사용자 필드 검증**
* **목표 달성성**: 도출된 **18개 사용자 스토리 (총 77 pt / 372h)**를 5인 전문 R&R과 애자일 스프린트로 5주 내 충분히 완주 가능.

---

## 🧭 2. 4대 기술 엔지니어링 전략

### 2.1 GIS 엔진 직접 코딩 ❌ ➔ Agent 도구 제어 & Routing Adapter ⭕
* C++ 수준의 지리 알고리즘을 바닥부터 구현하지 않고, `OpenRouteService`/`OSRM` 표준 라우팅 API Adapter를 연동하여 도로망 경로를 연산합니다.
* AI Agent는 반려견 조건과 산책 환경을 분석해 최적의 제약조건과 Waypoint를 결정하고 다요소 스코어링을 수행합니다.

### 2.2 화면 주시형 보행 위험 ❌ ➔ React Native (Expo) 기반 핸즈프리 음성 안내 & EAS OTA ⭕
* **시선 해방(Eyes-Free) & 두 손 자유(Hands-Free)**:
  - 한 손에 리드줄을 잡고 폰 화면을 들여다보며 걷는 위험한 보행을 탈피합니다.
  - **React Native (Expo SDK 51+) + Android Foreground Service**를 채택하여, 스마트폰을 주머니에 넣고 화면을 꺼두어도 백그라운드 GPS 수신 및 `expo-speech` TTS 기반 회전/안전 음성 안내(*"50m 앞 완만한 길입니다. 우회전하세요"*)를 제공합니다.
* **배포 및 유지보수 피로도 제로 (EAS Update OTA)**:
  - 테스터들의 재설치 번거로움을 없애기 위해 **EAS Build로 APK를 1회 배포**한 후, 모든 기능 수정 및 핫픽스는 **EAS Update (`expo-updates`)를 통해 무선 무점검 OTA**로 실시간 배포합니다.

### 2.3 소셜 로그인 및 서버 개인정보 DB ❌ ➔ 간단 이메일 가입 & 로컬 저장 ⭕
* 카카오/구글 소셜 로그인은 외부 개발자 센터 등록 및 도메인 검증, OAuth 심사 등 외부 병목이 큽니다.
* **Supabase Auth 기반의 간단한 이메일/비밀번호 가입(개발/CBT 중 Auto-confirm)**으로 인증을 단순화합니다.
* 자택 위치, 보행 궤적, 반려견 프로필 등 민감 정보는 **사용자의 폰(`AsyncStorage`)에만 저장**하여 서버 해킹 시에도 개인정보 유출을 원천 차단합니다.
* 서버는 오직 '커뮤니티 공개 코스(출발지 200m 마스킹)'와 '현장 위험 제보'만 가볍게 관리합니다.

### 2.4 복잡한 양방향 스트리밍 ❌ ➔ 예측 가능한 REST API & 5주 완결형 배포 ⭕
* SSE나 웹소켓 디버깅 병목을 배제하고, 예측 가능한 표준 REST API 구조를 준수합니다.
* 1~2주 차(코어 라우팅/Expo 세팅) $\to$ 3주 차(그늘/비전/음성 길 안내 엔진) $\to$ 4~5주 차(EAS 빌드/5인 실사용자 CBT 및 튜닝)의 5주 완결형 로드맵을 가동합니다.

---

## 👥 3. 5인 팀 R&R (역할과 책임) 명세

| 담당자 | 포지션 & 주요 역할 | 담당 범위 및 핵심 책임 | 관련 에픽 및 스토리 |
|:---:|---|---|---|
| **Member A** | **AI Agent / Product Logic Lead** | • LangGraph 기반 Walk Planning Agent 설계<br>• Pydantic V2 Strict Input Schema 및 상태 머신 수립<br>• 클라이언트 로컬 맥락(반려견 조건, 피드백) 기반 무상태(Stateless) 프롬프트 오케스트레이션<br>• 후보 경로 평가 코멘트 생성 및 가드레일 | Epic A (US-A1, US-A3)<br>Epic B (US-B4)<br>Epic D (US-D2)<br>Epic E (US-E3) |
| **Member B** | **Vision / Multimodal AI Lead** | • Gemini 1.5 Flash 기반 현장 시각적 위험물(턱, 계단, 장애물) 판독<br>• Structured JSON 출력 스키마 고정 및 판독 지연시간 최적화<br>• 저조도, 모션 블러 등 현장 사진 예외 처리 및 가이드<br>• 공원 종합안내판 출입 제한 구역 파싱 | Epic D (US-D1, US-D2) |
| **Member C** | **Backend / Routing / GIS Data Lead** | • FastAPI 백엔드 구축 및 Stateless REST API 엔드포인트 구현<br>• OpenRouteService / OSRM 라우팅 API Adapter 연동<br>• OSM Steps 데이터 필터링 및 DEM 경사도 분석 파이프라인<br>• SunCalc 태양각 및 건물 그림자 추정(Level 1~2) 모듈<br>• Candidate Route Scorer 랭킹 알고리즘 개발 | Epic A (US-A3)<br>Epic B (US-B1, US-B2, US-B3, US-B4)<br>Epic D (US-D2)<br>Epic G (US-G1) |
| **Member D** | **Frontend / Mobile App Lead** | • **React Native (Expo SDK 51+) 모바일 앱 구축**<br>• **Android Foreground Service + expo-speech 기반 시선 해방 핸즈프리 음성 안내 엔진 개발**<br>• react-native-maps 기반 구간별 색상 구분 Polyline 렌더링<br>• **AsyncStorage 로컬 스토리지 모듈(반려견 프로필, 개인 궤적, JSON 백업/복원)**<br>• 간편 이메일 회원가입/로그인 폼 및 앱 UI 웰니스 용어 준수 | Epic A (US-A2, US-A3)<br>Epic C (US-C1, US-C2)<br>Epic D (US-D2)<br>Epic E (US-E1, US-E2, US-E3)<br>Epic F (US-F1)<br>Epic G (US-G1, US-G2)<br>Epic H (US-H1) |
| **Member E** | **Infra / Automation & QA Lead** | • **EAS Build 기반 1회 Android APK 패키징 & EAS Update 무선 OTA 배포 파이프라인 구축**<br>• **Supabase Auth 간편 이메일 가입/로그인 연동 (Auto-confirm 활성화)**<br>• 커뮤니티 공개 코스(`community_courses`), 위험 제보(`hazard_reports`) 스키마 관리 및 200m 마스킹<br>• **기상청 단기예보 n8n 연동 및 최소 5인 실사용자 필드 테스트(CBT) 운영 리드** | Epic F (US-F1)<br>Epic G (US-G2)<br>Epic H (US-H1) |

---

## 🧠 4. PawTrail 핵심 AI 파이프라인

```mermaid
flowchart LR
    A[📱 로컬 반려견 정보 & 사용자 요청] --> B[FastAPI / LangGraph Agent]
    B --> C[Tools: Routing Adapter]
    C --> D[Steps / Slope / Shade 분석]
    D --> E[Candidate Route Scorer]
    E --> F[최종 안심 루프 코스 선정]
    F --> G[📱 React Native 지도 프리뷰]
    G --> H[주머니 속 핸즈프리 음성 안내<br/>expo-speech + OSRM Steps]
    H --> I[현장 위험 발견 시 Vision 판독]
    I -.->|우회 필요 시| B
    H --> J[📱 산책 완주 & 로컬 이력 저장]
    J -.->|선택 시: 출발지 마스킹 후| K[☁️ 커뮤니티 공개 코스 공유]
```

---

## 🚀 5. 팀 운영 및 실행 원칙

1. **시선과 두 손의 안전성 보장**: 스마트폰 화면을 보며 걷지 않도록, 백그라운드 음성 길 안내의 완성도를 최우선 검증합니다.
2. **배포 효율 극대화**: EAS Update OTA를 통해 코드 변경 시 테스터가 즉시 새로운 기능을 체감할 수 있도록 자동화합니다.
3. **프라이버시 기본 탑재 (Privacy by Design)**: 견주의 집 주소와 상세 궤적은 어떤 경우에도 서버 DB에 영구 저장하지 않으며 로컬에만 보관합니다.