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

## 🧪 3. AI 페어링 후 필수 검증 절차 (TDD Verification)

모든 코드 생성 및 리팩토링 후에는 반드시 로컬 터미널에서 전체 TDD 테스트 스위트를 실행하여 회귀 버그(Regression)가 없음을 검증해야 합니다:

```bash
# 전체 테스트 스위트 실행 (74개 테스트 100% 통과 확인)
python -m pytest test_case/
```

- 테스트 실패 시, 즉시 AI에게 실패 원인 트레이스백(Traceback)을 피드백하여 수정합니다.
- 수정 완료 후 관련된 기획서(01), 아키텍처(04), 추적 매트릭스(07) 문서에 변경된 스키마를 동기화합니다.
