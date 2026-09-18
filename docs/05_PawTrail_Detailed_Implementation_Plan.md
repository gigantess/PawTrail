# [상세 구현 계획서] PawTrail 단계별 구현 로드맵 및 5인 협업 실행 계획

## 1. 프로젝트 개요 및 팀 구성 (5인 애자일 스크럼 체계)

* **프로젝트명**: PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 에이전트 및 기록·공유 플랫폼)
* **목표**: 5주간 스크럼 기반 2개 스프린트 및 Hardening 기간을 통해 기획, 노면 가중치 순환 라우팅, 비전 멀티모달 위험 판독, 산책 기록/커뮤니티, n8n 자동화 파이프라인 구축 및 퍼블릭 클라우드 배포와 최소 5인 실사용자 CBT 완수.
* **팀원별 역할 분담 (R&R)**:
  * **Member A (팀장 / AI Agent & Workflow Lead)**:
    - LangGraph 기반 Walk Planning Agent 상태 머신 설계 및 ReAct 프롬프트 엔지니어링 (US-01, US-02, US-16)
    - Pydantic V2 Strict Tool-calling 규격 수립, Long-term Memory 맥락 주입 및 전체 PM 총괄
  * **Member B (AI / Vision & Multimodal Lead)**:
    - Gemini 1.5 Flash 기반 공원 입구 종합안내판 비전 판독 파이프라인(`ParkBoardInspector`) 개발 (US-04)
    - Structured JSON 출력 스키마 고정, 산책 완주 후기 사진 노면 검증 및 커뮤니티 지도 보강 파이프라인(`CommunityMapEnricher`) 구현 (US-05)
  * **Member C (Backend & Spatial Routing Lead)**:
    - FastAPI 백엔드 구축 및 REST API 엔드포인트 구현 (SSE는 제외하고 예측 가능한 REST 구조 우선)
    - OSM 노면 결측치 보정을 위한 환경부 세분류 토지피복지도 GeoPandas Spatial Join 및 1.5km Seed 데이터셋 구축, Routing API Provider 연동 기반 순환형(Loop) 라우터 도구 개발 (US-02, US-03, US-13, US-16)
  * **Member D (Frontend & UI/UX Lead)**:
    - React Native (Expo SDK 51+) 및 TypeScript 기반 모바일 앱 구축 (US-07)
    - React Native Maps 기반 노면별 색상 구분 Polyline 렌더링, Android Foreground Service 및 expo-speech 기반 시선 해방(Eyes-Free) & 두 손 자유(Hands-Free) 백그라운드 음성 길 안내 구현 (US-07, US-08, US-09, US-14, US-15)
  * **Member E (Infra, Automation & QA Lead)**:
    - Firebase(Cloud Firestore) 기반 Long-term Memory DB 및 즐겨찾기 스키마, EAS Build(1회 Android APK) 및 EAS Update(무선 OTA)/Render CI/CD 배포 자동화 (US-06, US-10, US-14)
    - n8n 기상청 지면열 연동 일일 산책 골든타임 알림 워크플로우 구축 (US-12)
    - **최소 5인 실사용자 CBT 운영, 피드백 수집 및 분석 리포트 총괄 (US-11)**

---

## 2. 스프린트 일정 개요 (5주 로드맵)

```
[Sprint 1 (Week 1~2)] 코어 AI 파이프라인 & 라우팅 엔진 구축 (29 pt)
       │
[Sprint 2 (Week 3~4)] 서비스 통합, 기록/커뮤니티/즐겨찾기, 배포 및 5인 CBT (28 pt)
       │
[Hardening & Launch (Week 5)] 피드백 반영 고도화, 문서화 및 최종 데모 (5 pt)
```
* **총 Story Points**: **62 pt** (Sprint 1: 29 pt, Sprint 2: 28 pt, Hardening: 5 pt)
* **총 개발 공수**: **334 Hours** (55개 Task, 5인 팀 기준)

---

## 3. 주차별 세부 구현 작업 (Step-by-Step)

