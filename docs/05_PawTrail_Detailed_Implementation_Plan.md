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
  * **Member A (팀장 / PM & AI Agent Lead / 65h)**:
    - LangGraph 기반 Walk Planning Agent 설계 및 무상태(Stateless) 프롬프트 오케스트레이션 (US-A1, US-E3).
    - Pydantic V2 Strict Tool-calling 규격 수립, 체급별 표준 보행 속도 모델 및 목표 시간 수렴도(±15%) 튜닝 (US-A3).
    - Candidate Route Scorer 다요소 랭킹 수치 알고리즘 구현 및 추천 사유/우회 안내 음성 브리핑 체인 연동 (US-B4, US-D2).
  * **Member B (AI & Spatial Data Engineer / 71h)**:
    - Gemini 가용 모델 순차 선택(Gemini 3.5 Flash-Lite ➔ Gemini 3.1 Flash-Lite ➔ Gemini 3.6 Flash) 기반 현장 위험물(높은 턱, 계단, 공사) 판독 및 공원 종합안내판 비전 판독 파이프라인 개발 (US-D1, US-D2).
    - DEM 고도 래스터 적재 및 경로 세그먼트 고도 샘플링 파이프라인 구축 (US-B2).
    - `SunCalc` 실시간 태양 고도각/방위각 연산 모듈 및 계단/경사/그늘 테스트베드 정량 검증 (US-B1, US-B2, US-B3).
    - 기상청 단기예보 n8n 연동 및 지면열 위험 지수 산출 수지식 모듈 구현 (US-F1).
    - 전국 공영주차장 API 클라이언트(US-G1) 및 커뮤니티 출발지 200m 공간 블러링(Spatial Jittering) 파이프라인 (US-G2).
  * **Member C (Backend & Spatial Routing Lead / 91h)**:
    - FastAPI 백엔드 코어 구축, OSM 계단 배제(`highway=steps`) 하드 제약 라우팅 모듈 및 고립 지형 Fallback 로직 개발 (US-B1).
    - 세그먼트별 경사도 연산 및 경사도 페널티 비용 함수 구현 (US-B2).
    - 건물 외곽선 폴리곤 기반 시간대별 그림자 투영 및 shade_ratio 공간 교차 연산 모듈 (US-B3).
    - 전문 Routing API(OpenRouteService/OSRM) 독립 어댑터 레이어 및 순환 루프 후보(2~3개) 생성 모듈 (US-B4).
    - 위험 감지 좌표 임시 차단(Block List) 및 실시간 안전 우회 경로 재탐색 API 구현 (US-D2).
    - Supabase Auth 간편 이메일 가입/로그인 및 커뮤니티 공개 코스 CRUD REST API 구현 (US-G2).
  * **Member D (Frontend & Mobile App Lead / 94h)**:
    - React Native Expo (SDK 51+) 클라이언트 코어 아키텍처 및 react-native-maps 색상 분기 Polyline 렌더링 (US-C1).
    - **Android Foreground Service 기반 백그라운드 GPS 위치 추적 및 expo-speech TTS 음성 안내 엔진** (US-C2, US-E1).
    - **Local-First AsyncStorage 로컬 스토리지 매니저** (반려견 프로필, 개인 보행 궤적, JSON 백업/복원) (US-A2, US-E1).
    - 도심 빌딩 숲 GPS 튀김 완화 칼만 필터 및 도로망 궤적 스냅 보정 (US-E1).
    - **EAS Build 기반 테스터용 APK 1회 패키징 및 EAS Update (`expo-updates`) 무선 무점검 OTA 배포 파이프라인** (US-H1).
  * **Member E (UI/UX Designer & Product Experience Lead / 51h)**:
    - **전문 디자이너: PawTrail 디자인 시스템 구축 (Color Tokens, Typography, Iconography, Thumb Zone UI)**.
    - **6대 핵심 시나리오 고화질 UI 화면 설계 (산책 플래너, 경로 프리뷰, 다크 포켓 모드, 비전 검사, 완주 리포트, 커뮤니티 피드)**.
    - 반려견 프로필 온보딩 폼 및 플래너 시간 슬라이더/노면 칩 인터랙션 UI/UX 설계 (US-A2, US-A3).
    - 코스 요약 바텀시트, 턴 스텝 안내 뷰, 완주 인포그래픽 카드 & 보행 체감 피드백 UI 디자인 (US-C1, US-E2).
    - **앱 전역 긍정적 웰니스 카피라이팅 가이드라인 수립 (임상 질병 용어 100% 배제)**.
    - **실사용자 5인 대상 필드 CBT 사용성 평가(Usability Testing), UI/UX 휴리스틱 평가 및 최종 디자인 튜닝 총괄** (US-H1).

