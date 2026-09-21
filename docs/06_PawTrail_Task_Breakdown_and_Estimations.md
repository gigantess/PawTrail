# [작업 분할 명세서] PawTrail 사용자 스토리별 상세 구현 Task 및 작업량 추정

## 1. 개요 및 추정 기준

* **프로젝트명**: PawTrail (AI Native 반려견 안심 산책 에이전트 및 기록 플랫폼)
* **목적**: 18개 사용자 스토리(US-A1 ~ US-H1)를 실제 개발 가능한 세부 Task로 분할하고, 애자일 추정치(Story Points, 공수 Hours) 및 담당자를 지정하여 5주간의 명확한 실행 계획을 제공.
* **작업량 산정 원칙 (지침 10.6 반영)**:
  - 이전의 292h 맞추기식 공수 축소를 전면 배제하고, 외부 API 연동, 데이터 신뢰도 검증, 예외/오류 처리, 테스트 및 배포를 포함한 **실제 사용 가능한 서비스 기준의 현실적 공수**로 재추정.
  - **13대 핵심 재추정 작업**:
    1. Routing API Adapter 연동
    2. OSM Steps 데이터 추출 및 계단 회피
    3. DEM Elevation / Slope 분석
    4. Solar & Building Shade Estimation
    5. Candidate Route Scoring 랭킹 알고리즘
    6. Vision Hazard Detection (높은 턱, 계단, 공사구간)
    7. Rerouting (동적 우회 재탐색)
    8. Foreground GPS 위치 추적 및 기록
    9. Supabase Context Memory & 피드백 반영
    10. Weather / Heat Risk 연산
    11. Mobile UX (Next.js PWA & 지도 렌더링)
    12. E2E 통합 테스트
    13. 클라우드 배포 및 운영 보안
* **팀 구성 (5인)**:
  - Member A: AI Agent / Product Logic Lead
  - Member B: Vision / Multimodal AI Lead
  - Member C: Backend / Routing / GIS Data Lead
  - Member D: Frontend / Mobile UX Lead
  - Member E: Infra / Data / QA Lead

---

## 2. 사용자 스토리별 세부 구현 Task 명세

### [Epic A] 산책 조건 입력 및 개인화

#### US-A1: 대화형 자연어 산책 요청 및 조건 구조화 (5 pt / 총 24h)
* **담당**: Member A (Sub: Member D) | **스프린트**: Sprint 1 (Week 1)
* **세부 Task**:
  * **TASK-A1-1**: LangGraph Agent 상태 그래프 스키마(`AgentState`) 설계 (4h / Member A)
  * **TASK-A1-2**: 자연어 발화에서 시간, 계단/경사/그늘 선호 엔티티를 추출하는 ReAct 프롬프트 작성 (6h / Member A)
  * **TASK-A1-3**: Pydantic V2 Strict Input Schema 및 누락 정보 질의(Clarification) 대화 분기 구현 (6h / Member A)
  * **TASK-A1-4**: FastAPI REST API 연동 및 모의 발화 10종 파싱 테스트 (8h / Member A)

#### US-A2: 반려견 프로필 등록 및 관리 (3 pt / 총 14h)
* **담당**: Member E (Sub: Member A) | **스프린트**: Sprint 1 (Week 1~2)
* **세부 Task**:
  * **TASK-A2-1**: Supabase `dogs` 테이블 DDL 설계 및 체급별 기본 보행속도 매핑 (4h / Member E)
  * **TASK-A2-2**: 반려견 프로필 CRUD API 구현 및 RLS 보안 정책 적용 (4h / Member E)
  * **TASK-A2-3**: 프로필 등록 온보딩 폼 UI 컴포넌트 개발 (6h / Member D)

#### US-A3: 목표 산책 시간/거리 기반 환산 (3 pt / 총 16h)
* **담당**: Member A, C (Sub: Member D) | **스프린트**: Sprint 1 (Week 1~2)
* **세부 Task**:
  * **TASK-A3-1**: 플래너 UI 산책 시간 원터치 칩(15/30/45/60분) 및 슬라이더 바인딩 (4h / Member D)
  * **TASK-A3-2**: 체급 및 관절 상태별 보행 속도 기반 목표 거리 환산 모듈 구현 (6h / Member C)
  * **TASK-A3-3**: 목표 시간 대비 경로 소요 시간 수렴도($\pm 15\%$) 검증 테스트 (6h / Member C)

---

### [Epic B] 무계단·완만한 경사·그늘 우선 경로 생성