### Week 1 (Sprint 1 시작): 도메인 데이터 인프라 및 AI 코어 셋업
* **주간 목표**: 개발 환경 통일, OSM 노면 데이터 파이프라인 검증, Agent 상태 머신 정의, Git 협업 룰 확립.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - LangGraph State 정의 (`messages`, `dog_profile`, `preferred_surfaces`, `route_result`).
    - 자연어 입력에서 견종, 산책 시간, 선호 노면을 추출하는 ReAct 시스템 프롬프트 초안 작성 및 테스트 (US-01).
  * **Member B (Vision AI)**:
    - 공원 종합안내판 15장 및 노면 근접 촬영 20장(흙, 잔디, 자갈 등) 벤치마킹 데이터셋 구축.
    - Gemini 1.5 Flash API 연동 및 `ParkBoardInspector` Few-shot 프롬프트 벤치마킹 (US-04).
  * **Member C (Backend/GIS)**:
    - 테스트베드 구역 OSM 보행 네트워크 데이터(.osm.pbf) 파싱 및 NetworkX 그래프 생성.
    - 환경부 세분류 토지피복지도(SHP) 다운로드 및 GeoPandas Spatial Join 파이프라인 구축. 항공·로드뷰 교차 검증 1.5km Seed 데이터셋 구축 착수 (US-03).
  * **Member D (Frontend)**:
    - React Native Expo SDK 51+ 프로젝트 보일러플레이트 구성 및 Android 빌드 환경 설정.
    - React Native Maps 컴포넌트 초기화 및 맵 캔버스/컨트롤 UI 구성.
  * **Member E (Infra/QA)**:
    - GitHub Organization 세팅, Git-flow 브랜치 전략(`main`, `develop`, `feature/*`), PR 템플릿 확립.
    - Firebase 프로젝트 생성 및 Cloud Firestore 컬렉션(`users`, `dogs`, `walk_history`, `feedback`) 및 Security Rules 배포 (US-06).

### Week 2 (Sprint 1 종료): 개별 AI 모듈 독립 구현 & 노면 가중치 라우팅
* **주간 목표**: 사용자 선호 노면 순환 라우팅 완료, 비전 판독 및 메모리 모듈 단위 테스트 100% 통과.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - Pydantic V2 Strict Schema 기반 자율 호출 도구 3종 바인딩 (`get_dog_context`, `generate_loop_route`, `inspect_park_board`).
    - 선호 노면 파라미터가 누락되었을 때의 사용자 명확화 질문(Clarification) 대화 루프 구현.
    - 목표 산책 시간(Target Duration) 칩/슬라이더 및 자연어 발화 파라미터 매핑 바인딩 (US-16).
  * **Member B (Vision AI)**:
    - `ParkBoardInspector` 모듈 완성: 공원명, 노면 범례, 반려견 출입 금지/허용 구역 구조화 JSON 파싱 (US-04).
    - 예외 처리: 저조도/반사광/각도 왜곡 사진 입력 시 신뢰도 부족 경고 및 재촬영 요청 로직 추가.
  * **Member C (Backend/GIS)**:
    - 사용자 선호 노면 할인 계수($W_{\text{pref}} = 0.4 \sim 0.5$) 및 페널티 계수 비용 함수 모듈 개발 (US-02).
    - `LandCoverSpatialService` 연동으로 OSM 결측 링크의 80% 이상을 흙/잔디/인공포장으로 정밀 판별하고 1.5km Seed 데이터셋 확정 (US-03).
    - 출발점 기준 다각형 경유지(Waypoint) 샘플링 및 Routing API(ORS/OSRM) 연동 순환 루프 코스 생성 모듈 구현 (US-03).
    - 반려견 체급/건강상태별 보행 속도 매핑 기반 목표 보행 거리 자동 환산 엔진 및 $\pm 10\%$ 시간 수렴 라우터 검증 (US-16).
  * **Member D (Frontend)**:
    - 선호 노면 선택 칩 UI(흙길, 잔디길, 탄성포장, 보도블록) 및 에이전트 채팅 버블 컴포넌트 개발.
    - 공원 안내판 촬영 및 후기 사진 업로드 컴포넌트 구현.
  * **Member E (Infra/QA)**:
    - Firebase Cloud Firestore 기반 Long-term Memory CRUD API 구현 및 에이전트 연동 테스트 (US-06).
    - Sprint 1 리뷰 및 데모 진행 (중간 산출물 점검).

