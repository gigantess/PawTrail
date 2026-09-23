# 📋 [Member A] PM & AI Agent Lead — AI Pair Programming 체크리스트

## 1. 역할 개요 및 미션
- **역할 (Role)**: PM & AI Agent Lead
- **핵심 목표**: LangGraph 기반의 자연어 대화형 산책 플래너 오케스트레이션, Pydantic V2 Strict Schema를 통한 신뢰성 있는 Tool Calling, 체급별 표준 보행 모델 및 다요소 순환 라우팅 후보 채점기(Candidate Route Scorer) 연동을 총괄하며, 스프린트 일정과 프로젝트 정합성을 수호한다.
- **배정 공수 및 스토리**: 총 **65 Hours (11개 Task)** | **US-A1, US-A3, US-B4, US-D2, US-E3**

---

## 2. AI Pair Programming 기본 원칙 & 프롬프팅 가이드

### 2.1 AI 페어링 컨텍스트 주입 원칙
- **무상태(Stateless) 프롬프트 원칙**: AI에게 세션 메모리나 DB를 통한 사용자 개인정보 조회를 요구하지 말고, 클라이언트 요청 페이로드(`client_dog_context`, `client_recent_feedback`)를 통해 의도를 파싱하도록 컨텍스트를 주입한다.
- **엄격한 스키마 검증**: 모든 LLM 출력은 자유 서술형이 아닌 `WalkIntent`, `AgentState` 등 Pydantic V2 모델로 강제 변환되도록 프롬프트 가드레일을 설정한다.
- **안전 Fallback 기본값 강제**: 불명확한 발화나 파싱 실패 시 반드시 안전 기본값(20분, 완만 경사, 계단 회피, 그늘 우선)으로 수렴하도록 AI 코드 생성을 유도한다.

---

## 3. 단계별 AI Pair Programming 체크리스트

### 1단계: 작업 착수 전 준비 (Pre-Coding)
- [ ] **스토리 및 인수 조건(AC) 재확인**: `docs/03_PawTrail_Agile_User_Stories.md`의 US-A1, US-A3, US-B4, US-D2, US-E3 명세 확인.
- [ ] **관련 산출물 및 DTO 검토**: `test_case/test_walk_plan_agent_schema.py` 및 `docs/04_PawTrail_Architecture_Design.md`의 `AgentState` 정의 확인.
- [ ] **AI 프롬프트 작성 준비**: LLM에 전달할 시스템 프롬프트(의도 추출 4대 요소: `TargetDuration`, `AvoidStairs`, `SlopePreference`, `ShadePriority`) 구조화.

### 2단계: AI 코드 생성 및 페어링 (During Coding)
- [ ] **LangGraph ReAct 상태 머신 구현 (TASK-A1-1)**:
  - [ ] StateGraph 노드 분기(`parse_intent` ➔ `call_tools` ➔ `score_candidates` ➔ `generate_briefing`)가 순환 루프 없이 명확히 종료되는가?
  - [ ] 불필요한 LLM 호출을 줄이기 위한 조건부 엣지(Conditional Edge)가 올바르게 설정되었는가?
- [ ] **자연어 의도 파싱 프롬프트 엔지니어링 (TASK-A1-2, A1-3)**:
  - [ ] 모호한 질의("그냥 조금 걷고 싶어") 입력 시 기본 20분/완만/계단회피로 정상 Fallback되는가?
  - [ ] 10~90분 슬라이더 범위를 벗어난 비정상 입력에 대해 클램핑(Clamping) 또는 유효성 에러를 처리하는가?
- [ ] **체급별 보행 속도 상수 및 거리 환산 모델 (TASK-A3-2, A3-3)**:
  - [ ] 소형견(2.8 km/h), 중형견(3.6 km/h), 대형견(4.2 km/h), 노령견/관절안심(2.2 km/h) 상수가 전 문서와 100% 일치하는가?
  - [ ] 생성된 루프 경로의 예상 소요 시간이 목표 시간 대비 오차 $\pm 15\%$ 이내로 수렴하는가?
- [ ] **Candidate Route Scorer 랭킹 알고리즘 연동 (TASK-B4-3, B4-4)**:
  - [ ] 계단(30점) + 경사도(30점) + 그늘(20점) + 시간 오차(20점) 100점 만점 채점 산식이 수학적으로 정확한가?
  - [ ] 최적 코스 선정 후 견주에게 친절한 '추천 사유 브리핑'(예: *"계단이 전혀 없고 65% 그늘길인 완만한 코스를 추천합니다"*)이 생성되는가?
- [ ] **무상태 피드백 가중치 보정 (TASK-E3-2, E3-3)**:
  - [ ] 클라이언트의 "경사 불만족" 피드백 수신 시 최대 허용 경사도를 1~2% 동적 하향 조정하는 파라미터 어댑터가 작동하는가?
- [ ] **클린코드 가드레일 준수**:
  - [ ] 단일 파일 250줄 이하, 함수 40줄 이하, 인지 복잡도 10 이하를 준수하는가?
  - [ ] 모든 함수 및 클래스에 명확한 타입 힌팅(`typing`)과 독스트링이 작성되었는가?

### 3단계: 단위 테스트 및 검증 (Testing & Verification)
- [ ] **TDD 테스트 스위트 실행**:
  ```bash
  python -m pytest test_case/test_walk_plan_agent_schema.py -v
  python -m pytest test_case/test_loop_target_duration.py -v
  ```
- [ ] **엔티티 추출률 검증**: 모의 견주 발화 10종에 대해 85% 이상의 엔티티 추출 정확도를 달성하는가?
- [ ] **회귀 테스트(Regression Test)**: 전체 74개 테스트 스위트 실행 시 100% 통과하는가?

### 4단계: 산출물 동기화 및 형상 관리 (Post-Coding & Review)
- [ ] **문서 정합성 확인**: API 스키마 변경 시 `docs/04_PawTrail_Architecture_Design.md` 및 `07_PawTrail_Traceability_Matrix.md` 즉시 갱신.
- [ ] **질병 용어 전면 배제 검사**: 프롬프트 템플릿 및 추천 브리핑 메시지에 '슬개골 탈구' 등 임상 질병 단어가 0건인가? ("관절 안심 케어", "폭신한 길"로 순화).

---

## 4. 핵심 안티패턴 (주의해야 할 금기사항)
1. ❌ **서버 DB에 견주 개인정보 영구 저장 금지**: 자택 좌표나 반려견 프로필을 서버에 영구 보관하는 코드를 작성하지 말 것 (Local-First 원칙 위반).
2. ❌ **비구조화된 텍스트 응답 금지**: 라우터나 클라이언트로 전달되는 응답에 정규 스키마 없이 임의의 문자열을 반환하지 말 것.
3. ❌ **무한 Tool Calling 루프 방치 금지**: LangGraph 상태 머신에 최대 반복 횟수(Max Iterations: 5회 이하) 가드레일을 필히 설정할 것.