#### US-B1: 지도 데이터 기반 확인된 계단 구간 우선 회피 (8 pt / 총 34h)
* **담당**: Member C | **스프린트**: Sprint 1 (Week 2)
* **세부 Task**:
  * **TASK-B1-1**: OSM 보행 도로망 데이터 파싱 및 `highway=steps` 링크 추출 인덱서 구축 (8h / Member C)
  * **TASK-B1-2**: 계단 링크 탐색 배제(Hard Constraint) 및 결측치 대응 신뢰도 메타데이터 부여 모듈 구현 (10h / Member C)
  * **TASK-B1-3**: 모든 경로가 계단을 포함할 때 최소 계단 대체 경로 산출 및 안내 Fallback 로직 개발 (8h / Member C)
  * **TASK-B1-4**: 계단 밀집 구역 테스트베드 대상 회피 라우팅 단위/통합 테스트 (8h / Member C)

#### US-B2: DEM 기반 최대 경사도 제어 및 완만 경사 우선 경로 도출 (5 pt / 총 26h)
* **담당**: Member C | **스프린트**: Sprint 1 (Week 2)
* **세부 Task**:
  * **TASK-B2-1**: 수치표고모델(DEM) 래스터 데이터 적재 및 경로 세그먼트 고도 샘플링 파이프라인 (8h / Member C)
  * **TASK-B2-2**: 세그먼트별 `max_slope_percent` 및 급경사 비율 연산 모듈 개발 (8h / Member C)
  * **TASK-B2-3**: 사용자 경사 선호도(매우 완만/완만/제한 없음)에 따른 페널티 비용 함수 구현 (6h / Member C)
  * **TASK-B2-4**: 구릉지 지형 테스트 샘플 대상 완만 경로 선별 알고리즘 검증 (4h / Member C)

#### US-B3: 태양 위치 및 건물 형상 기반 시간대별 그늘 우선 평가 (5 pt / 총 28h)
* **담당**: Member C | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-B3-1**: `SunCalc` 연동 산책 일시/위치 기준 태양 고도각 및 방위각 계산 모듈 (6h / Member C)
  * **TASK-B3-2**: 가용 건물 2.5D/3D 외곽선 및 높이 데이터 기반 그림자 투영 다각형 연산 (10h / Member C)
  * **TASK-B3-3**: 보행 링크와 그림자 다각형 교차 연산을 통한 예상 그늘 비율(`shade_ratio`) 산출 (6h / Member C)
  * **TASK-B3-4**: 정오 vs 늦은 오후 시간대별 그늘 평가 대조 테스트 및 신뢰도 태깅 (6h / Member C)

#### US-B4: Routing API Adapter 연동 및 후보 경로 다요소 스코어링 (8 pt / 총 36h)
* **담당**: Member C, A | **스프린트**: Sprint 1 (Week 1~2)
* **세부 Task**:
  * **TASK-B4-1**: OpenRouteService / OSRM REST API 연동 독립 Adapter 레이어 구현 (10h / Member C)
  * **TASK-B4-2**: 출발지 중심 다각형 Waypoint 샘플링 기반 순환 루프 후보(2~3개) 생성 모듈 (8h / Member C)
  * **TASK-B4-3**: 계단, 경사, 그늘, 시간 오차를 종합 평가하는 Candidate Route Scorer 랭킹 알고리즘 개발 (10h / Member C, A)
  * **TASK-B4-4**: Routing API 실패/장애 시 대체 템플릿 Fallback 및 지연시간 최적화 (8h / Member C)

---

### [Epic C] 지도 표시 및 외부 내비게이션

#### US-C1: 구간별 안전/고도/그늘 속성 시각화 및 경로 프리뷰 (5 pt / 총 24h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-C1-1**: Next.js PWA 반응형 지도(MapLibre/Leaflet) 캔버스 마운트 (6h / Member D)
  * **TASK-C1-2**: 경로 속성(그늘/완만: 초록, 일반: 파랑, 주의: 주황) 분기 Polyline 렌더링 (8h / Member D)
  * **TASK-C1-3**: 거리, 시간, 최대 경사, 그늘 비율, 계단 수 요약 카드 UI 구현 (6h / Member D)
  * **TASK-C1-4**: 모바일 브라우저 뷰포트 반응형 최적화 및 터치 제스처 검증 (4h / Member D)

#### US-C2: 외부 상용 지도(네이버/카카오 지도) 도보 길찾기 딥링크 연동 (2 pt / 총 10h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-C2-1**: 추천 경로 주요 Waypoint 좌표 기반 네이버 지도 길찾기 URL Scheme 생성 모듈 (4h / Member D)
  * **TASK-C2-2**: 카카오맵 도보 길찾기 URL Scheme 생성 및 원터치 호출 버튼 UI 연동 (4h / Member D)
  * **TASK-C2-3**: 미설치 기기 대응 웹 브라우저 Fallback URL 테스트 (2h / Member D)

