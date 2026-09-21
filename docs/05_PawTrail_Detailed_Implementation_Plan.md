# [상세 구현 계획서] PawTrail 단계별 구현 로드맵 및 5인 협업 실행 계획

## 1. 프로젝트 개요 및 팀 구성 (5인 애자일 체계)

* **프로젝트명**: PawTrail (반려견 맞춤형 안심 산책 에이전트 및 핸즈프리 모바일 플랫폼)
* **핵심 기술 스택**:
  - **모바일 클라이언트**: **React Native (Expo SDK 51+)**
  - **핸즈프리 보행 엔진**: Android Foreground Service + `expo-location` + `expo-speech` TTS
  - **무중단 배포**: `EAS Build` (1회 테스터 APK 배포) + `EAS Update (`expo-updates`)` (무선 OTA 핫픽스)
  - **프라이버시 로컬 저장**: `@react-native-async-storage/async-storage` (반려견 프로필, 개인 궤적)
  - **백엔드**: FastAPI (Python 3.11+) Stateless REST API
  - **데이터베이스 & 인증**: Supabase Cloud (간편 이메일/비밀번호 Auth, 200m 마스킹 커뮤니티 코스)
* **팀원별 역할 분담 (R&R)**:
  * **Member A (팀장 / AI Agent & Product Logic Lead)**:
    - LangGraph 기반 Walk Planning Agent 설계 및 무상태(Stateless) 프롬프트 오케스트레이션 (US-A1, US-A3, US-E3).
    - Pydantic V2 Strict Tool-calling 규격 수립, 클라이언트 로컬 프로필/피드백 페이로드 바인딩 및 음성 안내용 요약 브리핑 생성.
  * **Member B (Vision / Multimodal AI Lead)**:
    - Gemini 1.5 Flash 기반 현장 위험물(높은 턱, 계단, 공사) 판독(`VisionHazardInspector`) 및 공원 종합안내판 비전 판독(`ParkBoardInspector`) 개발 (US-D1, US-D2).
    - 비전 분석 신뢰도(Confidence >= 0.85) 임계치 판정 및 지도 속성 보강 파이프라인.
  * **Member C (Backend / Routing / GIS Data Lead)**:
    - FastAPI 백엔드 구축, OSM 계단 배제(`highway=steps`), DEM 경사도 연산 및 그늘 지표 산출 파이프라인 (US-B1, US-B2, US-B3, US-B4).
    - 전문 Routing API(OpenRouteService/OSRM) 연동 및 후보 경로 다요소 스코어링 엔진 개발.
  * **Member D (Frontend / Mobile UX Lead)**:
    - React Native Expo (SDK 51+) 클라이언트 개발 및 React Native Maps 색상 분기 렌더링 (US-C1, US-C2).
    - **Android Foreground Service 기반 백그라운드 GPS 위치 추적 및 expo-speech TTS 음성 안내 엔진** (US-E1, US-E2).
    - **Local-First AsyncStorage 로컬 스토리지 매니저** 및 나만의 코스 즐겨찾기 보관함 (US-A2, US-E3).
  * **Member E (Infra / DevOps & QA Lead)**:
    - **EAS Build(1회 APK) 및 EAS Update(무선 무점검 OTA) CI/CD 파이프라인** (US-H2).
    - Supabase Cloud 간편 이메일/비밀번호 회원가입 및 커뮤니티 공개 코스/제보 테이블 구축 (US-G1, US-G2).
    - n8n 기반 기상청 지면열 연동 알림 자동화 파이프라인(US-F1) 및 5인 CBT 검증 총괄(US-H1).

---

## 2. 스프린트 일정 개요 (5주 로드맵)

```text
[Week 1] 코어 인프라 & Expo 환경 셋업 (Expo SDK 51+, Supabase 간편 이메일 Auth, Routing API 연동)
   │
[Week 2] 로컬 스토리지 구축 & 라우팅 분석 (AsyncStorage 반려견 프로필, OSM Steps, DEM 경사도, Scorer)
   │
[Week 3] 환경 연산, 비전 위험 & 음성 안내 엔진 (SunCalc 그늘, Vision Inspector, expo-speech 음성 길 안내)
   │
[Week 4] 백그라운드 트래킹, EAS 배포 & 5인 CBT (Foreground Service GPS, EAS Build APK, EAS Update OTA, 5인 테스트)
   │
[Week 5] 무선 OTA 핫픽스, 피드백 반영 & 최종 안정화 (EAS Update 실시간 배포, 로컬 백업 검증, 최종 출시)
```
```text
[Sprint 1 (Week 1~2)] 코어 AI 파이프라인 & 라우팅 엔진 구축 (33 pt)
       │
[Sprint 2 (Week 3~4)] 모바일 통합, 음성안내, 커뮤니티, EAS 배포 및 5인 CBT (36 pt)
       │
[Hardening & Launch (Week 5)] 피드백 반영 고도화, 문서화 및 최종 데모 (8 pt)
```
* **총 Story Points**: **77 pt** (5인 팀 5주 완수)
* **총 개발 공수**: **372 Hours** (18개 스토리, 72개 세부 Task)

---

## 3. 주차별 세부 구현 작업 (Week 1 ~ Week 5)

