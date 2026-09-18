# [상세 구현 계획서] PawTrail 단계별 구현 로드맵 및 5인 협업 실행 계획

## 1. 프로젝트 개요 및 팀 구성 (5인 애자일 스크럼 체계)

* **프로젝트명**: PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 에이전트 및 기록·공유 플랫폼)
* **목표**: 5주간 스크럼 기반 2개 스프린트 및 Hardening 기간을 통해 기획, 노면 가중치 순환 라우팅, 비전 멀티모달 위험 판독, 산책 기록/커뮤니티, n8n 자동화 파이프라인 구축 및 퍼블릭 클라우드 배포와 최소 5인 실사용자 CBT 완수.
* **팀원별 역할 분담 (R&R)**:
  * **Member A (팀장 / AI Agent & Workflow Lead)**:
    - LangGraph 기반 Walk Planning Agent 상태 머신 설계 및 ReAct 프롬프트 엔지니어링 (US-01, US-02)
    - Pydantic V2 Strict Tool-calling 규격 수립, Long-term Memory 맥락 주입 및 전체 PM 총괄
  * **Member B (AI / Vision & Multimodal Lead)**:
    - Gemini 1.5 Flash 기반 노면 재질/위험물 진단 파이프라인(`SurfaceSafetyInspector`) 개발 (US-04)
    - Structured JSON 출력 스키마 고정, 노면 위험도 점수 연산 및 재탐색 피드백 핸들러 구현 (US-05)
  * **Member C (Backend & Spatial Routing Lead)**:
    - FastAPI 백엔드 구축 및 REST API 엔드포인트 구현 (SSE는 제외하고 예측 가능한 REST 구조 우선)
    - OSM 노면 결측치 Fallback 추정 및 Routing API Provider 연동 기반 순환형(Loop) 라우터 도구 개발 (US-02, US-03, US-13)
  * **Member D (Frontend & UI/UX Lead)**:
    - Next.js / Tailwind CSS 기반 반응형 모바일 웹 인터페이스 구축 (US-07)
    - Mapbox GL JS 기반 노면별 색상 구분 Polyline 렌더링, 주머니 보관 연속 GPS 추적(Wake Lock/포켓 모드) 및 외부 지도 딥링크 UI 구현 (US-07, US-08, US-09)
  * **Member E (Infra, Automation & QA Lead)**:
    - Supabase(PostgreSQL) 구조화 데이터 기반 Long-term Memory DB 및 Vercel/Render CI/CD 배포 자동화 (US-06, US-10)
    - n8n 기상청 지면열 연동 일일 산책 골든타임 알림 워크플로우 구축 (US-12)
    - **최소 5인 실사용자 CBT 운영, 피드백 수집 및 분석 리포트 총괄 (US-11)**

---

## 2. 스프린트 일정 개요 (5주 로드맵)

```
[Sprint 1 (Week 1~2)] 코어 AI 파이프라인 & 라우팅 엔진 구축 (26 pt)
       │
[Sprint 2 (Week 3~4)] 서비스 통합, 기록/커뮤니티, 배포 및 5인 CBT (24 pt)
       │
[Hardening & Launch (Week 5)] 피드백 반영 고도화, 문서화 및 최종 데모 (5 pt)
```

---

## 3. 주차별 세부 구현 작업 (Step-by-Step)

### Week 1 (Sprint 1 시작): 도메인 데이터 인프라 및 AI 코어 셋업
* **주간 목표**: 개발 환경 통일, OSM 노면 데이터 파이프라인 검증, Agent 상태 머신 정의, Git 협업 룰 확립.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - LangGraph State 정의 (`messages`, `dog_profile`, `preferred_surfaces`, `route_result`).
    - 자연어 입력에서 견종, 산책 시간, 선호 노면을 추출하는 ReAct 시스템 프롬프트 초안 작성 및 테스트 (US-01).
  * **Member B (Vision AI)**:
    - 노면 테스트 이미지 30장(흙, 잔디, 아스팔트, 파쇄석, 보도블록, 공사 잔해 등) 데이터셋 구축.
    - Gemini 1.5 Flash API 연동 및 Structured Output 프롬프트 벤치마킹 (US-04).
  * **Member C (Backend/GIS)**:
    - 테스트베드 구역 OSM 보행 네트워크 데이터(.osm.pbf) 파싱 및 NetworkX 그래프 생성.
    - OSM `surface` 결측치 자동 보정(Fallback) 룰 모듈 구현 (US-03).
  * **Member D (Frontend)**:
    - Next.js 14 + Tailwind CSS 보일러플레이트 구성 및 모바일 반응형 뷰포트 설정.
    - Mapbox GL JS 맵 캔버스 초기화 및 기본 마커/컨트롤 UI 구성.
  * **Member E (Infra/QA)**:
    - GitHub Organization 세팅, Git-flow 브랜치 전략(`main`, `develop`, `feature/*`), PR 템플릿 확립.
    - Supabase 인스턴스 생성 및 스키마(`users`, `dogs`, `walk_history`, `feedback`) DDL 배포 (US-06).

