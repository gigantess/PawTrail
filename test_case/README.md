# 🧪 PawTrail TDD (Test-Driven Development) 테스트 스위트

본 디렉토리(`test_case/`)는 **PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 에이전트 및 핸즈프리 모바일 플랫폼)**의 **8개 에픽(Epic A ~ H) 및 18개 핵심 애자일 사용자 스토리(US-A1 ~ US-H1)**와 시스템 아키텍처 명세를 기반으로 구축된 정밀 TDD 테스트 스위트입니다.

---

## 📂 테스트 스위트 구조 및 사용자 스토리 매핑 (18개 Story 전수 매핑)

| 테스트 파일명 | 대상 에픽 & 사용자 스토리 (Story ID) | 주요 검증 내용 (인수 조건 & DoD 연계) |
|---|:---:|---|
| [`test_walk_plan_agent_schema.py`](./test_walk_plan_agent_schema.py) | **[Epic A] US-A1, US-A2<br>[Epic E] US-E3** | • **[US-A1]**: 자연어 발화 의도 파싱(`TargetDuration`, `AvoidStairs`, `SlopePreference`, `ShadePriority`) Pydantic V2 엄격 검증 및 불명확 질의 안전 Fallback<br>• **[US-A2]**: Local-First `AsyncStorage` 프로필 영속화, JSON 내보내기/가져오기 백업/복원 무결성, 웰니스 카피라이팅 가드레일 (질병 단어 검출 0건)<br>• **[US-E3]**: 로컬 누적 피드백(경사 불만족 등) 전달 시 무상태(Stateless)로 최대 허용 경사도 1~2% 하향 보정 |
| [`test_loop_target_duration.py`](./test_loop_target_duration.py) | **[Epic A] US-A3** | • **[US-A3]**: 표준 보행 속도 모델(소형 2.8, 중형 3.6, 대형 4.2, 노령 2.2 km/h) 기반 목표 거리 환산($D = V \times T$)<br>• 10~90분 슬라이더(기본 권장 15~60분) 입력 유효성 검증<br>• 순환(Loop) 경로 목표 거리 대비 **오차 ±15% 이내 수렴 및 2개 이상 루프 후보 생성** 검증 |
| [`test_surface_cost_model.py`](./test_surface_cost_model.py) | **[Epic B] US-B1, US-B2<br>US-B3, US-B4** | • **[US-B1]**: OSM 보행망 `highway=steps` 링크 하드 회피(Hard Constraint) 및 계단 메타데이터 투명 반환<br>• **[US-B2]**: DEM 고도 기반 링크별 종단 경사도(`slope_percent`) 산출, 급경사($>8\%$) 3배 페널티, 코스 전체 최대/평균 경사도 연산<br>• **[US-B3]**: SunCalc 태양 고도각 연동 11~15시 피크 시간대 그늘길 비용 할인($W_{\text{shade}} = 0.6$) 적용<br>• **[US-B4]**: Candidate Route Scorer 다요소 종합 채점(계단 30, 경사 30, 그늘 20, 거리 20 -> 100점 만점) 및 최적 코스 선정<br>• 환경부 세분류 토지피복 공간 결합 5단계 출처 투명성 검증 |
| [`test_mobile_and_voice_navigation.py`](./test_mobile_and_voice_navigation.py) | **[Epic C] US-C1, US-C2** | • **[US-C1]**: React Native Maps Polyline 구간별 색상 분기 렌더링 (🌿 완만/그늘: 초록 `#10B981`, 🏢 일반: 파랑 `#3B82F6`, 🏃 탄성: 주황 `#F97316`, ⚠️ 주의/위험: 빨강 `#EF4444`)<br>• **[US-C2]**: 시선 해방(Eyes-Free) 백그라운드 핸즈프리 음성 내비게이션: Android Foreground Service GPS 연동, 회전 30m 전 `expo-speech` TTS 사전 브리핑, 40m 이상 이탈 감지 시 재탐색 음성 알림 |
| [`test_vision_safety_inspector.py`](./test_vision_safety_inspector.py) | **[Epic D] US-D1, US-D2** | • **[US-D1]**: Gemini 1.5 Flash Vision 기반 현장 높은 턱(25cm), 야외 계단, 공사 장애물 분석 DTO 및 공원 종합안내판 판독(`ParkBoardInspector`) 반려견 금지구역 파싱<br>• **[US-D2]**: 현장 위험 감지 시 해당 링크 비용 10배 페널티/차단 적용 및 3초 이내 대안 우회로 동적 재산출(`POST /api/v1/walk/reroute`) |
| [`test_walk_tracking_and_feedback.py`](./test_walk_tracking_and_feedback.py) | **[Epic E] US-E1, US-E2<br>[Epic H] US-H1** | • **[US-E1]**: 백그라운드 GPS 궤적 로컬 스토리지(`@PawTrail:walk_history`) 영속화, 최근 100회 산책 기록 한도(FIFO) 관리, 자택 좌표 서버 미전송 보장<br>• **[US-E2]**: 완주 인포그래픽 리포트 생성 및 3초 원터치 체감 피드백(완만함, 그늘, 발 편함) 수집 검증<br>• **[US-H1]**: EAS Update 무선 OTA 매니페스트 DTO 검증 및 5인 견주 CBT 설문 피드백 기반 가중치 튜닝 알고리즘 검증 |
| [`test_thermal_and_parking.py`](./test_thermal_and_parking.py) | **[Epic F] US-F1<br>[Epic G] US-G1** | • **[US-F1]**: 기상청 단기예보(기온, 일사량) 기반 지면열 추정 수지식 연산 및 35℃ 이하 안전 산책 골든타임 카드 도출<br>• **[US-G1]**: 현위치 반경 1.5km 이내 공영주차장(P&R) 필터링 및 주차장 출입구 시작/종료 순환 코스 스냅 DTO 검증 |
| [`test_api_contracts.py`](./test_api_contracts.py) | **[Epic G] US-G2<br>REST API Contract** | • **[US-G2]**: 코스 커뮤니티 공유 시 **출발지 및 도착지 반경 200m 공간 절단 및 지터링(Spatial Jittering)** 자택 노출 방지 알고리즘 검증<br>• FastAPI 백엔드 v1 엔드포인트 입출력 계약 DTO 전수 검증 (`POST /api/v1/walk/plan`, `POST /api/v1/community/share` 등) |

