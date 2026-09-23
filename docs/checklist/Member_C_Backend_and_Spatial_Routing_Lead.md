# 📋 [Member C] Backend & Spatial Routing Lead — AI Pair Programming 체크리스트

## 1. 역할 개요 및 미션
- **역할 (Role)**: Backend & Spatial Routing Lead
- **핵심 목표**: FastAPI 기반 무상태(Stateless) 고성능 백엔드 코어 구축, 전문 Routing API Adapter(ORS/OSRM) 연동 및 순환 루프 생성, OSM 계단 배제(`highway=steps`) 하드 제약 라우팅, DEM 경사도 및 그늘 가중치 연계, 3초 이내 현장 위험 우회 동적 재탐색 API, Supabase Cloud 이메일 Auth 및 마스킹 코스 CRUD를 총괄한다.
- **배정 공수 및 스토리**: 총 **91 Hours (14개 Task)** | **US-B1, US-B2, US-B3, US-B4, US-D2, US-F1, US-G1, US-G2**

---

## 2. AI Pair Programming 기본 원칙 & 프롬프팅 가이드

### 2.1 백엔드 아키텍처 및 클린코드 가이드라인
- **Stateless REST API 설계**: 서버 세션이나 쿠키에 의존하지 않고, 모든 요청/응답은 Pydantic V2 Strict Schema를 통해 완전 무상태로 처리되도록 AI 코드를 생성한다.
- **클린코드 엄격 제한 준수**:
  - 단일 모듈/파일 최대 250줄 이하 (초과 시 서비스/유틸 분리).
  - 단일 함수 최대 40줄 이하, 인지 복잡도(Cognitive Complexity) 10 이하.
- **다단계 Fallback 라우팅 보장**: OSM Steps 회피 시 고립 지형(Dead-end)이 발생할 경우, 연결 불가 에러 대신 최소 계단 경유 대안로 및 경고 메타데이터(`has_stairs: true`, 계단 단수)를 반환하도록 설계한다.

---

## 3. 단계별 AI Pair Programming 체크리스트

### 1단계: 작업 착수 전 준비 (Pre-Coding)
- [ ] **스토리 및 인수 조건(AC) 재확인**: `docs/03_PawTrail_Agile_User_Stories.md`의 Epic B(US-B1~B4), US-D2, US-F1, US-G1~G2 확인.
- [ ] **API 규격서 및 계약 DTO 점검**: `test_case/test_api_contracts.py`, `docs/04_PawTrail_Architecture_Design.md`의 엔드포인트 명세 확인 (`POST /api/walks/plan`, `POST /api/routes/reroute` 등).
- [ ] **외부 라우팅 엔진 규격 확인**: ORS (OpenRouteService) 및 OSRM 순환 루프 생성 파라미터 구조 파악.

### 2단계: AI 코드 생성 및 페어링 (During Coding)
- [ ] **OSM 계단 회피 하드 제약 라우터 (TASK-B1-1~3)**:
  - [ ] OSM 보행로 네트워크 그래프에서 `highway=steps` 링크를 하드 제약으로 제외하고 경로를 탐색하는가?
  - [ ] 계단을 완전 회피한 경로가 도출되었을 때 `has_stairs: false` 및 신뢰도 지표를 메타데이터로 정확히 반환하는가?
  - [ ] 섬/육교 등 계단 외 통행로가 전무한 고립 지형 발생 시, 안전 Fallback 및 우회 안내 경고를 반환하는가?
- [ ] **DEM 경사도 및 그늘 가중치 라우팅 연계 (TASK-B2-2, B2-3, B3-2, B3-3)**:
  - [ ] Member B의 DEM 고도 데이터 및 SunCalc 그늘 비율을 NetworkX 가중치 비용 함수($\text{Cost} = \text{Length} \times F_{\text{steps}} \times F_{\text{slope}} \times F_{\text{shade}}$)에 정확히 반영하는가?
  - [ ] 급경사(>8%) 링크를 피하고 완만 경사로 우선 선택 알고리즘이 정상 작동하는가?
- [ ] **Routing API Adapter 및 순환 루프 생성 (TASK-B4-1, B4-2)**:
  - [ ] 시작 좌표를 중심으로 120° 간격의 다중 경유지(Waypoint)를 자동 생성하여 자연스러운 원점 복귀 순환 루프를 도출하는가?
  - [ ] OSRM/ORS 서버 다운 시 내부 간이 다익스트라(Dijkstra) 라우터로 무중단 전환되는가?
- [ ] **위험 구간 동적 우회 실시간 재탐색 (TASK-D2-2)**:
  - [ ] Vision 감지 위험 좌표(링크)에 10배 비용 페널티 또는 통행 금지(`blocked_link`)를 적용하고 **3초 이내**에 대안 경로를 반환하는가?
- [ ] **Supabase Auth 및 커뮤니티 REST API (TASK-G2-1, G2-3, G2-4)**:
  - [ ] 소셜 로그인 의존 없이 `Supabase Auth` 이메일/비밀번호 간편 가입/로그인(Auto-confirm) 엔드포인트가 완성되었는가?
  - [ ] 코스 등록/조회 시 Row Level Security(RLS) 및 출발지 200m 마스킹 데이터만 저장/반환되는가?
- [ ] **클린코드 가드레일 준수**:
  - [ ] 파일당 250줄 초과 방지를 위해 라우터, 서비스, 모델 계층이 명확히 분리되었는가?
  - [ ] 비동기 I/O (`async def`) 및 연결 풀(Connection Pool) 관리가 최적화되었는가?

### 3단계: 단위 테스트 및 검증 (Testing & Verification)
- [ ] **TDD 테스트 스위트 실행**:
  ```bash
  python -m pytest test_case/test_surface_cost_model.py -v
  python -m pytest test_case/test_api_contracts.py -v
  ```
- [ ] **응답 지연시간(Latency) 검증**:
  - [ ] 일반 루프 경로 생성 API 지연시간 2.5초 이내 달성 확인.
  - [ ] 위험 우회 동적 재탐색 API 지연시간 3.0초 이내 달성 확인.
- [ ] **API 계약 무결성 검증**: 요청/응답 Pydantic V2 DTO 스키마 유효성 100% 통과.

### 4단계: 산출물 동기화 및 형상 관리 (Post-Coding & Review)
- [ ] **문서 정합성 확인**: API 엔드포인트 또는 에러 코드 변경 시 `docs/04_PawTrail_Architecture_Design.md` 및 `docs/07_PawTrail_Traceability_Matrix.md` 즉시 갱신.
- [ ] **프론트엔드 연동 지원**: Member D(모바일 앱)와 REST API 계약 일치 여부 크로스 체크.

---

## 4. 핵심 안티패턴 (주의해야 할 금기사항)
1. ❌ **하드코딩된 API Key 및 자격증명 방치 금지**: Supabase 키, ORS 토큰 등은 반드시 `.env` 환경변수로 관리할 것.
2. ❌ **블로킹(Blocking) I/O 동기 호출 금지**: 외부 API 호출 시 `httpx.AsyncClient`를 사용하여 이벤트 루프 블로킹을 방지할 것.
3. ❌ **마스킹 없는 원본 좌표 공개 금지**: 커뮤니티 코스 저장 시 클라이언트에서 마스킹 처리가 누락되었더라도 백엔드에서 2차 강제 지터링 검증을 수행할 것.
