# [상세 구현 계획서] PawTrail 단계별 구현 로드맵 및 5인 협업 실행 계획

## 1. 프로젝트 개요 및 팀 구성 (5인 애자일 체계)

* **프로젝트명**: PawTrail (반려견 맞춤형 안심 산책 에이전트 및 프라이버시 우선 플랫폼)
* **핵심 구현 원칙**:
  - **개인정보 로컬 보관 (Local-First)**: 자택 위치, 이동 궤적, 반려견 프로필을 폰(IndexedDB)에만 보관하고 서버는 무상태(Stateless)로 운영.
  - **간단한 이메일 회원가입**: 복잡한 소셜 OAuth 없이 Supabase Auth 이메일/비밀번호 가입(개발/CBT 중 Auto-confirm)으로 간소화.
  - **다요소 안심 라우팅**: Routing API Adapter + OSM Steps 회피 + DEM 완만 경사 + SunCalc 그늘 추정 + 현장 Vision 위험 분석.
* **팀원별 역할 분담 (R&R)**:
  * **Member A (AI Agent / Product Logic Lead)**:
    - LangGraph 기반 Walk Planning Agent 설계 및 무상태(Stateless) 프롬프트 오케스트레이션 (US-A1, US-A3, US-E3)
    - 클라이언트 로컬 프로필/피드백 페이로드 바인딩 및 후보 경로 평가/설명 총괄
  * **Member B (Vision / Multimodal AI Lead)**:
    - Gemini 1.5 Flash 기반 현장 위험물(높은 턱, 계단, 공사) 판독 파이프라인(`VisionHazardInspector`) 개발 (US-D1)
    - Structured JSON 출력 스키마 고정 및 안내판 파싱
  * **Member C (Backend / Routing / GIS Data Lead)**:
    - FastAPI 백엔드 구축 및 무상태 REST API 엔드포인트 구현
    - 전문 Routing API(ORS/OSRM) 어댑터, OSM Steps 필터링, DEM 경사도 분석, SunCalc 그림자 연산 모듈 개발 (US-B1, US-B2, US-B3, US-B4, US-G1)
  * **Member D (Frontend / Mobile UX Lead)**:
    - Next.js (App Router) PWA 모바일 반응형 웹 구축
    - **IndexedDB 로컬 스토리지 모듈 개발 (반려견 프로필, 개인 산책 궤적, JSON 백업/복원)** (US-A2, US-E1, US-E2)
    - 지도 시각화, Foreground GPS 위치 기록, 외부 지도(네이버/카카오) 딥링크 연동 (US-C1, US-C2)
  * **Member E (Infra / Data / QA Lead)**:
    - **Supabase Auth 간편 이메일/비밀번호 가입 연동 (Auto-confirm 활성화)**
    - 커뮤니티 공개 코스(`community_courses`) 및 위험 제보(`hazard_reports`) 스키마/스토리지 관리 (US-G2, US-F1)
    - **최소 5인 실사용자 필드 테스트 운영 및 품질 보증(QA) 총괄 (US-H1)**

---

## 2. 스프린트 일정 개요 (5주 로드맵)

```text
[Week 1] 코어 인프라 & 기본 라우팅 파이프라인 (환경 셋업, Supabase 간편 이메일 Auth, Routing API 연동)
   │
[Week 2] 로컬 스토리지 구축 & 라우팅 분석 모듈 (IndexedDB 반려견 프로필, OSM Steps, DEM 경사도, Scorer)
   │
[Week 3] 환경 연산, 비전 위험 분석 & PWA 결합 (Shade Estimation, Vision Hazard Inspector, 우회 재탐색, 통합 UI)
   │
[Week 4] 실사용 기능 완성 & 필드 테스트 착수 (Foreground GPS 로컬 기록, 출발지 200m 마스킹 커뮤니티 공유, 5인 CBT)
   │
[Week 5] 안정화, 품질 개선 및 최종 배포 (피드백 반영 튜닝, 로컬 데이터 백업 검증, 보안 최적화, 문서화)
```
* **총 Story Points**: **75 pt** (5인 팀 5주 완수)

---

## 3. 주차별 세부 구현 작업 (Week 1 ~ Week 5)

### Week 1: 코어 인프라 셋업, 간편 이메일 Auth & 기본 라우팅
* **주간 목표**: 개발 환경 통일, Supabase 간편 이메일 Auth 연동, 기본 Agent 상태 머신 정의, Routing API 연동 및 웹 지도 표시.
* **세부 작업**:
  * **Member A**: LangGraph 상태 그래프 정의, 자연어 발화 엔티티 추출 ReAct 프롬프트 초안 작성 (US-A1).
  * **Member B**: 현장 위험물(턱, 계단, 공사) 벤치마킹 이미지 20장 수집 및 Gemini Flash Few-shot 프롬프트 셋업 (US-D1).
  * **Member C**: FastAPI 보일러플레이트 구성, OpenRouteService / OSRM 라우팅 어댑터 기본 순환 루프 생성 구현 (US-B4).
  * **Member D**: Next.js App Router PWA 초기화, MapLibre GL JS 지도 뷰어 마운트 및 모바일 반응형 뷰포트 구성.
  * **Member E**: GitHub 협업 전략 수립, Supabase 프로젝트 생성 및 간편 이메일 Auth 연동 (Auto-confirm 활성화).