---

## 🚀 테스트 실행 방법

### 1. 가상환경 및 의존성 확인
```bash
python -m pip install pytest pydantic
```

### 2. 전체 테스트 스위트 실행 (67개 테스트 전수 100% Pass)
```bash
python -m pytest test_case/ -v
```

### 3. 에픽/도메인별 단위 테스트 실행
```bash
# [Epic A & E] AI 의도 파싱, Local-First 프로필, 무상태 피드백 보정 테스트
python -m pytest test_case/test_walk_plan_agent_schema.py -v

# [Epic A] 산책 시간 및 표준 속도 환산 테스트
python -m pytest test_case/test_loop_target_duration.py -v

# [Epic B] 무계단·완만경사·그늘 과학 라우팅 및 다요소 스코어러 테스트
python -m pytest test_case/test_surface_cost_model.py -v

# [Epic C] 모바일 Polyline 색상 분기 및 핸즈프리 음성 안내 테스트
python -m pytest test_case/test_mobile_and_voice_navigation.py -v

# [Epic D] Vision AI 현장 위험 분석 및 동적 우회 재탐색 테스트
python -m pytest test_case/test_vision_safety_inspector.py -v

# [Epic E & H] GPS 로컬 저장, 완주 피드백, EAS OTA 및 CBT 가중치 튜닝 테스트
python -m pytest test_case/test_walk_tracking_and_feedback.py -v

# [Epic F & G] 지면열 골든타임 및 공영주차장 P&R 탐색 테스트
python -m pytest test_case/test_thermal_and_parking.py -v

# [Epic G & API] 200m 공간 마스킹 및 REST API v1 계약 DTO 테스트
python -m pytest test_case/test_api_contracts.py -v
```

---

## 📋 TDD 원칙 및 테스트 동기화 규칙
1. **18개 사용자 스토리 100% 정합성**: 모든 테스트 모듈은 `03_PawTrail_Agile_User_Stories.md`의 인수 조건(Acceptance Criteria) 및 `06_PawTrail_Task_Breakdown_and_Estimations.md`의 완료 정의(DoD)를 직접 검증합니다.
2. **웰니스 카피라이팅 가드레일**: 앱 UI, DTO 및 테스트 코드 내에서 '슬개골 탈구' 등 임상 질병 단어를 배제하고 '관절 안심 케어', '폭신한 길' 등 순화된 언어를 엄격히 준수합니다.
3. **프라이버시 바이 디자인(Local-First) 검증**: 민감한 자택 위치 및 상세 보행 GPS 궤적은 서버로 전송하지 않고 로컬 스토리지에만 보관하며, 커뮤니티 공유 시 200m 공간 마스킹이 적용됨을 테스트로 보증합니다.

