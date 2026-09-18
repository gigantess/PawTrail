# [작업 분할 명세서] PawTrail 사용자 스토리별 상세 구현 Task 및 작업량 추정

## 1. 개요 및 추정 기준

* **프로젝트명**: PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 에이전트 및 기록·공유 플랫폼)
* **목적**: 13개 사용자 스토리(US-01 ~ US-13)를 실제 개발 가능한 단위의 하위 Task로 분할하고, 애자일 추정치(Story Points, 공수 Hours) 및 담당자를 지정하여 5주 스프린트 수행의 명확한 실행 지침 제공.
* **작업량 단위 기준**:
  - **스토리 포인트 (Story Points)**: 사용자 스토리 단위 (피보나치 1, 2, 3, 5, 8 pt)
  - **Task 추정 공수 (Estimated Hours)**: 세부 구현 작업 단위 (순수 개발 시간 기준, 1 MD = 8 시간)
  - **팀 구성 (5인)**:
    - Member A (AI Agent & Workflow Lead)
    - Member B (AI / Vision & Multimodal Lead)
    - Member C (Backend & Spatial Routing Lead)
    - Member D (Frontend & UI/UX Lead)
    - Member E (Infra, Automation & QA Lead)

---

## 2. 사용자 스토리별 세부 구현 Task 명세

### [Epic 1] 노면 맞춤형 AI 산책 플래닝

#### US-01: 대화형 산책 목표 및 조건 입력 (5 pt / 총 24h)
* **담당**: Member A (Sub: Member D) | **스프린트**: Sprint 1 (Week 1)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-01-1**: LangGraph Agent 상태 그래프 스키마(`StateGraph`, `AgentState`) 정의 (4h / Member A)
    - 대화 메시지 목록, 견종, 산책 시간, 선호 노면, 생성된 경로 ID 등 상태 변수 설계.
  * **TASK-01-2**: 엔티티 추출 프롬프트 엔지니어링 및 Few-shot 템플릿 작성 (6h / Member A)
    - 사용자 자연어 발화에서 목표 시간(분), 반려견 특성(나이, 질환), 출발지를 추출하는 ReAct 프롬프트 구성.
  * **TASK-01-3**: Pydantic V2 Strict Input Schema 및 필수 항목 누락 시 Clarification 대화 루프 구현 (6h / Member A)
    - 필수 인자 미충족 시 "몇 분 정도 산책을 원하시나요?" 형태의 되물음 노드 분기 처리.
  * **TASK-01-4**: FastAPI 비동기 REST API 엔드포인트 연동 및 모의 발화 10종 단위 테스트 (8h / Member A)
    - Agent의 요청/응답 처리 및 단위 테스트 자동화 스크립트 작성 (안정적인 REST 구조 우선).

