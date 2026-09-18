# 🧪 PawTrail TDD (Test-Driven Development) 테스트 스위트

본 디렉토리(`test_case/`)는 **PawTrail (AI Native 반려견 맞춤형 안심 노면 산책 플랫폼)**의 16개 애자일 사용자 스토리(US-01 ~ US-16) 및 시스템 아키텍처 명세를 기반으로 작성된 TDD 테스트 모듈 세트입니다.

---

## 📂 테스트 스위트 구조 및 사용자 스토리 매핑

| 테스트 파일명 | 대상 사용자 스토리 (Story ID) | 주요 검증 내용 |
|---|:---:|---|
| [`test_surface_cost_model.py`](./test_surface_cost_model.py) | **US-02, US-03** | • 노면 비용 함수($\text{Cost} = \text{Length} \times W_{\text{base}} \times W_{\text{pref}}$)<br>• 선호 노면 할인(0.45) 및 아스팔트(2.5)/자갈(3.5) 페널티<br>• **환경부 세분류 토지피복지도(SHP) 공간 결합 및 5단계 출처 투명성(`surface_source`)** 검증<br>• 순환(Loop) 경로 시작/종료점 일치 및 선호 노면 점유율 $\ge 50\%$ |
| [`test_walk_plan_agent_schema.py`](./test_walk_plan_agent_schema.py) | **US-01, US-06** | • Pydantic V2 산책 생성 요청 엄격 검증(시간 5~120분, 좌표 유효범위)<br>• 필수 파라미터 누락 시 Clarification(되물음) 트리거<br>• 반려견 건강 프로필(관절 안심 케어 수준) 및 롱텀 메모리 주입 |
| [`test_loop_target_duration.py`](./test_loop_target_duration.py) | **US-16** | • **[US-16] 사용자 지정 산책 시간(Target Duration) 기반 맞춤 코스 생성**<br>• 15분, 30분, 45분 시간대별 및 견종 체급별 목표 거리($D = V \times T$) 산출<br>• 목표 거리 대비 **오차 ±10% 이내 2개 이상 순환 루프 코스 생성** 검증<br>• `POST /api/walks/plan` 페이로드 시간 제약(10~90분) 유효성 검증 |
| [`test_vision_safety_inspector.py`](./test_vision_safety_inspector.py) | **US-04, US-05** | • **[US-04] 공원 종합안내판 비전 판독(`ParkBoardInspectionResult`)**: 반려견 출입 금지 구역 및 흙길 범례 파싱<br>• **[US-05] 완주 후기 사진 비전 검증(`SurfaceEnrichmentResult`)**: 신뢰도 $\ge 0.85$ 시 지도 영구 보강 및 미달 시 격리<br>• 저조도/각도 왜곡 사진 재촬영 안내 플래그 |
| [`test_walk_tracking_and_feedback.py`](./test_walk_tracking_and_feedback.py) | **US-08, US-09, US-11, US-15** | • 산책 완주 후 이동 거리 대비 선호 노면 달성률(%) 계산<br>• 산책 완료 체크인 스키마 및 만족도(1~5점) 검증<br>• 5인 CBT 피드백 기반 가중치 재조정 플래그 평가<br>• 오프라인 체크인 IndexedDB 로컬 큐 동기화 |
| [`test_thermal_and_parking.py`](./test_thermal_and_parking.py) | **US-12, US-13** | • 기상청 일사량 연동 지면열 추정 수지식 연산<br>• 35℃ 이하 안전 산책 골든타임 도출<br>• 반경 1.5km 이내 공영주차장(P&R) 필터링 |
| [`test_api_contracts.py`](./test_api_contracts.py) | **REST API Contract (US-14 등)** | • FastAPI 백엔드 엔드포인트 입출력 DTO 계약 검증<br>• `POST /api/walks/inspect-board` 및 `POST /api/walks/verify-surface` DTO 검증<br>• 나만의 코스 즐겨찾기(`POST /api/walks/{id}/favorite`) DTO 검증<br>• GeoJSON FeatureCollection 규격 준수 |

---

## 🚀 테스트 실행 방법

### 1. 가상환경 및 의존성 설치
```bash
pip install pytest pydantic
```

### 2. 전체 테스트 스위트 실행 (71개 테스트 전수 검증)
```bash
pytest test_case/ -v
```

### 3. 특정 모듈 단위 테스트 실행
```bash
# 노면 비용 모델 및 환경부 토지피복 공간 결합 테스트
pytest test_case/test_surface_cost_model.py -v

# AI Agent 스키마 및 Clarification 테스트
pytest test_case/test_walk_plan_agent_schema.py -v

# 공원 안내판 판독 및 커뮤니티 사진 검증 테스트
pytest test_case/test_vision_safety_inspector.py -v

# API 계약 DTO 유효성 테스트
pytest test_case/test_api_contracts.py -v
```

---

## 📋 TDD 원칙 및 테스트 동기화 규칙 (`.gemini/GEMINI.md` 준수)
1. **Red ➔ Green ➔ Refactor**: 구현 전 테스트케이스를 먼저 확인하고, 구현 후 테스트 100% 통과를 확인합니다.
2. **요구사항 변경 시 테스트케이스 동기화**: 사용자 스토리나 Task의 인수 조건(Acceptance Criteria)이 변경된 경우 관련 테스트 파일의 기대값과 Fixture를 즉시 수정·동기화합니다.