---

## 2. 스프린트 일정 개요 (5주 로드맵)

```text
[Week 1] 코어 인프라 & Expo 환경 셋업 (Expo SDK 51+, 디자인 시스템, Routing API 어댑터, Agent 상태머신)
   │
[Week 2] 로컬 스토리지 구축, 도메인 분석 & UI 프로토타입 (AsyncStorage, OSM 계단 배제, DEM 경사도, 고화질 목업)
   │
[Week 3] 환경 연산, 비전 위험 & 핸즈프리 음성 안내 (SunCalc 그늘, Gemini Vision, expo-speech TTS, 코스 시각화)
   │
[Week 4] 백그라운드 트래킹, EAS 배포 & 5인 CBT 착수 (Foreground Service GPS, EAS Build APK, 완주 리포트, 사용성 평가)
   │
[Week 5] 무선 OTA 핫픽스, 피드백 반영 & 최종 출시 (EAS Update 실시간 배포, 디자인 시스템 튜닝, 최종 출시)
```
```text
[Sprint 1 (Week 1~2)] 코어 AI 파이프라인, 라우팅 엔진 & UI 디자인 시스템 (33 pt)
       │
[Sprint 2 (Week 3~4)] 모바일 통합, 음성안내, 커뮤니티, EAS 배포 및 5인 CBT (36 pt)
       │
[Hardening & Launch (Week 5)] 피드백 반영 고도화, 사용성 개선, 문서화 및 최종 데모 (8 pt)
```
* **총 Story Points**: **77 pt** (기능 스프린트 77 pt / 배포 포함 총 82 pt 전수 정합)
* **총 개발 공수**: **372 Hours** (18개 핵심 스토리, 68개 세부 Task)
  $$\text{Member A}(65\text{h}) + \text{Member B}(71\text{h}) + \text{Member C}(91\text{h}) + \text{Member D}(94\text{h}) + \text{Member E}(51\text{h}) = \mathbf{372\text{ Hours}}$$

---

## 3. 주차별 세부 구현 작업 (Week 1 ~ Week 5)

### Week 1: 코어 인프라 셋업, Expo 보일러플레이트, 디자인 시스템 & 기본 라우팅
* **주간 목표**: 개발 환경 통일, Expo 프로젝트 초기화, 디자인 시스템 구축, 기본 라우팅 어댑터 연결, Git 협업 룰 확립.
* **세부 작업**:
  * **Member A**: LangGraph 상태 그래프 스키마(`AgentState`) 정의, 자연어 발화 엔티티 추출 ReAct 프롬프트 초안 작성 및 Pydantic V2 스키마 정의 (US-A1).
  * **Member B**: 현장 위험물(턱, 계단, 공사) 벤치마킹 이미지 20장 및 공원 종합안내판 이미지 15장 수집/라벨링, Gemini Flash Few-shot 프롬프트 셋업 (US-D1).
  * **Member C**: FastAPI 보일러플레이트 구성, OpenRouteService / OSRM 라우팅 어댑터 독립 레이어 구현 및 순환 루프 기본 후보 생성 (US-B4).
  * **Member D**: React Native Expo SDK 51+ 프로젝트 초기화, `@react-native-async-storage` 로컬 스토리지 래퍼 모듈 개발 (US-A2).
  * **Member E**: PawTrail 디자인 시스템 기초 설계 (Color Tokens, Typography, Iconography), 6대 화면 와이어프레임 설계 및 긍정적 웰니스 카피라이팅 가이드라인 수립 (US-A2).

---

### Week 2: 로컬 스토리지 구축, 도메인 분석 & UI 프로토타입
* **주간 목표**: AsyncStorage 로컬 스토리지 완성, OSM 계단 배제, DEM 경사도 연산 모듈 완성, 고화질 UI 화면 목업 제작.
* **세부 작업**:
  * **Member A**: 체급별 보행 속도 모델/목표거리 환산 모듈 연동(US-A3), Candidate Route Scorer 다요소 랭킹 알고리즘 연동(US-B4).
  * **Member B**: DEM 래스터 데이터 적재 & 고도 샘플링 파이프라인(US-B2), SunCalc 실시간 태양 고도/방위각 연산 모듈(US-B3), 계단 회피 정량 검증(US-B1).
  * **Member C**: OSM `highway=steps` 배제 모듈 및 최소 계단 Fallback 로직 개발(US-B1), 세그먼트별 max_slope 및 경사도 비용 함수 구현(US-B2).
  * **Member D**: 프로필 JSON 파일 내보내기/가져오기 백업 뷰 구현(US-A2), 플래너 슬라이더 UI 연동(US-A3), Polyline 분기 렌더링 캔버스 준비.
  * **Member E**: 산책 플래너 슬라이더/칩 인터랙션 UI 디자인(US-A3), 반려견 프로필 온보딩 폼 고화질 UI 목업 완성(US-A2).