### Week 1: 코어 인프라 셋업, Expo 보일러플레이트 & 기본 라우팅
* **주간 목표**: 개발 환경 통일, Expo 프로젝트 초기화, Supabase 간편 이메일 Auth 연동, 기본 라우팅 API 연결, Git 협업 룰 확립.
* **세부 작업**:
  * **Member A**: LangGraph 상태 그래프 정의, 자연어 발화 엔티티 추출 ReAct 프롬프트 초안 작성 및 Pydantic V2 스키마 정의 (US-A1).
  * **Member B**: 현장 위험물(턱, 계단, 공사) 벤치마킹 이미지 20장 및 공원 종합안내판 이미지 15장 수집, Gemini Flash Few-shot 프롬프트 셋업 (US-D1).
  * **Member C**: FastAPI 보일러플레이트 구성, OpenRouteService / OSRM 라우팅 어댑터 기본 순환 루프 생성 구현 (US-B4).
  * **Member D**: React Native Expo SDK 51+ 프로젝트 초기화, react-native-maps 컴포넌트 마운트 및 모바일 화면 구성.
  * **Member E**: GitHub 레포지토리 세팅, EAS CLI 환경 구성 및 Supabase 간편 이메일 Auth 연동 (Auto-confirm 활성화), SonarLint CI 게이트 셋업.

---

### Week 2: 로컬 스토리지 구축, 도메인 분석 & 후보 경로 평가
* **주간 목표**: AsyncStorage 로컬 스토리지 완성, OSM Steps 필터링, DEM 경사도 연산 모듈 완성.
* **세부 작업**:
  * **Member A**: 클라이언트 로컬 프로필(`client_dog_context`)을 요청 본문으로 받아 라우팅 도구로 주입하는 Stateless 체인 구현 (US-A1, US-A3).
  * **Member B**: `VisionHazardInspector` 1차 모듈 구현 (구조화 JSON 출력 규격화) (US-D1).
  * **Member C**: OSM `highway=steps` 배제 모듈(US-B1) 및 DEM 고도 데이터 기반 구간별 `max_slope_percent` 산출 로직 개발 (US-B2).
  * **Member D**: **AsyncStorage 로컬 스토리지 매니저 개발** (반려견 프로필 등록 폼, JSON 파일 내보내기/가져오기 백업 뷰) (US-A2). 앱 UI 웰니스 용어 적용.
  * **Member E**: Supabase 커뮤니티 코스 및 위험 제보 테이블 DDL 배포, Week 2 중간 데모 진행.

---

### Week 3: 환경 연산, 비전 위험 분석 & 핸즈프리 음성 안내 엔진 개발
* **주간 목표**: SunCalc 건물 그림자 연산, 비전 위험 분석 결합, OSRM Steps 기반 `expo-speech` 음성 길 안내 엔진 개발.
* **세부 작업**:
  * **Member A**: Vision 위험 분석 결과 수신 시 우회 경로 재탐색 에이전트 워크플로우 연결 (US-D2).
  * **Member B**: 저조도/각도 왜곡 사진 예외 처리 및 판독 지연 2.5초 이내 최적화 (US-D1).
  * **Member C**: `SunCalc` 태양각 및 건물 외곽선 기반 예상 그늘 비율(`shade_ratio`) 연산 모듈 개발 (Level 1~2) (US-B3).
  * **Member D**: **시선 해방 핸즈프리 음성 길 안내 엔진 개발** (OSRM Steps 파싱, `expo-speech` TTS 연동, 30m 전 사전 음성 브리핑 송출) (US-C2), 추천 경로 Polyline 분기 렌더링 (US-C1).
  * **Member E**: Supabase Storage 버킷 구성 및 백엔드 클라우드 배포(Render/Cloud Run).

---

### Week 4: 백그라운드 GPS, EAS 배포 & 실사용 5인 CBT
* **주간 목표**: Android Foreground Service 백그라운드 트래킹 완성, EAS Build 1회 APK 패키징 및 5인 실사용자 필드 테스트 착수.
* **세부 작업**:
  * **Member A**: 로컬에 누적된 피드백 요약을 요청 페이로드로 받아 다음 라우팅 가중치를 자동 보정하는 Stateless Memory 완성 (US-E3).
  * **Member B**: 실사용자 필드 업로드 사진 실시간 모니터링 및 판독 정확도 검증.
  * **Member C**: 전국 공영주차장 API 연동(US-G1) 및 기상청 단기예보 기반 열 위험 지수 산출(US-F1).
  * **Member D**: **Android Foreground Service 기반 백그라운드 GPS 위치 추적 완성** (화면 꺼짐 지속 유지, 폰 로컬 스토리지에 궤적 적재) (US-E1), 완주 후 피드백 입력 UI (US-E2).
  * **Member E [실사용 테스트 & 배포 리드]**:
    - **EAS Build로 테스터용 Android APK 1회 패키징 및 5인 테스터 배포** (US-H1).
    - **EAS Update (`expo-updates`) 무선 OTA 파이프라인 가동**.
    - 커뮤니티 코스 공유 시 **출발지 200m 마스킹 블러링** 파이프라인 검증 (US-G2).
    - 견주 5인 대상 필드 테스트 수행 및 설문 수집 (주머니 속 음성 안내 편의성, 계단 회피 등).

---

### Week 5: 무선 OTA 핫픽스, 피드백 반영 & 최종 출시
* **주간 목표**: 5인 CBT 피드백 반영, EAS Update 무선 OTA 실시간 핫픽스 배포, 최종 안정화.
* **세부 작업**:
  * **Member A**: 실사용자 발화 로그 분석을 통한 프롬프트 보정 및 음성 브리핑 멘트 고도화.
  * **Member B**: 비전 판독 임계치 최종 캘리브레이션.
  * **Member C**: 라우팅 연산 캐싱 적용으로 평균 응답 지연 2.5초 이내 달성.
  * **Member D**: 실사용자 피드백 기반 음성 안내 타이밍 및 UI 수정 ➔ **EAS Update로 재설치 없이 실시간 핫픽스 배포**.
  * **Member E**: API 키 은닉 점검, 5인 실사용자 테스트 평가 보고서 및 최종 운영 가이드 문서 정리 (US-H1).