### Week 2 (Sprint 1 종료): 개별 AI 모듈 독립 구현 & 노면 가중치 라우팅
* **주간 목표**: 사용자 선호 노면 순환 라우팅 완료, 비전 판독 및 메모리 모듈 단위 테스트 100% 통과.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - Pydantic V2 Strict Schema 기반 자율 호출 도구 3종 바인딩 (`get_dog_context`, `generate_loop_route`, `analyze_surface_image`).
    - 선호 노면 파라미터가 누락되었을 때의 사용자 명확화 질문(Clarification) 대화 루프 구현.
  * **Member B (Vision AI)**:
    - `SurfaceSafetyInspector` 모듈 완성: `safety_score`(0~100), 노면 재질, 위험요소 파싱 (US-04).
    - 예외 처리: 저조도/흐린 사진 입력 시 신뢰도 부족 경고 및 재촬영 요청 로직 추가.
  * **Member C (Backend/GIS)**:
    - 사용자 선호 노면 할인 계수($W_{\text{pref}} = 0.4 \sim 0.5$) 및 페널티 계수 비용 함수 모듈 개발 (US-02).
    - 출발점 기준 다각형 경유지(Waypoint) 샘플링 및 Routing API(ORS/OSRM) 연동 순환 루프 코스 생성 모듈 구현 (US-03).
  * **Member D (Frontend)**:
    - 선호 노면 선택 칩 UI(흙길, 잔디길, 탄성포장, 보도블록) 및 에이전트 채팅 버블 컴포넌트 개발.
    - 카메라 촬영/이미지 업로드 컴포넌트 구현.
  * **Member E (Infra/QA)**:
    - Supabase 기반 Long-term Memory CRUD API 구현 및 에이전트 연동 테스트 (US-06).
    - Sprint 1 리뷰 및 데모 진행 (중간 산출물 점검).

### Week 3 (Sprint 2 시작): 서비스 통합, 산책 기록 & n8n 자동화
* **주간 목표**: Frontend-Backend-AI E2E 통합, GPS 실시간 트래킹 및 커뮤니티 피드 개발, n8n 알림 구축.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - Long-term Memory 맥락 주입 파이프라인 결합 (과거 산책 피로도 및 질환 이력 반영).
    - 비전 분석 결과와 라우팅 엔진 간의 위험 노면 우회 재탐색(Rerouting) 이벤트 체인 완성 (US-05).
  * **Member B (Vision AI)**:
    - 실시간 산책 중 제보된 노면 사진의 위험도를 지도 메타데이터로 브로드캐스팅하는 핸들러 구현.
  * **Member C (Backend/GIS)**:
    - 전국공영주차장 표준 API 연동 모듈 개발 (출발지 인근 P&R 코스 도출) (US-13).
    - 추천 경로 GeoJSON 및 구간별 노면 속성 반환 REST API 최적화 (응답 지연 1.5초 이내 달성).
  * **Member D (Frontend)**:
    - 추천 경로 Polyline 노면별 색상 분기 렌더링 (잔디: 초록, 흙: 갈색, 탄성포장: 주황, 아스팔트: 회색) (US-07).
    - Screen Wake Lock & 포켓 모드 기반 주머니 보관 중 GPS 연속 추적, 절전 복귀 시 스냅 보정 및 '선호 노면 달성률(%)' 카드 렌더링 (US-08).
    - 외부 네이버지도/카카오맵 도보 길찾기 바로가기 연동 버튼 추가 (US-07).
  * **Member E (Infra/QA)**:
    - n8n 워크플로우 구현: 기상청 단기예보 조회 → 지면열 회귀 연산 → 35℃ 이하 골든타임 웹훅 알림 발송 (US-12).
    - 커뮤니티 피드 테이블 구축 및 산책 완주 기록 저장 연동 (US-09).