---

### Week 3: 환경 연산, 비전 위험 분석 & 핸즈프리 음성 안내 엔진 개발
* **주간 목표**: SunCalc 건물 그림자 연산, 비전 위험 분석 결합, OSRM Steps 기반 `expo-speech` 음성 길 안내 엔진 개발.
* **세부 작업**:
  * **Member A**: Vision 위험 분석 결과 수신 시 우회 사유 및 변경 경로 에이전트 음성 브리핑 메시지 생성 체인 연동 (US-D2).
  * **Member B**: 저조도/각도 왜곡 사진 예외 처리 및 판독 지연 2.5초 이내 최적화 (US-D1), Vision 신뢰도 임계치 판정 핸들러(US-D2), 정오 vs 오후 그늘 대조 검증(US-B3).
  * **Member C**: 건물 외곽선 폴리곤 기반 그림자 투영 및 shade_ratio 공간 연산 모듈 개발(US-B3), 위험 감지 좌표 임시 차단 및 우회 경로 재탐색 API 구현(US-D2).
  * **Member D**: **시선 해방 핸즈프리 음성 길 안내 엔진 개발** (OSRM Steps 파싱, `expo-speech` TTS 연동, 30m 전 사전 음성 브리핑 송출) (US-C2), react-native-maps 지도 마운트 및 Polyline 색상 분기 렌더링 (US-C1).
  * **Member E**: 코스 요약 카드 및 바텀시트, 턴 스텝 안내 뷰 UI/UX 디자인 시스템 설계(US-C1), 모바일 Thumb Zone 인체공학적 레이아웃 최적화.

---

### Week 4: 백그라운드 GPS, EAS 배포 & 실사용 5인 CBT 착수
* **주간 목표**: Android Foreground Service 백그라운드 트래킹 완성, EAS Build 1회 APK 패키징 및 5인 실사용자 필드 테스트 착수.
* **세부 작업**:
  * **Member A**: 로컬에 누적된 피드백 요약을 요청 페이로드로 받아 다음 라우팅 가중치를 자동 보정하는 Stateless Memory 완성 (US-E3).
  * **Member B**: 기상청 단기예보 API/n8n 파이프라인 및 지면열 수지식 모듈 구현(US-F1), 전국 공영주차장 API 클라이언트(US-G1), 커뮤니티 200m 공간 블러링 파이프라인(US-G2).
  * **Member C**: 열 위험 지수 캐싱 및 REST API(US-F1), 주차장 출입구 연계 순환 엔드포인트(US-G1), Supabase Auth 간편 이메일 가입 및 커뮤니티 코스 CRUD API(US-G2).
  * **Member D**: **Android Foreground Service 기반 백그라운드 GPS 위치 추적 완성** (화면 꺼짐 지속 유지, 폰 로컬 스토리지에 궤적 적재) (US-E1), **EAS Build 테스터 APK 1회 패키징 및 EAS Update 무선 OTA 배포 파이프라인 수립** (US-H1).
  * **Member E**: 산책 완주 인포그래픽 요약 카드 & 보행 체감 피드백 UI 디자인(US-E2), 지면열 경고 배너(US-F1), 주차장 바텀시트(US-G1), 커뮤니티 피드 UI 디자인(US-G2), **실사용자 5인 대상 CBT 사용성 평가 계획 수립 및 진행 총괄** (US-H1).

---

### Week 5: 무선 OTA 핫픽스, 피드백 반영 & 최종 출시
* **주간 목표**: 5인 CBT 피드백 반영, EAS Update 무선 OTA 실시간 핫픽스 배포, 최종 디자인 튜닝 및 프로젝트 완성.
* **세부 작업**:
  * **Member A**: 실사용자 발화 로그 분석을 통한 에이전트 프롬프트 보정 및 음성 브리핑 멘트 고도화.
  * **Member B**: 비전 판독 임계치 최종 캘리브레이션 및 기상청 예보 파이프라인 안정화.
  * **Member C**: 라우팅 연산 인메모리 캐싱 적용으로 평균 응답 지연 2초 이내 달성 및 백엔드 안정화.
  * **Member D**: 실사용자 피드백 기반 모바일 핸즈프리 음성 안내 타이밍 캘리브레이션 ➔ **EAS Update로 재설치 없이 무선 실시간 핫픽스 배포** (US-H1).
  * **Member E**: 실사용자 5인 CBT 사용성 평가 보고서 및 UI/UX 휴리스틱 분석서 작성, 최종 디자인 시스템 튜닝 완료 (US-H1).