---

### [Epic D] 현장 위험 분석 및 재탐색

#### US-D1: Vision AI 기반 현장 턱·계단·보행 장애물 시각 분석 (5 pt / 총 26h)
* **담당**: Member B | **스프린트**: Sprint 2 (Week 3)
* **세부 Task**:
  * **TASK-D1-1**: 현장 위험물(높은 턱, 계단, 공사 잔해) 벤치마킹 이미지셋 구축 및 라벨링 (6h / Member B)
  * **TASK-D1-2**: Gemini 1.5 Flash Vision 프롬프트 엔지니어링 및 Structured JSON 출력 스키마 고정 (8h / Member B)
  * **TASK-D1-3**: 모션 블러, 저조도 사진 입력 시 예외 처리 및 가이드 로직 구현 (6h / Member B)
  * **TASK-D1-4**: 이미지 업로드 REST API(`POST /api/v1/surface/inspect`) 연동 및 판독 지연 2.5초 이내 최적화 (6h / Member B)

#### US-D2: 현장 위험 구간 우회 및 동적 재탐색 (5 pt / 총 22h)
* **담당**: Member A, C | **스프린트**: Sprint 2 (Week 3~4)
* **세부 Task**:
  * **TASK-D2-1**: 위험 감지 좌표 기준 인접 링크 임시 차단(Block List) 핸들러 구현 (6h / Member C)
  * **TASK-D2-2**: 현재 위치에서 출발지 복귀 안전 우회 경로 재탐색 API(`POST /api/v1/walk/reroute`) 구현 (8h / Member C)
  * **TASK-D2-3**: 우회 사유 및 경로 변경 사항 에이전트 브리핑 메시지 생성 체인 연동 (4h / Member A)
  * **TASK-D2-4**: 모바일 UI 상 우회 경로 갱신 인터랙션 E2E 검증 (4h / Member D, A)

---

### [Epic E] 산책 기록 및 Memory

#### US-E1: Foreground 위치 추적 및 실산책 경로·시간 기록 (5 pt / 총 22h)
* **담당**: Member D, E | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-E1-1**: HTML5 Geolocation API 기반 Foreground 위치 주기적 수집 모듈 개발 (6h / Member D)
  * **TASK-E1-2**: 보행 시작, 일시 정지, 종료 제어 및 실시간 궤적 지도 마킹 (6h / Member D)
  * **TASK-E1-3**: 산책 완주 데이터(`actual_duration`, `distance`, `actual_path`) Supabase 적재 API 구현 (6h / Member E)
  * **TASK-E1-4**: GPS 튀김 현상 완화(Kalman 필터링 또는 단순 평활화) 적용 (4h / Member D)

#### US-E2: 산책 종료 후 보행 체감 피드백 수집 및 인포그래픽 (3 pt / 총 14h)
* **담당**: Member D, E | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-E2-1**: 완주 결과 요약 인포그래픽 모달 컴포넌트 개발 (4h / Member D)
  * **TASK-E2-2**: 보행 만족도 점수 및 태그(계단 없음, 경사 편함, 그늘 충분 등) 입력 UI (4h / Member D)
  * **TASK-E2-3**: `walk_feedback` 테이블 적재 API 및 통계 집계 쿼리 작성 (6h / Member E)

#### US-E3: Context Memory 축적 및 다음 산책 추천 자동 보정 (3 pt / 총 16h)
* **담당**: Member A, E | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-E3-1**: 최근 5회 산책 요약 및 피드백 텍스트를 추출하는 Memory 조회 모듈 (4h / Member E)
  * **TASK-E3-2**: 부정 평가(예: "경사 힘들었음") 누적 시 허용 경사도 기준 자동 하향 보정 로직 (6h / Member A)
  * **TASK-E3-3**: LangGraph Agent 시스템 프롬프트 맥락 주입 및 단위 검증 (6h / Member A)

---

### [Epic F] 기상/열 위험 정보

#### US-F1: 기상청 단기예보 연동 시간대별 열 위험 지수 안내 (3 pt / 총 14h)
* **담당**: Member E (Sub: Member C) | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-F1-1**: 기상청 단기예보 API 클라이언트 구현 및 시간대별 기온/운량 파싱 (6h / Member E)
  * **TASK-F1-2**: 일사량 및 열 위험 지수(안전/주의/위험) 산출 모듈 개발 (4h / Member E)
  * **TASK-F1-3**: 플래너 상단 산책 골든타임 알림 카드 UI 렌더링 (4h / Member D)