### Week 4 (Sprint 2 종료): 외부 클라우드 배포 & 실사용자 5인 CBT
* **주간 목표**: 외부 접근 가능한 퍼블릭 배포 완료, 실사용자 5인 이상 섭외 및 필드 테스트 수행, 1차 피드백 수집.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - 실사용자 대화 로그 모니터링, 프롬프트 인젝션 방어 가드레일 및 AI 시뮬레이션 고지 UI 검증 (US-10).
  * **Member B (Vision AI)**:
    - 실사용자가 필드에서 업로드한 현장 노면 사진 판독 결과 실시간 모니터링 및 임계값 캘리브레이션.
  * **Member C (Backend/GIS)**:
    - Render / Cloud Run 프로덕션 환경 배포, 도메인 연결, CORS 설정 및 부하 테스트.
  * **Member D (Frontend)**:
    - Vercel 프로덕션 배포 완료 (모바일 PWA 메타태그 적용).
    - 인앱 사용자 만족도 평가 및 피드백 입력 모달 배포 (US-09, US-11).
  * **Member E (Infra/QA) [핵심 총괄]**:
    - **실사용자 CBT 운영 (US-11)**:
      - 반려견 견주 5명(소형견 2, 중/대형견 2, 노령/관절질환견 1) 섭외 및 서비스 URL 전달.
      - 5개 검증 시나리오에 따라 실제 필드 산책 1회 이상 수행 및 설문 수집.
    - 테스터 피드백 취합 대시보드 작성 및 긴급 버그 핫픽스 관리.

### Week 5 (Hardening & Launch): 피드백 반영 기능 고도화 & 최종 데모
* **주간 목표**: 수집된 사용자 피드백을 기반으로 가중치/프롬프트 개선 배포, GitHub 문서화 및 발표 완비.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - 피드백 반영: "선호 노면 비중이 부족함" 의견 수용 → $W_{\text{pref}}$ 계수 0.5에서 0.35로 강화하여 재배포.
    - AI Agent 설계 근거 및 기술적 의사결정 보고서 정리.
  * **Member B (Vision AI)**:
    - 피드백 반영: 그늘진 아스팔트의 노면 오분류 케이스 프롬프트 보정.
  * **Member C (Backend/GIS)**:
    - 피드백 반영: 순환 코스 오차 허용범위 축소 (목표 거리 대비 $\pm 10\%$ 이내 튜닝).
  * **Member D (Frontend)**:
    - 모바일 주행 가독성 개선 (하단 플로팅 컨트롤 바 최적화) 및 시연 데모 비디오 녹화.
  * **Member E (Infra/QA)**:
    - GitHub `README.md` 최종 정비 (아키텍처, 5인 R&R, 기술 스택, 실행 방법, CBT 피드백 반영 내역).
    - 최종 프로젝트 결과 발표 슬라이드(PDF) 제작 및 미션 체크리스트 전수 검증.

---

## 4. 실사용자(5인) CBT 운영 및 검증 계획 (US-11)

| 테스터 ID | 대상 반려견 프로필 | 테스트 시나리오 | 검증 지표 | Week 5 피드백 반영 계획 |
|:---:|---|---|---|---|
| **Tester 1** | 말티즈 (4세, 슬개골 탈구 2기) | "흙길+잔디길" 선택 후 15분 코스 생성 및 산책 | 흙/잔디길 달성률, 관절 부담도 | 아스팔트 회피 페널티 3.0으로 상향 |
| **Tester 2** | 골든 리트리버 (3세, 대형견) | "주차장 출발" 40분 원정 산책 코스 생성 및 산책 | 주차장 도보 접근성, 코스 만족도 | 공영주차장 연계 반경 1.5km로 확장 |
| **Tester 3** | 푸들 (11세, 노령견) | 한낮 폭염 시 "탄성포장/흙길" 20분 코스 생성 | 지면열 체감, 보행 편의성 | 평지 우선 경사도 회피 가중치 보정 |
| **Tester 4** | 웰시코기 (5세, 일반 보행) | 산책 중 노면 사진 촬영 제보 및 대체 경로 이동 | 비전 판독 속도, 리라우팅 적절성 | 비전 Structured Output 응답 시간 튜닝 |
| **Tester 5** | 비숑 프리제 (2세, 활동견) | n8n 골든타임 알림 수신 후 즉시 산책 완주 | 알림 적시성, 커뮤니티 공유 기능 | 알림 발송 시각을 골든타임 45분 전으로 조정 |

---

## 5. 최종 산출물 및 미션 체크리스트

* [x] **기획서 및 애자일 요구사항 명세서 완비**: MoSCoW, DoD, 스토리 포인트 명시
* [x] **필수 AI 기술 4종 적용**: AI Agent, Vision 멀티모달, Long-term Memory, n8n 워크플로우
* [x] **외부 퍼블릭 배포**: Vercel(Front) + Render(Back) 상시 접속 URL 확보
* [x] **실사용자 5인 이상 CBT 완수**: 5개 페르소나별 필드 산책 수행 및 설문 결과 확보
* [x] **사용자 피드백 기반 서비스 개선**: Week 5 프롬프트 및 라우팅 가중치 튜닝 재배포
* [x] **GitHub 버전 관리 및 문서화**: 5인 R&R, 아키텍처 다이어그램, 실행 가이드 완비
* [x] **발표 자료 준비**: 최종 결과 발표 슬라이드 및 서비스 시연 영상 준비
