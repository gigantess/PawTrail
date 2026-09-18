# [작업 분할 명세서] PawTrail 사용자 스토리별 상세 구현 Task 및 작업량 추정

## 1. 개요 및 추정 기준

* **프로젝트명**: PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 에이전트 및 기록·공유 플랫폼)
* **목적**: 16개 사용자 스토리(US-01 ~ US-16)를 실제 개발 가능한 단위의 하위 Task로 분할하고, 애자일 추정치(Story Points, 공수 Hours) 및 담당자를 지정하여 5주 스프린트 수행의 명확한 실행 지침 제공.
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

#### US-03: Waypoint 최적화, Routing API(ORS/OSRM) 연동 및 토지피복도 노면 보정 (8 pt / 총 38h)
* **담당**: Member C, A | **스프린트**: Sprint 1 (Week 1~2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-03-1**: 테스트베드 OSM 도로망(.pbf) 파싱 및 NetworkX 그래프/인덱스 적재 파이프라인 구축 (10h / Member C)
    - 도보 통행 가능 링크(`highway=footway, pedestrian, path`) 추출 및 지오메트리 변환.
  * **TASK-03-2**: 환경부 세분류 토지피복지도 GeoPandas Spatial Join 및 1.5km Seed 데이터셋 구축 (8h / Member C)
    - 공원 내부 OSM 링크 지오메트리와 환경부 피복도 폴리곤(초지, 나지, 인공포장) 공간 결합, 결측치 80% 이상 고정밀 보정 및 항공·로드뷰 교차 검증 1.5km Seed 데이터셋 구축 (`surface_source` 5단계 투명성 태깅).
  * **TASK-03-3**: 다각형 경유지(Waypoint) 샘플링 및 Routing API(ORS/OSRM) 연동 순환 루프 생성 모듈 개발 (12h / Member C)
    - 단순 왕복(U턴) 방지 및 목표 거리 대비 $\pm 15\%$ 허용 오차 내 대안 루프 경로 산출.
  * **TASK-03-4**: 라우터 벤치마크 테스트 및 경로 생성 시간 2초 이내 최적화 (8h / Member C)
    - Routing Provider 어댑터 구조 적용 및 캐싱을 통한 지연시간 최소화.

#### US-16: 사용자 지정 산책 시간(Target Duration) 기반 맞춤형 코스 생성 (3 pt / 총 16h)
* **담당**: Member A, C (Sub: Member D) | **스프린트**: Sprint 1 (Week 1~2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-16-1**: 플래너 UI 산책 시간 원터치 칩(15/30/45/60분) 및 슬라이더 UI, 자연어 발화 시간 파싱 바인딩 (4h / Member A, D)
    - 5분 단위 산책 시간 선택 인터페이스 및 Agent 입력 인자 추출/검증 연계.
  * **TASK-16-2**: 견종 체급/건강 상태별 보행 속도 매핑 및 목표 보행 거리 자동 환산 엔진 구현 (6h / Member C)
    - 소형견(3.0km/h), 중형견(3.6km/h), 대형견(4.2km/h), 관절주의견(2.4km/h) 속도 기준 $\text{Target Distance} = \text{Walking Speed} \times \text{Target Duration}$ 공식 모듈 개발.
  * **TASK-16-3**: 생성 코스의 예상 소요 시간 허용 오차($\pm 10\%$ 또는 $\pm 3$분) 검증 및 수렴 라우터 단위 테스트 (6h / Member C)
    - 다각형 Waypoint 탐색 반경 자동 조율 및 15분, 30분, 60분 테스트 케이스 오차 범위 검증.

---

### [Epic 2] 비전 멀티모달 안내판 분석 및 커뮤니티 지도 보강

#### US-04: 공원 종합안내판 비전 판독 및 산책 제약조건 도출 (5 pt / 총 26h)
* **담당**: Member B | **스프린트**: Sprint 1 (Week 1~2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-04-1**: 공원 입구 종합안내판(15장) 및 노면 샘플 이미지 수집 및 벤치마크 데이터셋 구축 (6h / Member B)
    - 보라매공원 등 공원 종합안내판 사진 수집, 노면 범례 및 반려견 출입 금지구역 Ground Truth 라벨링.
  * **TASK-04-2**: Gemini 1.5 Flash 비전 프롬프트 설계 및 Few-shot 최적화 (8h / Member B)
    - `ParkBoardInspector` 시스템 프롬프트: 공원명, 흙길/산책로 범례 식별, 잔디마당/어린이놀이터 등 반려견 출입 금지구역 JSON 추출.
  * **TASK-04-3**: Pydantic 기반 Structured JSON Output 파서 및 제약조건 변환 모듈 구현 (6h / Member B)
    - `ParkBoardInspectionResult` 스키마 바인딩, `restricted_zones`를 라우팅 금지 노드로 자동 변환하는 어댑터 개발.
  * **TASK-04-4**: 반사광/각도 왜곡 사진 예외 처리 및 안내판 판독 단위 테스트 자동화 (6h / Member B)
    - 저조도/각도 왜곡 사진 입력 시 신뢰도 부족 경고 및 15장 테스트베드 안내판 데이터셋 기준 85% 이상 파싱 정확도 검증.

#### US-05: 완주 후기 사진 비전 검증 기반 지도 속성 영구 보강 (3 pt / 총 16h)
* **담당**: Member B, C | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-05-1**: 산책 완주 후기 사진 노면 판독 및 신뢰도 검증 파이프라인 구현 (6h / Member B)
    - Gemini Flash 기반 `CommunityMapEnricher`: 흙/잔디/자갈 노면 분류, `confidence >= 0.85` 임계치 판정 및 위험물(깨진 유리 등) 검출.
  * **TASK-05-2**: OSM Way 노면 속성 영구 업데이트 및 신뢰도 미달 격리 핸들러 개발 (6h / Member C, B)
    - 신뢰도 0.85 이상 시 DB 내 Way ID의 `surface`를 `community_verified`로 영구 갱신, 0.85 미만은 수동 검토 대기 큐로 격리.
  * **TASK-05-3**: 완주 후기 사진 업로드부터 지도 속성 갱신 및 커뮤니티 피드 반영 E2E 테스트 (4h / Member B, C)
    - 사진 업로드, 비전 검증, DB 링크 속성 갱신, 후기 등록 응답까지 2.5초 이내 완료 검증.

---

### [Epic 3] 개인화 Long-term Memory

#### US-06: 반려견 건강 프로필 및 과거 산책 이력 기억 (3 pt / 총 18h)
* **담당**: Member E (Sub: Member A) | **스프린트**: Sprint 1 (Week 2)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-06-1**: Supabase 테이블 DDL 설계 (`users`, `dogs`, `walk_history`, `feedback`) (4h / Member E)
    - 견종, 관절 안심 케어 수준(0~4), 선호 노면 배열, 산책 거리/시간/노면비율 필드 구성.
  * **TASK-06-2**: Long-term Memory 조회/적재 FastAPI 비동기 CRUD 모듈 구현 (6h / Member E)
    - 유저 세션별 반려견 프로필 및 최근 5회 산책 요약 데이터 캐싱 및 조회 함수 작성.
  * **TASK-06-3**: LangGraph Agent 노드 내 이전 산책 맥락(피로도, 선호도) 동적 인젝션 (8h / Member A)
    - "지난 산책에서 언덕을 힘들어함" 피드백을 시스템 프롬프트의 동적 제약조건으로 주입.

#### US-14: 마음에 드는 안심 산책로 '나만의 코스(즐겨찾기)' 보관 (2 pt / 총 12h)
* **담당**: Member D, E | **스프린트**: Sprint 2 (Week 3~4)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-14-1**: 즐겨찾기 북마크 추가/삭제 및 목록 조회 REST API 구현 (5h / Member E)
    - `POST /api/walks/{id}/favorite` 및 `GET /api/favorites` 엔드포인트 구현, Supabase `favorites` 테이블 DDL 및 RLS 정책 적용.
  * **TASK-14-2**: 프론트엔드 북마크 토글 버튼 및 보관함 '나만의 코스' 목록 UI 컴포넌트 개발 (7h / Member D)
    - 산책 상세 및 완주 카드 내 북마크 아이콘 원터치 토글, 프로필/보관함 탭에서 저장된 코스 목록(거리, 노면비율, 시간) 즉시 조회 및 맵 렌더링 연동.

---

### [Epic 4] 서비스 인터페이스 & 외부 배포

#### US-07: 지도 기반 추천 경로 시각화 및 OSRM 회전 안내 연동 (5 pt / 총 26h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-07-1**: React Native Maps 연동 및 노면별 색상 구분 Polyline 렌더링 (8h / Member D)
    - 잔디(초록), 흙(갈색), 탄성포장(주황), 아스팔트(회색) 분기 렌더링.
  * **TASK-07-2**: 코스 요약 카드 UI 구현 (거리, 시간, 선호 노면 비율 % 표시) (6h / Member D)
    - 반응형 바텀시트 및 노면 달성 예상치 프로그레스 바 제작.
  * **TASK-07-3**: OSRM/ORS steps 기반 턴 정보 및 구간 노면 속성 파싱 모듈 구현 (4h / Member D)
    - 회전 명령(좌/우회전 등) 및 노면 속성을 음성 안내 큐로 가공.
  * **TASK-07-4**: Android 실기기 뷰포트 반응형 레이아웃 및 제스처 최적화 (8h / Member D)
    - 터치 제스처 최적화 및 맵 뷰어 안정성 검증.

#### US-08: 시선 해방(Eyes-Free) & 두 손 자유(Hands-Free) 백그라운드 음성 길 안내 및 선호 노면 달성률 (5 pt / 총 26h)
* **담당**: Member D (Sub: Member E) | **스프린트**: Sprint 2 (Week 3)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-08-1**: Android Foreground Service 기반 백그라운드 GPS 위치 트래커 및 화면 꺼짐 지속 유지 (8h / Member D)
    - 스마트폰을 주머니나 가방에 넣고 화면을 끈 상태에서도 위치 추적이 백그라운드에서 중단 없이 지속되도록 구현.
    - 일시적 GPS 오차 발생 시 추천 경로 링크 스냅(Dead Reckoning) 보정 처리.
  * **TASK-08-2**: expo-speech TTS 기반 턴/노면 사전 음성 길 안내 엔진 구현 (6h / Member D)
    - 30m 전 회전 지점 도달 시 "50m 앞 부드러운 흙길입니다. 우회전하세요" 사전 음성 브리핑 및 경로 이탈 알림.
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

#### US-10: EAS Build/Update 기반 무선 배포 및 AI 윤리/면책 고지 (3 pt / 총 16h)
* **담당**: Member E (Sub: Member C, D) | **스프린트**: Sprint 2 (Week 4)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-10-1**: EAS Build 기반 1회 Android APK 빌드 및 EAS Update(OTA) 무선 배포 파이프라인 구축 (6h / Member E, D)
    - GitHub Actions 연계 무선 업데이트 환경 구성 및 테스터 즉시 배포.
  * **TASK-10-2**: Render(Backend) 배포 환경 구축 및 CORS 보안 점검 (4h / Member C, E)
    - 배포 도메인 화이트리스트 등록 및 모바일 앱 API 호출 테스트.
  * **TASK-10-3**: AI 윤리 고지 문구 및 백그라운드 위치정보 권한 동의 모달 구현 (6h / Member D, E)
    - "AI 분석 결과는 산책 계획을 위한 참고 정보이며 의료적 진단이 아닙니다" 상단 배너 배치 및 동의 토글 구현.

#### US-15: 네트워크 단절 시 오프라인 지도 캐시 및 산책 유지 (2 pt / 총 10h)
* **담당**: Member D | **스프린트**: Sprint 2 (Week 4)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-15-1**: AsyncStorage 기반 추천 경로 GeoJSON 및 지도 타일 로컬 사전 캐싱 모듈 구현 (5h / Member D)
    - 코스 생성 시 해당 경로 주변의 벡터 타일과 GeoJSON 데이터를 기기 로컬 캐시에 즉각 프리캐싱.
  * **TASK-15-2**: NetInfo 기반 네트워크 단절 감지 토스트 UI 및 로컬 체크인 임시 저장/자동 동기화 구현 (5h / Member D)
    - 오프라인 상태 안내 토스트 및 오프라인 산책 완료 시 로컬 스토리지 임시 보관, 네트워크 복구 시 백엔드 DB 자동 동기화.

---

### [Epic 5] 실사용자(CBT) 검증 & 자동화 파이프라인

#### US-11: 최소 5인 이상 실사용자(견주) CBT 및 피드백 반영 (5 pt / 총 30h)
* **담당**: 전원 (Lead: Member E) | **스프린트**: Sprint 2 (Week 4) ~ Hardening (Week 5)
* **상세 작업 분할 (Task Breakdown)**:
  * **TASK-11-1**: 견주 5인 섭외 및 페르소나별 테스트 시나리오/설문지(구글 폼) 설계 (6h / Member E)
    - 소형견(관절 안심 케어), 대형견(P&R), 노령견, 일반견, 활동견 5개 타깃 구성.
  * **TASK-11-2**: 5인 테스터 배포 링크 전달, 필드 산책 1회 이상 완주 가이드 및 결과 수집 (8h / 전원)
    - 실제 현장 산책 후 선호 노면 일치율, 음성 안내 편의성, 비전 노면 판독 만족도 설문 데이터 확보.
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
| **US-03** | Waypoint 최적화, Routing API(ORS/OSRM) 연동 및 토지피복도 노면 보정 | Member C, A | 8 pt | 4개 | 38 h |
| **US-04** | 공원 종합안내판 비전 판독 및 산책 제약조건 도출 | Member B | 5 pt | 4개 | 26 h |
| **US-05** | 완주 후기 사진 비전 검증 기반 지도 속성 영구 보강 | Member B, C | 3 pt | 3개 | 16 h |
| **US-06** | 반려견 프로필 및 산책 이력 기억 (Memory) | Member E, A | 3 pt | 3개 | 18 h |
| **US-07** | 지도 시각화 및 OSRM 회전 안내 연동 | Member D | 5 pt | 4개 | 26 h |
| **US-08** | 핸즈프리 음성 길 안내 및 선호 노면 달성률 | Member D, C | 5 pt | 4개 | 26 h |
| **US-09** | 커뮤니티 피드 공유 및 피드백 제출 | Member D, E | 3 pt | 3개 | 16 h |
| **US-10** | EAS 무선 배포 및 AI 윤리 고지 | Member E, C, D | 3 pt | 3개 | 16 h |
| **US-11** | 최소 5인 이상 실사용자 CBT 및 피드백 반영 | 전원 (Lead: E) | 5 pt | 4개 | 30 h |
| **US-12** | 기상청 지면열 연동 골든타임 알림 (n8n) | Member E | 3 pt | 3개 | 16 h |
| **US-13** | 공영/민영 주차장(P&R) 코스 탐색 | Member C | 2 pt | 3개 | 12 h |
| **US-14** | 나만의 안심 코스 즐겨찾기(북마크) 보관 | Member D, E | 2 pt | 2개 | 12 h |
| **US-15** | 오프라인 지도 캐시 및 산책 유지 (Expo) | Member D | 2 pt | 2개 | 10 h |
| **US-16** | 산책 시간(Target Duration) 기반 맞춤형 코스 생성 | Member A, C | 3 pt | 3개 | 16 h |
| **합계** | **16개 사용자 스토리 전수 분할** | **5인 팀 전원** | **62 pt** | **54개 Task** | **330 h (약 324h)** |

---

## 4. 팀원별 담당 공수 배분 현황 (5인 밸런스 검증)

* **Member A (AI Agent Lead)**: 62 h (US-01, US-02 일부, US-06 일부, US-11, US-16)
* **Member B (Vision AI Lead)**: 48 h (US-04, US-05, US-11)
* **Member C (Backend/GIS Lead)**: 90 h (US-02, US-03, US-05 일부, US-10 일부, US-13, US-16)
* **Member D (Frontend Lead)**: 79 h (US-07, US-08, US-09, US-11, US-14, US-15)
* **Member E (Infra/QA Lead)**: 51 h (US-06, US-10, US-11 총괄, US-12, US-14)
* **총 개발 공수**: **330 Hours (약 324h)** (개발자 1인당 5주간 주당 평균 약 13.2시간 순수 구현 투입으로 일정 리스크 없이 완수 가능)