#### US-02: 사용자 선호 노면 재질 선택 및 가중치 적용 (5 pt / 총 28h)
* **담당**: Member C (Sub: Member A, D) | **스프린트**: Sprint 1 (Week 2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-02-1**: 노면 재질별 기본 비용 가중치($W_{\text{base}}$) 상수 테이블 설계 (4h / Member C)
    - `dirt`: 0.6, `grass`: 0.6, `rubber`: 0.7, `paved`: 1.0, `asphalt`: 2.5, `gravel`: 3.5.
  * **TASK-02-2**: 사용자 선택 노면 할인 계수($W_{\text{pref}} = 0.4 \sim 0.5$) 동적 적용 모듈 구현 (8h / Member C)
    - 사용자 선택 노면(예: 흙길, 잔디길)에 할인 가중치를 부여하고 비선호 노면은 페널티를 곱하는 비용 계산 수식 구현.
  * **TASK-02-3**: AI Agent 도구 `generate_loop_route` 파라미터에 `preferred_surfaces` 바인딩 (6h / Member A)
    - Agent가 추출한 선호 노면 리스트를 라우팅 도구의 입력 인자로 엄격 매핑.
  * **TASK-02-4**: 선호 노면별(흙길 우선 vs 보도블록 우선) 대조 라우팅 단위 테스트 및 맵 뷰어 검증 (10h / Member C)
    - 동일 출발 좌표에서 선호도 옵션에 따라 분기된 경로가 정상 생성되는지 검증 리포트 작성.

#### US-03: 순환형(Loop) 산책 경로 생성 및 노면 추정 보정 (8 pt / 총 38h)
* **담당**: Member C, A | **스프린트**: Sprint 1 (Week 1~2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-03-1**: 테스트베드 OSM 도로망(.pbf) 파싱 및 NetworkX 그래프/인덱스 적재 파이프라인 구축 (10h / Member C)
    - 도보 통행 가능 링크(`highway=footway, pedestrian, path`) 추출 및 지오메트리 변환.
  * **TASK-03-2**: OSM `surface` 결측치 Fallback 추정 규칙 모듈 구현 (8h / Member C)
    - 공원 경계 내부 $\to$ `dirt`, 보행자길 $\to$ `paved`, 일반도로 $\to$ `asphalt` 매핑 및 `surface_source: estimated` 메타데이터 유지.
  * **TASK-03-3**: 다각형 경유지(Waypoint) 샘플링 및 Routing API(ORS/OSRM) 연동 순환 루프 생성 모듈 개발 (12h / Member C)
    - 단순 왕복(U턴) 방지 및 목표 거리 대비 $\pm 15\%$ 허용 오차 내 대안 루프 경로 산출.
  * **TASK-03-4**: 라우터 벤치마크 테스트 및 경로 생성 시간 2초 이내 최적화 (8h / Member C)
    - Routing Provider 어댑터 구조 적용 및 캐싱을 통한 지연시간 최소화.

---

### [Epic 2] 비전 멀티모달 현장 안전 진단

#### US-04: 비전 멀티모달 현장 노면 시각적 위험도 판독 (5 pt / 총 26h)
* **담당**: Member B | **스프린트**: Sprint 1 (Week 1~2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-04-1**: 노면 분류용 테스트 이미지셋(30장) 수집 및 Ground Truth 데이터셋 구축 (6h / Member B)
    - 흙, 잔디, 아스팔트, 자갈, 깨진 유리, 공사 잔해 등 클래스별 샘플 라벨링.
  * **TASK-04-2**: Gemini 1.5 Flash 비전 프롬프트 설계 및 Few-shot 최적화 (8h / Member B)
    - 노면 유형 식별 및 시각적 위험물(유리, 뾰족한 파쇄석, 물 웅덩이, 파손) 검출 지침 명시 (※ 지면열은 기상 모델로 분리).
  * **TASK-04-3**: Pydantic 기반 Structured JSON Output 파서 및 0~100 안전 점수 알고리즘 구현 (6h / Member B)

    - `safety_score`, `primary_surface`, `hazard_detected`, `ai_comment` 스키마 고정.
  * **TASK-04-4**: 저조도/블러 사진 예외 처리 및 단위 테스트 자동화 (6h / Member B)
    - 신뢰도 저하 시 재촬영 안내 메시지 반환 및 이미지 20장 배치 평가 정확도 검증(85% 이상).

#### US-05: 위험 노면 식별 시 경로 재탐색(Rerouting) 피드백 (3 pt / 총 16h)
* **담당**: Member B, C | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-05-1**: 위험 판독 이벤트 수신 시 해당 도로 링크 가중치 5배 할증 핸들러 구현 (6h / Member C)
    - `safety_score < 50` 판정 시 해당 지점 링크를 임시 기피 링크로 업데이트.
  * **TASK-05-2**: AI Agent 재탐색 트리거 도구 연동 및 대안 경로 생성 체인 완성 (6h / Member A, B)
    - 위험 구간 우회 사유를 자연어 코멘트로 생성하고 프론트엔드로 푸시.
  * **TASK-05-3**: 사진 업로드부터 우회 경로 반환까지 E2E 통합 테스트 수행 (4h / Member B, C)
    - 3초 이내에 우회 Polyline이 정상 렌더링되는지 확인.

---

### [Epic 3] 개인화 Long-term Memory

#### US-06: 반려견 건강 프로필 및 과거 산책 이력 기억 (3 pt / 총 18h)
* **담당**: Member E (Sub: Member A) | **스프린트**: Sprint 1 (Week 2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-06-1**: Supabase 테이블 DDL 설계 (`users`, `dogs`, `walk_history`, `feedback`) (4h / Member E)
    - 견종, 슬개골 질환 단계, 선호 노면 배열, 산책 거리/시간/노면비율 필드 구성.
  * **TASK-06-2**: Long-term Memory 조회/적재 FastAPI 비동기 CRUD 모듈 구현 (6h / Member E)
    - 유저 세션별 반려견 프로필 및 최근 5회 산책 요약 데이터 캐싱 및 조회 함수 작성.
  * **TASK-06-3**: LangGraph Agent 노드 내 이전 산책 맥락(피로도, 선호도) 동적 인젝션 (8h / Member A)
    - "지난 산책에서 언덕을 힘들어함" 피드백을 시스템 프롬프트의 동적 제약조건으로 주입.

---

### [Epic 4] 서비스 인터페이스 & 외부 배포

#### US-07: 지도 기반 추천 경로 시각화 및 외부 길찾기 연동 (5 pt / 총 26h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-07-1**: Mapbox GL JS 맵 연동 및 노면별 색상 구분 Polyline 렌더링 (8h / Member D)
    - 잔디(초록), 흙(갈색), 탄성포장(주황), 아스팔트(회색) 분기 렌더링.
  * **TASK-07-2**: 코스 요약 카드 UI 구현 (거리, 시간, 선호 노면 비율 % 표시) (6h / Member D)
    - 반응형 바텀시트 및 노면 달성 예상치 프로그레스 바 제작.
  * **TASK-07-3**: 네이버지도 / 카카오맵 도보 길찾기 외부 딥링크 연동 버튼 구현 (4h / Member D)
    - 출발지/도착지 좌표를 쿼리스트링으로 조합해 상용 지도 앱 즉시 실행.
  * **TASK-07-4**: 모바일 Safari / Chrome 크로스 브라우징 반응형 레이아웃 튜닝 (8h / Member D)
    - 뷰포트 높이(dvh) 및 터치 제스처 최적화.

#### US-08: 주머니 보관 연속 GPS 트래킹 및 선호 노면 달성률 기록 (5 pt / 총 26h)
* **담당**: Member D (Sub: Member E) | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-08-1**: Screen Wake Lock API & 포켓 모드 기반 연속 위치 트래커 및 지도 궤적 표시 (8h / Member D)
    - `navigator.wakeLock` 연동으로 화면 꺼짐 방지 및 오터치 방지 '다크 락스크린(포켓 모드)' 오버레이 제공.
    - 화면 복귀 또는 일시적 수신 지연 시 이전 좌표와 복귀 좌표 간 추천 경로 링크 스냅(Dead Reckoning) 선형 보간 처리.
  * **TASK-08-2**: 실시간 이동 거리, 경과 시간, 이동 속도 연산 타이머 모듈 개발 (6h / Member D)
    - Haversine 공식을 활용한 누적 보행 거리 계산.
  * **TASK-08-3**: 통과한 도로 링크의 노면 비율 집계 및 '선호 노면 달성률(%)' 산출 엔진 (6h / Member C, D)
    - 주행 궤적과 도로망 링크의 공간 매핑을 통해 실제 밟은 흙길/잔디길 비율 계산.
  * **TASK-08-4**: 산책 완료 시 요약 인포그래픽 생성 및 Supabase 기록 저장 연동 (6h / Member D, E)
    - 산책 결과 리포트 모달 제작 및 DB 적재.

#### US-09: 안심 코스 커뮤니티 피드 공유 및 피드백 제출 (3 pt / 총 16h)
* **담당**: Member D (Sub: Member E) | **스프린트**: Sprint 2 (Week 3~4)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-09-1**: 산책 완주 코스 커뮤니티 피드 리스트 UI 및 카드 뷰 컴포넌트 개발 (6h / Member D)
    - 다른 사용자가 완주한 코스 썸네일, 흙길 비율, 소요 시간 브라우징 기능.
  * **TASK-09-2**: 코스 별점(1~5점) 및 정성 피드백 텍스트 제출 폼 모달 구현 (4h / Member D)
    - 견주 후기 및 바닥 상태 한줄평 입력창 연동.
  * **TASK-09-3**: 피드백 데이터 DB 저장 및 개인정보 보호 좌표 마스킹 연동 (6h / Member E, D)
    - 저장된 피드백 목록 브라우징 및 출발지/집 주소 노출 방지(좌표 블러링) 처리.

#### US-10: 외부 접근 가능한 클라우드 배포 및 AI 윤리/면책 고지 (3 pt / 총 16h)
* **담당**: Member E (Sub: Member C) | **스프린트**: Sprint 2 (Week 4)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-10-1**: Vercel(Frontend) 및 Render(Backend) 배포 환경 구축 및 환경변수 관리 (6h / Member E)
    - SSL 인증서 적용 및 퍼블릭 HTTPS 도메인 연결.
  * **TASK-10-2**: CORS 허용 설정 및 프론트-백엔드 간 보안 통신 점검 (4h / Member C, E)
    - 배포 도메인 화이트리스트 등록 및 모바일 웹 API 호출 테스트.
  * **TASK-10-3**: AI 윤리 고지 문구 및 위치정보 수집 사전 동의 모달 구현 (6h / Member D, E)
    - "AI 분석 결과는 산책 계획을 위한 참고 정보이며 의료적 진단이 아닙니다" 상단 배너 배치 및 동의 토글 구현.

---

### [Epic 5] 실사용자(CBT) 검증 & 자동화 파이프라인

#### US-11: 최소 5인 이상 실사용자(견주) CBT 및 피드백 반영 (5 pt / 총 30h)
* **담당**: 전원 (Lead: Member E) | **스프린트**: Sprint 2 (Week 4) ~ Hardening (Week 5)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-11-1**: 견주 5인 섭외 및 페르소나별 테스트 시나리오/설문지(구글 폼) 설계 (6h / Member E)
    - 소형견(슬개골), 대형견(P&R), 노령견, 일반견, 활동견 5개 타깃 구성.
  * **TASK-11-2**: 5인 테스터 배포 링크 전달, 필드 산책 1회 이상 완주 가이드 및 결과 수집 (8h / 전원)
    - 실제 현장 산책 후 선호 노면 일치율, 비전 노면 판독 만족도 설문 데이터 확보.
  * **TASK-11-3**: 수집된 피드백 분석 및 정량/정성 개선 과제 도출 리포트 작성 (6h / Member E)
    - 설문 통계(만족도 평균) 및 개선점(예: "아스팔트 비중이 아직 높음") 도출.
  * **TASK-11-4**: 피드백 반영: $W_{\text{pref}}$ 가중치 강화 및 프롬프트 수정 재배포 (10h / Member A, C)
    - 선호 노면 할인 계수(0.5 $\to$ 0.35) 튜닝 및 GitHub 릴리즈 노트에 개선 내역 명시.

#### US-12: 기상청 지면열 연동 일일 최적 산책 골든타임 알림 (3 pt / 총 16h)
* **담당**: Member E | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-12-1**: 공공데이터포털 기상청 단기예보 API 연동 노드 구축 (n8n) (4h / Member E)
    - 기온, 일사량, 풍속 데이터 파싱.
  * **TASK-12-2**: 경험적 지면열 수지식 연산 노드 및 35℃ 이하 골든타임 계산 스크립트 작성 (6h / Member E)
    - 회귀식을 통해 시간대별 지면 예상 온도 슬롯 계산.
  * **TASK-12-3**: 골든타임 도달 30분 전 웹 푸시/디스코드 웹훅 알림 발송 파이프라인 완성 (6h / Member E)
    - 7일 연속 스케줄러 자동 실행 검증.

#### US-13: 출발 거점 연계 공영/민영 주차장(P&R) 코스 탐색 (2 pt / 총 12h)
* **담당**: Member C | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-13-1**: 전국공영주차장표준데이터 API 호출 및 반경 1km 주차장 좌표 필터링 모듈 (4h / Member C)
    - 주차장명, 주차면수, 유무료 정보 파싱.
  * **TASK-13-2**: 주차장 좌표를 시작/종료 노드로 설정하는 P&R 라우팅 도구 연동 (4h / Member C)
    - 주차장에서 바로 보행 네트워크로 진입하는 인터페이스 설계.
  * **TASK-13-3**: 주차장 미발견 시 현위치 기준 자동 폴백(Fallback) 예외 처리 (4h / Member C)
    - 반경 내 주차장 부재 시 에러 없이 현위치 순환 코스로 전환.

---

## 3. 종합 공수 및 작업량 집계표

| Story ID | 사용자 스토리 요약 | 담당자 | Story Points | Task 개수 | 총 추정 공수 (Hours) |
|:---:|---|:---:|:---:|:---:|:---:|
| **US-01** | 대화형 산책 목표 및 조건 입력 | Member A | 5 pt | 4개 | 24 h |
| **US-02** | 사용자 선호 노면 재질 선택 및 가중치 적용 | Member C, A | 5 pt | 4개 | 28 h |
| **US-03** | 순환형(Loop) A* 경로 생성 및 결측 보정 | Member C | 8 pt | 4개 | 38 h |
| **US-04** | 비전 멀티모달 노면 위험도 판독 | Member B | 5 pt | 4개 | 26 h |
| **US-05** | 위험 노면 식별 시 경로 재탐색 피드백 | Member B, C | 3 pt | 3개 | 16 h |
| **US-06** | 반려견 프로필 및 산책 이력 기억 (Memory) | Member E, A | 3 pt | 3개 | 18 h |
| **US-07** | 지도 시각화 및 외부 길찾기 연동 | Member D | 5 pt | 4개 | 26 h |
| **US-08** | 실시간 GPS 트래킹 및 선호 노면 달성률 | Member D, C | 5 pt | 4개 | 26 h |
| **US-09** | 커뮤니티 피드 공유 및 피드백 제출 | Member D, E | 3 pt | 3개 | 16 h |
| **US-10** | 클라우드 퍼블릭 배포 및 AI 윤리 고지 | Member E, C | 3 pt | 3개 | 16 h |
| **US-11** | 최소 5인 이상 실사용자 CBT 및 피드백 반영 | 전원 (Lead: E) | 5 pt | 4개 | 30 h |
| **US-12** | 기상청 지면열 연동 골든타임 알림 (n8n) | Member E | 3 pt | 3개 | 16 h |
| **US-13** | 공영/민영 주차장(P&R) 코스 탐색 | Member C | 2 pt | 3개 | 12 h |
| **합계** | **13개 사용자 스토리 전수 분할** | **5인 팀 전원** | **55 pt** | **47개 Task** | **292 h** |

---

## 4. 팀원별 담당 공수 배분 현황 (5인 밸런스 검증)

* **Member A (AI Agent Lead)**: 58 h (US-01, US-02 일부, US-06 일부, US-11)
* **Member B (Vision AI Lead)**: 48 h (US-04, US-05, US-11)
* **Member C (Backend/GIS Lead)**: 78 h (US-02, US-03, US-05 일부, US-10 일부, US-13)
* **Member D (Frontend Lead)**: 62 h (US-07, US-08, US-09, US-11)
* **Member E (Infra/QA Lead)**: 46 h (US-06, US-10, US-11 총괄, US-12)
* **총 개발 공수**: **292 Hours** (개발자 1인당 5주간 주당 평균 약 11.6시간 순수 구현 투입으로 일정 리스크 없이 완수 가능)