### Week 3 (Sprint 2 시작): 서비스 통합, 산책 기록 & n8n 자동화
* **주간 목표**: Frontend-Backend-AI E2E 통합, GPS 실시간 트래킹 및 커뮤니티 피드 개발, n8n 알림 구축.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - Long-term Memory 맥락 주입 파이프라인 결합 (과거 산책 피로도 및 질환 이력 반영).
    - 공원 안내판 판독 결과(반려견 금지구역 Block)와 라우팅 엔진 간의 제약조건 주입 체인 완성.
  * **Member B (Vision AI)**:
    - `CommunityMapEnricher` 모듈 완성: 완주 후기 사진 노면 재질 판독, 신뢰도(0.85 임계치) 및 위험요소 검증 파이프라인 구현 (US-05).
  * **Member C (Backend/GIS)**:
    - 완주 후기 비전 판독 결과(신뢰도 0.85 이상)를 바탕으로 DB 내 OSM Way의 surface 속성을 영구 보강하는 핸들러 연동 (US-05).
    - 전국공영주차장 표준 API 연동 모듈 개발 (출발지 인근 P&R 코스 도출) (US-13).
    - 추천 경로 GeoJSON 및 구간별 노면 속성 반환 REST API 최적화 (응답 지연 1.5초 이내 달성).
  * **Member D (Frontend)**:
    - 추천 경로 Polyline 노면별 색상 분기 렌더링 (잔디: 초록, 흙: 갈색, 탄성포장: 주황, 아스팔트: 회색) (US-07).
    - Android Foreground Service 기반 백그라운드 GPS 위치 추적과 expo-speech TTS 연동 시선 해방 & 두 손 자유 핸즈프리 음성 길 안내("50m 앞 부드러운 흙길입니다. 우회전하세요") 엔진 및 완주 후 '선호 노면 달성률(%)' 카드 렌더링 (US-08).
    - OSRM/ORS steps 회전 안내 및 노면 속성 연동 사전 음성 가이드 구현 (US-07).
    - 산책 경로 상세 및 완주 카드 내 북마크(나만의 코스) 원터치 토글 및 보관함 목록 UI 구현 (US-14).
  * **Member E (Infra/QA)**:
    - n8n 워크플로우 구현: 기상청 단기예보 조회 → 지면열 회귀 연산 → 35℃ 이하 골든타임 웹훅 알림 발송 (US-12).
    - 커뮤니티 피드 컬렉션 구축 및 산책 완주 기록 저장 연동 (US-09).
    - 즐겨찾기(북마크) CRUD API (`POST /api/walks/{id}/favorite`, `GET /api/favorites`) 및 Cloud Firestore(`users/{userId}/favorites`) 연동 (US-14).

### Week 4 (Sprint 2 종료): 외부 클라우드 배포 & 실사용자 5인 CBT
* **주간 목표**: 외부 접근 가능한 퍼블릭 배포 완료, 실사용자 5인 이상 섭외 및 필드 테스트 수행, 1차 피드백 수집.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - 실사용자 대화 로그 모니터링, 프롬프트 인젝션 방어 가드레일 및 AI 시뮬레이션 고지 UI 검증 (US-10).
  * **Member B (Vision AI)**:
    - 실사용자가 필드에서 업로드한 공원 안내판 및 산책 후기 노면 사진 판독 결과 실시간 모니터링 및 임계값 캘리브레이션 (US-04, US-05).
  * **Member C (Backend/GIS)**:
    - Render / Cloud Run 프로덕션 환경 배포, 도메인 연결, CORS 설정 및 부하 테스트.
  * **Member D (Frontend)**:
    - EAS Build 기반 1회 Android APK 빌드 및 테스터 배포, EAS Update 기반 GitHub Actions 연동 무선 OTA 즉시 업데이트 파이프라인 가동 (US-10).
    - AsyncStorage 기반 추천 경로 GeoJSON 로컬 사전 캐싱, 오프라인 감지 토스트 및 로컬 체크인 임시저장/온라인 재접속 동기화 모듈 개발 (US-15).
    - 인앱 사용자 만족도 평가 및 피드백 입력 모달 배포 (US-09, US-11).
  * **Member E (Infra/QA) [핵심 총괄]**:
    - **실사용자 CBT 운영 (US-11)**:
      - 반려견 견주 5명(소형견 2, 중/대형견 2, 관절 안심 케어견 1) 섭외 및 APK/OTA 서비스 전달.
      - 5개 검증 시나리오에 따라 실제 필드 산책 1회 이상 수행(핸즈프리 음성 안내 포함) 및 설문 수집.
    - 테스터 피드백 취합 대시보드 작성 및 긴급 버그 핫픽스 관리.