---

### [Epic G] 주차 및 부가 서비스

#### US-G1: 출발 거점 연계 공영주차장(P&R) 코스 탐색 (2 pt / 총 10h)
* **담당**: Member C | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-G1-1**: 전국 공영주차장 공공데이터 API 클라이언트 및 좌표 검색 모듈 구현 (5h / Member C)
  * **TASK-G1-2**: 주차장 출입구 좌표 연계 순환 산책 코스 생성 엔드포인트 연동 (5h / Member C)

#### US-G2: 마음에 드는 안심 산책로 '나만의 코스(즐겨찾기)' 보관 (2 pt / 총 10h)
* **담당**: Member D, E | **스프린트**: Sprint 2 (Week 4)
* **세부 Task**:
  * **TASK-G2-1**: 즐겨찾기 북마크 추가/삭제 REST API 및 Supabase 테이블 연동 (4h / Member E)
  * **TASK-G2-2**: 산책 상세 카드 북마크 토글 버튼 및 보관함 목록 뷰 개발 (6h / Member D)

---

### [Epic H] 실사용 검증 및 운영

#### US-H1: 최소 5인 이상 실사용자 필드 테스트 및 피드백 반영 (5 pt / 총 30h)
* **담당**: 전원 (Lead: Member E) | **스프린트**: Hardening (Week 4~5)
* **세부 Task**:
  * **TASK-H1-1**: 실사용자 5인(소형견 2, 노령견 1, 대형견 2) 섭외 및 필드 테스트 시나리오 가이드 배포 (6h / Member E)
  * **TASK-H1-2**: 현장 실산책 수행 및 데이터 수집 (계단 회피 적중률, 경사 만족도, 그늘 적중률) (10h / 전원)
  * **TASK-H1-3**: 수집된 설문 분석 및 라우팅 가중치/프롬프트 튜닝 (8h / Member A, C)
  * **TASK-H1-4**: 운영 보안(API 키 은닉) 점검 및 최종 E2E 테스트 보고서 작성 (6h / Member E)

---

## 3. 공수 집계 및 애자일 일정 매핑

### 3.1 에픽별 작업량 요약표

| 에픽 (Epic) | Story Points | 세부 Task 수 | 추정 공수 (Hours) | 비중 (%) |
|---|:---:|:---:|:---:|:---:|
| **Epic A. 산책 조건 입력 및 개인화** | 11 pt | 11개 | 54h | 14.7% |
| **Epic B. 무계단·완만 경사·그늘 우선 경로 생성** | 26 pt | 16개 | 124h | 33.7% |
| **Epic C. 지도 표시 및 외부 내비게이션** | 7 pt | 7개 | 34h | 9.2% |
| **Epic D. 현장 위험 분석 및 재탐색** | 10 pt | 8개 | 48h | 13.0% |
| **Epic E. 산책 기록 및 Memory** | 11 pt | 11개 | 52h | 14.1% |
| **Epic F. 기상/열 위험 정보** | 3 pt | 3개 | 14h | 3.8% |
| **Epic G. 주차 및 부가 서비스** | 4 pt | 4개 | 20h | 5.4% |
| **Epic H. 실사용 검증 및 운영** | 5 pt | 4개 | 30h | 8.2% |
| **합계** | **77 pt** | **64개 Task** | **376h** | **100.0%** |

### 3.2 팀원별 공수 배분 현황

| 담당자 | 주요 역할 | 담당 Task 공수 (Hours) | 주당 평균 공수 (5주 기준) |
|---|---|:---:|:---:|
| **Member A** | AI Agent / Product Logic Lead | 74h | 약 14.8h / 주 |
| **Member B** | Vision / Multimodal AI Lead | 52h | 약 10.4h / 주 |
| **Member C** | Backend / Routing / GIS Data Lead | 112h | 약 22.4h / 주 |
| **Member D** | Frontend / Mobile UX Lead | 82h | 약 16.4h / 주 |
| **Member E** | Infra / Data / QA Lead | 56h | 약 11.2h / 주 |
| **합계** | **5인 전원** | **376h** | **약 75.2h / 주 (팀 전체)** |

> [!NOTE]
> 5인 개발팀이 5주간 소화하기에 가장 적절하고 충실한 **총 376시간 (77 pt)** 규모로 재산정되었습니다. 직접 A* 엔진 개발이나 백그라운드 GPS의 불확실성을 배제하고, 실제 구동 가능한 외부 API 어댑터, Steps/Slope/Shade 분석, Foreground 기록, 5인 실사용자 필드 테스트에 자원을 집중합니다.
