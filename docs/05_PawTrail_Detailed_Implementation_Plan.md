# [상세 구현 계획서] PawTrail 단계별 구현 로드맵 및 5인 협업 실행 계획

## 1. 프로젝트 개요 및 팀 구성 (5인 애자일 체계)

* **프로젝트명**: PawTrail (반려견 맞춤형 안심 산책 에이전트 및 기록 플랫폼)
* **목표**: 5주간 실제 사용 가능한 1차 제품 버전의 구현 및 검증을 완료하고, AI Agent 기반 무계단·완만 경사·그늘 우선 순환 라우팅, 현장 Vision 위험 분석, 개인화 Memory, Foreground 위치 기록, 최소 5인 실사용자 필드 테스트를 완수.
* **팀원별 역할 분담 (R&R)**:
  * **Member A (AI Agent / Product Logic Lead)**:
    - LangGraph 기반 Walk Planning Agent 상태 머신 및 ReAct 프롬프트 설계 (US-A1, US-A3)
    - Pydantic V2 Strict Tool Schema 수립, Context Memory 맥락 주입 및 후보 경로 평가/설명 총괄
  * **Member B (Vision / Multimodal AI Lead)**:
    - Gemini 1.5 Flash 기반 현장 위험물(높은 턱, 계단, 공사 구간) 판독 파이프라인(`VisionHazardInspector`) 개발 (US-D1)
    - 공원 종합안내판 출입 제한 구역 판독 및 구조화 JSON 출력 규격화
  * **Member C (Backend / Routing / GIS Data Lead)**:
    - FastAPI 백엔드 구축 및 REST API 엔드포인트 구현
    - 전문 Routing API(OpenRouteService / OSRM) 어댑터 구축, OSM Steps 필터링, DEM 경사도 분석, SunCalc 건물 그림자 연산 모듈 개발 (US-B1, US-B2, US-B3, US-B4, US-G1)
  * **Member D (Frontend / Mobile UX Lead)**:
    - Next.js (App Router) 및 TypeScript 기반 모바일 반응형 웹/PWA 구축 (US-C1)
    - 지도 시각화(안전/경사/그늘 구간 색상 분기), Foreground GPS 위치 추적, 외부 지도(네이버/카카오) 길찾기 딥링크, 산책 UI 개발 (US-C2, US-E1, US-G2)
  * **Member E (Infra / Data / QA Lead)**:
    - Supabase(PostgreSQL) DDL 설계 및 Context Memory CRUD, Vercel/Cloud 배포 자동화 (US-A2, US-E2, US-E3)
    - 기상청 단기예보 연동 열 위험 모니터링 (US-F1)
    - **최소 5인 실사용자 필드 테스트 운영, 피드백 수집 및 품질 보증(QA) 총괄 (US-H1)**

---

## 2. 스프린트 일정 개요 (5주 로드맵)

```text
[Week 1] 코어 인프라 & 기본 라우팅 파이프라인 (환경 셋업, Auth, Routing API 연동, 기본 지도)
   │
[Week 2] 도메인 데이터 분석 및 후보 경로 평가 (Dog Profile, OSM Steps, DEM 경사도, Candidate Scorer)
   │
[Week 3] 환경 연산, 비전 위험 분석 & UI 결합 (Shade Estimation, Vision Hazard Inspector, 우회 재탐색, PWA 통합)
   │
[Week 4] 실사용 기능 완성 & 필드 테스트 착수 (Foreground GPS 기록, 열 위험 지수, 주차장 P&R, 5인 CBT)
   │
[Week 5] 안정화, 품질 개선 및 최종 배포 (피드백 반영 튜닝, 보안/성능 최적화, 운영 문서화)
```
* **총 Story Points**: **77 pt** (5인 팀 5주 완수)

---

## 3. 주차별 세부 구현 작업 (Week 1 ~ Week 5)

