# [상세 구현 계획서] ShadowTrail 단계별 기술 구현 및 5인 협업 로드맵

## 1. 프로젝트 개요 및 팀 구성 (5인 권장 체계)

* **프로젝트명**: ShadowTrail (AI Native 반려견 맞춤형 안심 산책 에이전트)
* **목표**: 5주간 "문제 정의 → 서비스 설계 → AI Agent/워크플로우 구축 → 프론트엔드 연동 → 클라우드 배포 및 최소 5인 실사용자 피드백 반영"의 AI Native 개발 전 주기 완수
* **팀 규모**: 5인 (코디세이 Final Project 권장 인원)
* **팀원별 역할 분담 (R&R)**:
  * **Member A (팀장 / AI Agent Lead)**:
    - AI Agent(LangGraph/LangChain) 아키텍처 설계 및 ReAct 프롬프트 엔지니어링
    - Tool-calling 인터페이스 표준화, 전체 파이프라인 조율 및 프로젝트 관리(PM)
  * **Member B (AI / Vision & Multimodal Lead)**:
    - Vision 멀티모달(Gemini 1.5 Flash) 노면 분석 파이프라인 개발
    - 프롬프트 튜닝, Pydantic 기반 구조화된 JSON 파싱 및 비전 위험도 채점 엔진 구현
  * **Member C (Backend & GIS Engine Lead)**:
    - FastAPI 백엔드 구축 및 REST/WebSocket API 엔드포인트 구현
    - 건물 3D 및 태양 궤적(SunCalc) 연동 그늘 계산 모듈, PostGIS 기반 루프 라우팅 엔진 개발
  * **Member D (Frontend & UI/UX Lead)**:
    - 웹/모바일 반응형 프론트엔드(Next.js 또는 React Native Web) 개발
    - Mapbox/Leaflet 기반 노면별 색상 구분 경로 시각화 및 대화형 에이전트 인터페이스 구현
  * **Member E (Infra, Automation & QA Lead)**:
    - n8n 기반 기상청 지면열 연동 일일 산책 골든타임 알림 워크플로우 구축
    - Supabase(PostgreSQL + pgvector) Long-term Memory DB 및 Vercel/Render 배포 자동화(CI/CD)
    - 실사용자 5인 이상 필드 CBT 운영, 피드백 수집 및 분석 리포트 총괄

---

## 2. 주차별 상세 구현 로드맵 (5주 스프린트)

```
[Week 1: 기반 인프라 & 도메인 데이터 파이프라인]
   │
[Week 2: AI Core 엔진 & 멀티모달/메모리 구현]
   │
[Week 3: 서비스 통합, 인터페이스 구현 & n8n 자동화]
   │
[Week 4: 외부 클라우드 배포 & 실사용자(5인+) CBT 수행]
   │
[Week 5: 사용자 피드백 반영 기능 고도화 & 최종 발표 준비]
```

---

### Week 1: 기반 인프라, 도메인 데이터 파이프라인 및 아키텍처 셋업
* **주간 공통 목표**: 개발 환경 통일, 인터페이스 규격(API/Data Schema) 확정, Git 협업 룰 세팅.