### Week 5 (Hardening & Launch): 피드백 반영 기능 고도화 & 최종 데모
* **주간 목표**: 수집된 사용자 피드백을 기반으로 가중치/프롬프트 개선 배포, GitHub 문서화 및 발표 완비.
* **팀원별 세부 구현 태스크**:
  * **Member A (AI Agent)**:
    - 피드백 반영: "선호 노면 비중이 부족함" 의견 수용 → $W_{\text{pref}}$ 계수 0.5에서 0.35로 강화하여 재배포.
    - AI Agent 설계 근거 및 기술적 의사결정 보고서 정리.
  * **Member B (Vision AI)**:
    - 피드백 반영: 안내판 반사광/각도 왜곡 및 복합 노면(흙+자갈) 판독 프롬프트 보정.
  * **Member C (Backend/GIS)**:
    - 피드백 반영: 순환 코스 오차 허용범위 축소 (목표 거리 대비 $\pm 15\%$ → $\pm 10\%$ 이내 튜닝, CBT 피드백 기반 점진 수렴).
  * **Member D (Frontend)**:
    - 음성 안내 턴 사전 알림 타이밍(30m 전) 튜닝 및 주머니 보관 중 오디오 큐 가독성 개선, 시연 데모 비디오 녹화.
  * **Member E (Infra/QA)**:
    - GitHub `README.md` 최종 정비 (아키텍처, 5인 R&R, 기술 스택, 실행 방법, CBT 피드백 반영 내역).
    - 최종 프로젝트 결과 발표 슬라이드(PDF) 제작 및 미션 체크리스트 전수 검증.

---

## 4. 실사용자(5인) CBT 운영 및 검증 계획 (US-11)

| 테스터 ID | 대상 반려견 프로필 | 테스트 시나리오 | 검증 지표 | Week 5 피드백 반영 계획 |
|:---:|---|---|---|---|
| **Tester 1** | 말티즈 (4세, 관절 안심 케어 집중견) | "흙길+잔디길" 선택 후 15분 코스 생성 및 핸즈프리 음성 산책 | 흙/잔디길 달성률, 음성 안내 편의성, 관절 부담도 | 아스팔트 회피 페널티 3.0으로 상향 |
| **Tester 2** | 골든 리트리버 (3세, 대형견) | "주차장 출발" 40분 원정 산책 코스 생성 및 산책 | 주차장 도보 접근성, 코스 만족도 | 공영주차장 연계 반경 1.5km로 확장 |
| **Tester 3** | 푸들 (11세, 노령견) | 한낮 폭염 시 "탄성포장/흙길" 20분 코스 생성 | 지면열 체감, 보행 편의성 | 평지 우선 경사도 회피 가중치 보정 |
| **Tester 4** | 웰시코기 (5세, 일반 보행) | 공원 입구 종합안내판 촬영 업로드 및 산책 후기 사진 검증 | 안내판 판독 정확도, 후기 사진 노면 반영 속도 | 안내판 내 반려견 금지구역 파싱 프롬프트 보강 |
| **Tester 5** | 비숑 프리제 (2세, 활동견) | n8n 골든타임 알림 수신 후 즉시 산책 완주 | 알림 적시성, 커뮤니티 공유 기능 | 알림 발송 시각을 골든타임 45분 전으로 조정 |

---

## 5. 최종 산출물 및 미션 체크리스트

* [x] **기획서 및 애자일 요구사항 명세서 완비**: MoSCoW, DoD, 스토리 포인트 명시
* [x] **필수 AI 기술 4종 적용**: AI Agent, Vision 멀티모달, Long-term Memory, n8n 워크플로우
* [x] **외부 퍼블릭 배포**: EAS Build(APK) & EAS Update(OTA) + Render(Back) 상시 서비스 환경 확보
* [x] **실사용자 5인 이상 CBT 완수**: 5개 페르소나별 필드 산책 수행 및 설문 결과 확보
* [x] **사용자 피드백 기반 서비스 개선**: Week 5 프롬프트 및 라우팅 가중치 튜닝 재배포
* [x] **GitHub 버전 관리 및 문서화**: 5인 R&R, 아키텍처 다이어그램, 실행 가이드 완비
* [x] **발표 자료 준비**: 최종 결과 발표 슬라이드 및 서비스 시연 영상 준비