### Week 1: 코어 인프라 셋업, Auth & 기본 라우팅 연결
* **주간 목표**: 개발 환경 통일, Supabase Auth 및 DDL 배포, 기본 Agent 상태 머신 정의, Routing API 연동 및 웹 지도 기본 표시.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - LangGraph State 정의 (`messages`, `dog_context`, `plan_request`, `candidate_routes`).
    - 자연어 발화에서 산책 시간, 반려견 조건(나이, 관절 주의)을 추출하는 ReAct 시스템 프롬프트 초안 작성 (US-A1).
  * **Member B (Vision AI)**:
    - 현장 위험물(높은 턱, 야외 계단, 공사 자재 등) 및 공원 안내판 벤치마킹 이미지 20장 수집 및 Ground Truth 라벨링.
    - Gemini 1.5 Flash API 연동 및 Few-shot 위험 분류 프롬프트 벤치마킹 착수 (US-D1).
  * **Member C (Backend/GIS)**:
    - FastAPI 프로젝트 보일러플레이트 구성, Pydantic V2 기본 스키마 작성.
    - OpenRouteService / OSRM 라우팅 API 연동 Adapter 구현 (출발지 기준 순환 Waypoint 샘플링 기반 기본 루프 생성) (US-B4).
  * **Member D (Frontend)**:
    - Next.js (App Router) + TypeScript + Tailwind CSS PWA 프로젝트 초기화.
    - MapLibre GL JS / Leaflet 기반 지도 뷰어 컴포넌트 마운트 및 현재 위치 마커 렌더링.
  * **Member E (Infra/QA)**:
    - GitHub Repository 세팅, Git-flow 전략 확립, Supabase 프로젝트 생성.
    - `users`, `dogs`, `walk_history`, `walk_feedback` DDL 배포 및 Auth 연동 (US-A2).

---

### Week 2: 도메인 데이터 분석, 안전 제약 & 후보 경로 평가
* **주간 목표**: OSM Steps 데이터 필터링, DEM 경사도 연산 모듈 완성, Candidate Route Scorer 검증.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - Pydantic V2 Strict Schema 기반 도구 호출 바인딩 (`get_dog_context`, `search_routes`, `evaluate_candidates`).
    - 조건 누락 시 확인 질문(Clarification) 대화 분기 처리 로직 구현 (US-A1, US-A3).
  * **Member B (Vision AI)**:
    - `VisionHazardInspector` 1차 모듈 구현: 턱 높이 추정, 계단 식별, 구조화 JSON(`HazardReport`) 출력 규격화 (US-D1).
  * **Member C (Backend/GIS)**:
    - OSM 보행망 데이터에서 `highway=steps` 속성 파싱 및 배제(Hard Constraint) 처리 모듈 구현 (US-B1).
    - DEM 고도 데이터 연계 구간별 `max_slope_percent` 및 급경사 비율 산출 로직 개발 (US-B2).
    - 수집된 2~3개 후보 경로에 대한 Candidate Route Scorer 채점 모듈 구현 (US-B4).
  * **Member D (Frontend)**:
    - 산책 조건 입력 폼 컴포넌트 개발 (시간 칩/슬라이더, 계단 회피 토글, 경사도 선택 칩).
    - 반려견 프로필 등록 및 온보딩 뷰 완성 (US-A2).
  * **Member E (Infra/QA)**:
    - Dog Profile CRUD API 구현 및 에이전트 연동 테스트.
    - Week 2 중간 데모 및 라우팅 알고리즘 산출 경로 품질 1차 점검.

---