* **팀원별 세부 업무**:
  * **Member A (AI Agent)**:
    - Agent 상태 머신(LangGraph State) 정의 및 Agent-Tool 간 입출력 데이터 규격서 작성.
    - 시스템 프롬프트 초안 작성 (견종별 보행 속도 환산 및 제약 조건 주입 로직).
  * **Member B (Vision AI)**:
    - 노면 테스트 이미지 데이터셋(아스팔트, 흙, 잔디, 자갈, 공사 파쇄석 등 30장) 수집 및 레이블링 기준 수립.
    - Gemini API Key 발급 및 멀티모달 호출 테스트 스크립트 작성.
  * **Member C (Backend/GIS)**:
    - 테스트베드 구역(예: 대전 유성구 전민/신성동 또는 서울 마포구 상암동) OSM 보행 네트워크 데이터(.osm.pbf) 파싱 및 네트워크 그래프 구축.
    - Python `suncalc` 라이브러리를 활용한 시간대별 태양 고도/방위각 연산 유틸 함수 구현.
  * **Member D (Frontend)**:
    - Next.js / Tailwind CSS 프로젝트 보일러플레이트 구축 및 반응형 레이아웃 셋업.
    - Mapbox GL JS 또는 Leaflet 기반 기본 지도 렌더링 캔버스 구성.
  * **Member E (Infra/QA)**:
    - GitHub Organization 생성 및 Branch 전략(Git-flow: `main`, `develop`, `feature/*`), PR 템플릿 세팅.
    - Supabase 인스턴스 프로비저닝 (반려견 프로필, 산책 기록 테이블 DDL 정의).
    - n8n 셀프호스팅 또는 Cloud 워크스페이스 세팅.

---

### Week 2: AI Core 엔진 & 멀티모달/메모리 구현
* **주간 공통 목표**: 개별 AI 모듈(Agent, Vision, Memory)과 GIS 연산 모듈의 독립 구동 및 단위 테스트 완료.

* **팀원별 세부 업무**:
  * **Member A (AI Agent)**:
    - ReAct 패턴 기반 Walk Planning Agent 구현 (LangGraph).
    - 자율 호출 도구 3종 연동: `search_parking`, `calculate_shade_route`, `analyze_surface_image`.
    - 자연어 사용자 입력에서 견종, 시간, 장소, 노면 선호도 엔티티 추출 로직 고도화.
  * **Member B (Vision AI)**:
    - Gemini 1.5 Flash 기반 노면 진단 모듈 완성 (`SurfaceSafetyInspector`).
    - Pydantic을 활용한 JSON Structured Output 강제화 (`primary_surface`, `safety_score`, `hazard_detected`).
    - 단위 테스트 수행 (위험 노면 사진 입력 시 `safety_score < 50` 판정 검증).
  * **Member C (Backend/GIS)**:
    - 건물 높이 데이터를 반영한 2.5D 그림자 투영 알고리즘 작성.
    - 출발점 기준 다각형 경유지 샘플링을 통한 순환형(Loop) A* 라우팅 알고리즘 개발.
    - 링크별 노면 재질 및 시간대별 그늘 비율에 따른 가중치 페널티 계산 로직 결합.
  * **Member D (Frontend)**:
    - 에이전트 대화창 UI 구현 (메시지 스트리밍 렌더링, 제안 코스 카드 뷰).
    - 카메라/앨범 연동 노면 사진 업로드 컴포넌트 및 이미지 미리보기 구현.
  * **Member E (Infra/QA)**:
    - Supabase 기반 Long-term Memory 모듈 구현 (견공 프로필, 과거 산책 이력, 피드백 적재 CRUD API).
    - n8n 기상청 API 연동 노드 설계 (기온, 습도, 자외선 데이터 수집 파이프라인 구축).

---

### Week 3: 서비스 통합, 인터페이스 구현 & n8n 자동화
* **주간 공통 목표**: 프론트엔드-백엔드-AI 모듈 전체 E2E 연동 완료 및 내부 통합 테스트(Alpha Test).

