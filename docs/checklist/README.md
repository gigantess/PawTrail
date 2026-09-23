# 📑 PawTrail 팀원별 AI Pair Programming 표준 체크리스트 가이드

본 디렉토리(`docs/checklist/`)는 **PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 에이전트 및 기록·공유 플랫폼)** 개발 시 팀원 5명이 AI(Gemini Code Assist, Claude, ChatGPT 등)와 페어 프로그래밍을 진행할 때 점검하고 준수해야 하는 **역할별 실천 체크리스트**를 담고 있습니다.

---

## 👥 1. 팀원별 체크리스트 목록 및 담당 영역

| 팀원 | 포지션 & 주요 역할 | 배정 공수 | 담당 사용자 스토리 | 전담 체크리스트 링크 |
|:---:|---|:---:|:---:|:---:|
| **Member A** | **PM & AI Agent Lead** | **65 h** (17.5%) | US-A1, US-A3, US-B4, US-D2, US-E3 (11개 Task) | [`Member_A_PM_and_AI_Agent_Lead.md`](./Member_A_PM_and_AI_Agent_Lead.md) |
| **Member B** | **AI & Spatial Data Engineer** | **71 h** (19.1%) | US-B1, US-B2, US-B3, US-D1, US-D2, US-F1, US-G1, US-G2 (14개 Task) | [`Member_B_AI_and_Spatial_Data_Engineer.md`](./Member_B_AI_and_Spatial_Data_Engineer.md) |
| **Member C** | **Backend & Spatial Routing Lead** | **91 h** (24.5%) | US-B1, US-B2, US-B3, US-B4, US-D2, US-F1, US-G1, US-G2 (14개 Task) | [`Member_C_Backend_and_Spatial_Routing_Lead.md`](./Member_C_Backend_and_Spatial_Routing_Lead.md) |
| **Member D** | **Frontend & Mobile App Lead** | **94 h** (25.3%) | US-A2, US-C1, US-C2, US-D2, US-E1, US-E2, US-E3, US-H1 (17개 Task) | [`Member_D_Frontend_and_Mobile_App_Lead.md`](./Member_D_Frontend_and_Mobile_App_Lead.md) |
| **Member E** | **UI/UX Designer & Product Experience Lead** | **51 h** (13.7%) | US-A2, US-A3, US-C1, US-E2, US-F1, US-G1, US-G2, US-H1 (12개 Task) | [`Member_E_UI_UX_Designer_and_Product_Experience_Lead.md`](./Member_E_UI_UX_Designer_and_Product_Experience_Lead.md) |
| **합계** | **5인 체제 전원** | **372 h** | **18개 핵심 스토리 (68개 Task)** | **전원 준수** |

---

## 🧭 2. 전 팀원 공통 AI Pair Programming 4대 핵심 원칙

1. **1인 1담당자 단일 배정 원칙 (Single Assignee Principle)**:
   - 68개 모든 Task는 오직 1명의 담당자만 배정되어 있으므로, AI와 페어링 시 자신의 책임 영역을 명확히 지정하고 의존성이 있는 타 팀원의 인터페이스(DTO)를 준수합니다.
2. **무상태(Stateless) & Local-First 프라이버시 원칙**:
   - 자택 좌표, 실시간 GPS 보행 궤적, 반려견 신체 정보는 클라이언트 `AsyncStorage`에만 보관하고 서버로 절대 무단 전송하지 않습니다.
   - 커뮤니티 공개 코스는 반드시 **출발지/도착지 반경 200m 공간 지터링(Spatial Jittering)**을 강제합니다.
3. **Gemini 차세대 가용 모델 체인 및 1.5 계열 원천 차단**:
   - 구형 `gemini-1.5` 계열은 사용할 수 없으므로 배제하며, 반드시 `GeminiModelSelector`를 통해 **`gemini-3.5-flash-lite` ➔ `gemini-3.1-flash-lite` ➔ `gemini-3.6-flash`** 순차 선택 체인을 적용합니다.
4. **긍정적 웰니스 카피라이팅 가드레일 (Wellness Copywriting)**:
   - 앱 UI, 음성 안내 스크립트, AI 프롬프트 전역에서 '슬개골 탈구', '관절염' 등 임상 질병 단어를 100% 배제하고, "관절 안심 케어", "폭신한 길 위주" 등 정서적 안정감을 주는 순화 언어를 사용합니다.

---

## 🤖 4. AI Pair Programming 자동 점검 시스템 (Automated Enactment)

본 체크리스트의 모든 항목은 팀원이 매번 일일이 문서를 열어보고 수동으로 점검하지 않아도 되도록, **IDE 및 에이전트 시스템 레벨에서 자동 강제(Enforced)**되도록 구성되어 있습니다:

- **자동 규칙 바인딩 경로**: [`.agents/rules/ai_pair_programming_rules.md`](file:///d:/코디세이/PawTrail/.agents/rules/ai_pair_programming_rules.md) 및 [`.gemini/GEMINI.md`](file:///d:/코디세이/PawTrail/.gemini/GEMINI.md)
- **작동 방식**:
  1. AI(Antigravity / Gemini)가 코드 작업 대상 파일(예: `backend/`, `frontend/`, `vision/` 등)을 식별하는 즉시 해당 역할의 체크리스트를 **사전 컨텍스트로 자동 로딩**합니다.
  2. 코드 생성 중 `gemini-1.5` 모델 호출이나 '슬개골 탈구' 등 임상 질병 단어, 계단 누락, 클린코드 임계치(250줄/40줄/복잡도 10) 위반이 감지되면 **AI가 스스로 코드를 교정(Self-Correction)**합니다.
  3. 코드 생성 완료 후 `pytest test_case/` 회귀 테스트 및 검증 체크를 수행하여 최종 산출물의 무결성을 자동 보장합니다.