### Week 3: 환경 연산, 비전 위험 분석 & 프론트엔드 통합
* **주간 목표**: SunCalc 건물 그림자 연산, 비전 위험 분석 결합, 위험 우회 재탐색, Next.js PWA 통합.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - Vision 위험 분석 결과(`route_action: avoid_recommended`) 수신 시 우회 경로 재탐색 에이전트 워크플로우 연결 (US-D2).
    - 최종 산책 경로에 대한 에이전트 추천 코멘트 생성 프롬프트 고도화.
  * **Member B (Vision AI)**:
    - 저조도, 모션 블러, 각도 왜곡 등 예외 사진 입력 시 신뢰도 부족 경고 및 가이드 로직 추가 (US-D1).
    - 현장 사진 판독 지연시간 2.5초 이내 최적화.
  * **Member C (Backend/GIS)**:
    - `SunCalc` 태양각 계산 및 건물 2.5D 외곽선 기반 예상 그늘 비율(`shade_ratio`) 연산 모듈 개발 (Level 1~2) (US-B3).
    - 위험 구간 링크 임시 차단 및 동적 우회 재탐색 API(`POST /api/v1/walk/reroute`) 구현 (US-D2).
  * **Member D (Frontend)**:
    - 지도 위 추천 경로 Polyline 색상 분기 렌더링 (그늘/완만: 초록, 일반: 파랑, 급경사 주의: 주황) (US-C1).
    - 외부 지도 앱(네이버/카카오 지도) 도보 길찾기 딥링크 버튼 연동 (US-C2).
    - 현장 위험 사진 촬영 모달 및 업로드 컴포넌트 연동.
  * **Member E (Infra/QA)**:
    - Supabase Storage 버킷 구성 (현장 위험 사진 업로드용) 및 RLS 정책 적용.
    - 백엔드 스테이징 클라우드 배포(Render/Cloud Run) 및 CORS 연동.

---

### Week 4: GPS 산책 기록, 열 위험 안내, 부가 편의 & 실사용 테스트
* **주간 목표**: Foreground GPS 보행 추적, 기상청 열 위험 알림, 공영주차장 연동, 최소 5인 실사용자 필드 테스트 착수.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - 이전 산책 피드백(경사 불만족 등)을 다음 세션 프롬프트 및 라우팅 인자에 주입하는 Context Memory 피드포워드 파이프라인 완성 (US-E3).
  * **Member B (Vision AI)**:
    - 실사용자 필드 업로드 사진 실시간 모니터링 및 판독 정확도 검증 (US-D1).
  * **Member C (Backend/GIS)**:
    - 전국 공영주차장 API 연동 모듈 개발 (출발 거점 연계 P&R 코스 도출) (US-G1).
    - 기상청 단기예보 기반 시간대별 열 위험 지수 산출 모듈 개발 (US-F1).
  * **Member D (Frontend)**:
    - HTML5 Geolocation 기반 Foreground 실시간 위치 트래커 및 보행 궤적 표시 모듈 완성 (US-E1).
    - 산책 완료 요약 인포그래픽 카드 및 보행 만족도 피드백 모달 구현 (US-E2).
    - 나만의 코스(즐겨찾기) 저장 및 보관함 뷰 개발 (US-G2).
  * **Member E (Infra/QA) [실사용 테스트 리드]**:
    - **최소 5인 실사용자(견주) 필드 테스트 운영 (US-H1)**:
      - 소형견 2, 노령견 1, 대형견 2 견주 대상 PWA 배포 및 현장 테스트 가이드 전달.
      - 실제 도심 보행로 산책 수행 후 계단 회피, 경사도 만족도, 그늘 적중률 설문 수집.

---

### Week 5: 안정화, 피드백 반영, 보안/성능 최적화 & 최종 출시
* **주간 목표**: 필드 테스트 피드백 반영 튜닝, API 키 보안 검증, 성능 최적화, 배포 및 운영 문서 완성.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - 실사용자 발화 로그 분석을 통한 프롬프트 보정 및 비정상 입력 방어 가드레일 강화.
  * **Member B (Vision AI)**:
    - 판독 임계치 최종 캘리브레이션 및 Vision 장애 시 안내 가이드 검증.
  * **Member C (Backend/GIS)**:
    - 라우팅 및 그늘 연산 캐싱 적용으로 복합 경로 생성 평균 응답 지연 3초 이내 달성.
    - 데이터 출처(`source`) 및 신뢰도(`confidence`) 메타데이터 정합성 최종 점검.
  * **Member D (Frontend)**:
    - 모바일 브라우저 크로스 디바이스(iOS Safari, Android Chrome) 뷰포트 반응형 최적화.
    - 위치 권한 거부, 오프라인 등 네트워크 단절 시 사용자 친화적 에러 토스트 제공.
  * **Member E (Infra/QA)**:
    - 프로덕션 프로덕트 배포, API 키 은닉 및 환경변수 보안 감사.
    - 5인 실사용자 테스트 최종 평가 보고서 및 운영 가이드 문서 정리 (US-H1).