* **팀원별 세부 업무**:
  * **Member A (AI Agent)**:
    - Long-term Memory와 Walk Planning Agent 결합 (과거 산책 피로도 및 질환 이력을 동적 프롬프트로 주입).
    - 예외 처리 로직 강화 (경로 생성 실패 시 대안 반경 확장 탐색 폴백).
  * **Member B (Vision AI)**:
    - 비전 분석 결과를 GIS 엔진의 링크 가중치로 동적 피드백하는 핸들러 구현.
    - 분석 결과 설명용 AI 코멘트 템플릿 최적화 ("소형견 발바닥 화상 주의 구간").
  * **Member C (Backend/GIS)**:
    - 공공데이터포털 전국공영주차장 실시간 API 연동 및 P&R(주차장 출발/복귀) 코스 추천 모듈 완성.
    - FastAPI 라우터와 Agent 파이프라인 통합 (비동기 스트리밍 SSE 엔드포인트 구현).
  * **Member D (Frontend)**:
    - 지도 상에 추천 경로 Polyline 표출 (잔디: 초록, 흙: 갈색, 아스팔트: 회색으로 구간별 분기 렌더링).
    - 코스 요약 인포그래픽 카드 완성 (총 거리, 소요 시간, 그늘 비율 %, 흙길 비율 %).
  * **Member E (Infra/QA)**:
    - n8n 워크플로우 완성: 매일 오전 지면 온도 추정 수식을 실행하고, 지면열 안전 시간대에 알림 웹훅 발송.
    - 통합 E2E 테스트 시나리오 작성 및 API 부하/에러 모니터링 셋업.

---

### Week 4: 외부 클라우드 배포 & 실사용자(5인+) CBT 수행
* **주간 공통 목표**: 외부 접근 가능한 퍼블릭 배포 완료, 실사용자 5인 이상 섭외 및 필드 테스트 수행.

* **팀원별 세부 업무**:
  * **Member A (AI Agent)**:
    - 실제 사용자 프롬프트 패턴 모니터링 및 프롬프트 인젝션 방어/안내 가이드 보강.
    - AI 윤리 고지 팝업 연동 ("본 산책로는 AI 시뮬레이션 결과입니다").
  * **Member B (Vision AI)**:
    - 실사용자가 업로드한 현장 사진에 대한 비전 판독 정확도 검증 및 임계값 튜닝.
  * **Member C (Backend/GIS)**:
    - 외부 배포 환경(Render / Cloud Run) 백엔드 프로비저닝 및 CORS, SSL 인증서 설정.
    - 응답 속도 최적화 (경로 캐싱 및 인덱싱을 통해 Agent 생성 시간 6초 이내 달성).
  * **Member D (Frontend)**:
    - Vercel 기반 프론트엔드 프로덕션 배포 완료.
    - 산책 완료 후 실사용자 평가 입력 폼(별점, 만족도, 개선 요청 텍스트) 인앱 모듈 배포.
  * **Member E (Infra/QA) [핵심 주간]**:
    - **실사용자 CBT 운영**: 반려견 견주 5명 이상(소형견 2, 중/대형견 2, 노령/관절질환견 1) 섭외.
    - 테스터에게 배포 링크 전달 후 실제 동반 산책 1회 이상 수행 유도.
    - 구글 폼 및 인앱 피드백 수집 관리, 정량/정성 피드백 요약 대시보드 작성.

---

### Week 5: 피드백 반영 기능 고도화 & 최종 발표 산출물 정리
* **주간 공통 목표**: 사용자 피드백 기반 서비스 개선 배포, GitHub 문서화 및 포트폴리오 발표 자료 완비.

* **팀원별 세부 업무**:
  * **Member A (AI Agent)**:
    - 실사용자 피드백 반영: "경사가 심한 구간이 포함됨" 등의 의견을 수용하여 평지 우선 가중치 프롬프트 조정 및 재배포.
    - AI Agent 의사결정 근거 및 기술적 의사결정 과정 문서화.
  * **Member B (Vision AI)**:
    - 노면 위험도 판단 정확도 개선 (가로수 그늘 오분류 케이스 프롬프트 수정).
  * **Member C (Backend/GIS)**:
    - 피드백 반영: 산책로 회귀 거리 오차 허용범위 축소 (목표 거리 대비 ±10% 이내 튜닝).
    - 소스 코드 리팩토링 및 API Swagger 문서 최신화.
  * **Member D (Frontend)**:
    - 모바일 화면 가독성 개선 (산책 중 한 손 조작을 위한 하단 플로팅 컨트롤 바 보완).
    - 서비스 시연 시나리오 녹화 (GIF/동영상 에셋 제작).
  * **Member E (Infra/QA)**:
    - GitHub `README.md` 최종 정리 (아키텍처 다이어그램, 5인 R&R, 기술 스택, 실행 방법, CBT 피드백 반영 내역).
    - 최종 발표 슬라이드(PDF) 제작: 문제 정의, AI Native 아키텍처, 사용자 피드백 개선 전후 비교, 배포 URL 링크 기재.