---

### Week 2: 로컬 스토리지 구축, 도메인 분석 & 후보 경로 평가
* **주간 목표**: 클라이언트 IndexedDB 로컬 스토리지 완성, OSM Steps 필터링, DEM 경사도 연산 모듈 완성.
* **세부 작업**:
  * **Member A**: 클라이언트가 요청 본문으로 보낸 `client_dog_context`를 파싱해 라우팅 도구로 주입하는 Stateless 체인 구현 (US-A1, US-A3).
  * **Member B**: `VisionHazardInspector` 1차 모듈 구현 (구조화 JSON 출력 규격화) (US-D1).
  * **Member C**: OSM `highway=steps` 배제 모듈(US-B1) 및 DEM 고도 데이터 기반 구간별 `max_slope_percent` 산출 로직 개발 (US-B2).
  * **Member D**: **IndexedDB 로컬 스토리지 매니저 개발** (반려견 프로필 등록 폼, JSON 파일 내보내기/가져오기 백업 뷰) (US-A2).
  * **Member E**: Supabase 커뮤니티 코스 및 위험 제보 테이블 DDL 배포, Week 2 중간 데모 진행.

---

### Week 3: 환경 연산, 비전 위험 분석 & 프론트엔드 통합
* **주간 목표**: SunCalc 건물 그림자 연산, 비전 위험 분석 결합, 위험 우회 재탐색, Next.js PWA 통합.
* **세부 작업**:
  * **Member A**: Vision 위험 분석 결과 수신 시 우회 경로 재탐색 에이전트 워크플로우 연결 (US-D2).
  * **Member B**: 저조도/각도 왜곡 사진 예외 처리 및 판독 지연 2.5초 이내 최적화 (US-D1).
  * **Member C**: `SunCalc` 태양각 및 건물 외곽선 기반 예상 그늘 비율(`shade_ratio`) 연산 모듈 개발 (Level 1~2) (US-B3) 및 우회 재탐색 API 구현.
  * **Member D**: 추천 경로 Polyline 색상 분기 렌더링, 외부 상용 지도(네이버/카카오 지도) 딥링크 버튼 연동, 현장 위험 사진 촬영 모달 연동 (US-C1, US-C2).
  * **Member E**: Supabase Storage 버킷 구성 및 백엔드 클라우드 배포(Render/Cloud Run).

---

### Week 4: GPS 산책 기록, 커뮤니티 공유, 부가 편의 & 실사용 테스트
* **주간 목표**: Foreground GPS 로컬 궤적 저장, 출발지 마스킹 커뮤니티 공유, 5인 실사용자 필드 테스트 착수.
* **세부 작업**:
  * **Member A**: 로컬에 누적된 피드백 요약을 요청 페이로드로 받아 다음 라우팅 가중치를 자동 보정하는 Stateless Memory 완성 (US-E3).
  * **Member B**: 실사용자 필드 업로드 사진 실시간 모니터링 및 판독 정확도 검증.
  * **Member C**: 전국 공영주차장 API 연동(US-G1) 및 기상청 단기예보 기반 열 위험 지수 산출(US-F1).
  * **Member D**: Foreground 위치 추적 모듈 개발 및 **수집된 궤적 로컬 스토리지에만 저장**(US-E1), 완주 후 보행 만족도 로컬 저장 뷰(US-E2).
  * **Member E [실사용 테스트 리드]**:
    - **간편 이메일 가입 및 코스 공유 연동**: 커뮤니티 공유 시 **출발지 200m 마스킹 블러링** 파이프라인 검증 (US-G2).
    - **5인 실사용자 필드 테스트 운영 (US-H1)**: 소형견/노령견 견주 5인 대상 PWA 배포, 계단 회피 및 프라이버시(로컬 저장) 만족도 설문 수집.

---

### Week 5: 안정화, 피드백 반영, 보안 최적화 & 최종 출시
* **주간 목표**: 필드 테스트 피드백 반영 튜닝, 로컬 데이터 백업/복원 검증, 보안 점검, 배포 및 운영 문서 완성.
* **세부 작업**:
  * **Member A**: 실사용자 발화 로그 분석을 통한 프롬프트 보정 및 가드레일 강화.
  * **Member B**: 비전 판독 임계치 최종 캘리브레이션.
  * **Member C**: 라우팅 연산 캐싱 적용으로 평균 응답 지연 3초 이내 달성.
  * **Member D**: 브라우저 캐시 삭제 시 JSON 복원 플로우 검증 및 크로스 브라우징(Safari/Chrome) 최적화.
  * **Member E**: API 키 은닉 점검, 5인 실사용자 테스트 평가 보고서 및 최종 운영 가이드 문서 정리 (US-H1).