---

## 3. GitHub 브랜치 전략 및 협업 규칙

* **브랜치 운용 (Git-flow 변형)**:
  - `main`: 상시 배포 가능한 프로덕션 브랜치 (Vercel/Render 자동 배포 연동)
  - `develop`: 통합 개발 브랜치
  - `feature/{member}-{feature-name}`: 팀원별 세부 작업 브랜치 (예: `feature/member-a-agent-routing`, `feature/member-b-vision-hazard`)
* **PR 및 코드 리뷰 규칙**:
  - 최소 1인 이상의 팀원 승인(Approve) 후 `develop` 브랜치에 Merge.
  - 모든 커밋 메시지는 Conventional Commits 규격 준수 (`feat:`, `fix:`, `docs:`, `refactor:`).
* **AI 도구 활용 원칙**:
  - Gemini Code Assist / Claude 등을 활용해 코드 생성 시 테스트 케이스를 동시 생성하여 검증 수행.
  - 생성된 코드의 의사결정 근거를 PR 본문에 명시.

---

## 4. 실사용자(5인) 피드백 수집 및 검증 시나리오

| 테스터 ID | 대상 반려견 특성 | 테스트 시나리오 | 수집 지표 | 피드백 반영 목표 (Week 5) |
|---|---|---|---|---|
| **Tester 1** | 말티즈 (4세, 슬개골 탈구 2기) | 낮 시간대 쿠션 노면(흙/잔디) 20분 코스 | 노면 만족도, 관절 부담 여부 | 아스팔트 페널티 가중치 2.5배 상향 |
| **Tester 2** | 골든 리트리버 (3세, 대형견) | 주차장 거점 40분 원정 산책 코스 | P&R 동선 편의성, 그늘 일치도 | 공영주차장 도보 접근 링크 최단거리 보정 |
| **Tester 3** | 푸들 (11세, 노령견) | 오후 2시 폭염 시간대 15분 그늘 코스 | 체감 지면열, 그늘 체감 비율 | 건물 그림자 외 식생 수관율(가로수) 가중치 보정 |
| **Tester 4** | 웰시코기 (5세, 일반 보행) | 자연어 에이전트 대화 생성 및 노면 사진 제보 | 에이전트 응답 속도, 비전 판독 정확도 | 비전 모델 Structured Output 파싱 안정화 |
| **Tester 5** | 비숑 프리제 (2세, 활동적) | n8n 산책 골든타임 알림 수신 후 산책 | 알림 적시성, 시간대 만족도 | 지면열 임계 기준 시간대 30분 앞당겨 알림 발송 |

---

## 5. 최종 산출물 체크리스트 (미션 요구사항 대비)

* [x] **기획서 및 기능 요구 명세서**: Markdown 및 PDF 정리 완료
* [x] **핵심 AI 기술 2개 이상 포함**: AI Agent, Vision 멀티모달, Long-term Memory, n8n 워크플로우 4종 적용
* [x] **외부 접근 가능한 서비스 배포**: Vercel(Front) + Render/Cloud Run(Back) 배포 URL 확보
* [x] **최소 5인 이상 실사용자 테스트 및 피드백 반영**: CBT 설문 결과 및 Week 5 개선 내역 명시
* [x] **GitHub 버전 관리 및 문서화**: 5인 R&R, 아키텍처 다이어그램, 설치/실행 가이드 완비
* [x] **발표 자료 준비**: 최종 발표 PDF 슬라이드 및 시연 영상 링크 첨부
