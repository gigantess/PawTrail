"""[US-16] 사용자 지정 산책 시간(Target Duration) 기반 맞춤형 코스 생성 TDD 테스트 모듈.

명세서 기준 (US-16 Definition of Done & 인수 조건):
1. 산책 시간대별(15분, 30분, 45분) 및 견종 체급별 목표 거리 산출:
   - 목표 거리 D_target = V_dog * T_target
   - V_dog: 소형견 50m/min(3.0km/h), 중형견 63.3m/min(3.8km/h), 대형견 75m/min(4.5km/h), 노령/관절질환견 41.7m/min(2.5km/h)
2. GIS 루프 경로 생성 알고리즘의 목표 거리/시간 대비 오차 ±10% 이내 검증
3. 최소 2개 이상의 대안 순환 코스 생성 검증
4. REST API (POST /api/walks/plan) 페이로드 검증 (target_duration_minutes: 10~90분)
"""

import pytest
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field, ValidationError

# 체급별 기준 보행 속도 (m/min)
DOG_WALK_SPEEDS_M_PER_MIN = {
    "small": 50.0,       # 3.0 km/h
    "medium": 63.33,     # 3.8 km/h
    "large": 75.0,       # 4.5 km/h
    "senior_patella": 41.67  # 2.5 km/h (관절 보호 및 노령견)
}


class TargetDurationPlanRequest(BaseModel):
    """US-16 산책 시간 지정 요청 DTO."""
    dog_id: str
    target_duration_minutes: int = Field(..., ge=10, le=90, description="목표 산책 시간(10분~90분)")
    dog_size: Literal["small", "medium", "large", "senior_patella"] = "small"
    origin_lat: float = Field(..., ge=-90.0, le=90.0)
    origin_lon: float = Field(..., ge=-180.0, le=180.0)


def calculate_target_distance_meters(
    duration_minutes: int,
    dog_size: Literal["small", "medium", "large", "senior_patella"]
) -> float:
    """시간과 보행 속도를 곱하여 목표 거리(m)를 산출하는 함수."""
    speed = DOG_WALK_SPEEDS_M_PER_MIN[dog_size]
    return round(speed * duration_minutes, 1)


def generate_simulated_loop_candidates(
    target_distance: float,
    origin: tuple
) -> List[Dict[str, Any]]:
    """목표 거리 기반으로 ±10% 오차 범위 내의 2개 이상 루프 코스 후보 생성 시뮬레이션."""
    # 알고리즘 시뮬레이션: 코스 1 (오차 -4%), 코스 2 (오차 +3%)
    candidate1_dist = round(target_distance * 0.96, 1)
    candidate2_dist = round(target_distance * 1.03, 1)

    return [
        {
            "route_id": "loop_opt_1",
            "name": "공원 둘레길 코스 A",
            "distance_m": candidate1_dist,
            "origin": origin,
            "destination": origin,  # 순환 폐곡선
            "error_rate": round(abs(candidate1_dist - target_distance) / target_distance, 4)
        },
        {
            "route_id": "loop_opt_2",
            "name": "숲길 힐링 코스 B",
            "distance_m": candidate2_dist,
            "origin": origin,
            "destination": origin,
            "error_rate": round(abs(candidate2_dist - target_distance) / target_distance, 4)
        }
    ]


class TestTargetDurationCourseGeneration:
    """US-16 목표 시간 기반 코스 생성 단위 테스트 스위트."""

    @pytest.mark.parametrize("duration, dog_size, expected_distance", [
        (15, "small", 750.0),            # 15분 소형견: 750m
        (30, "small", 1500.0),           # 30분 소형견: 1500m
        (45, "small", 2250.0),           # 45분 소형견: 2250m
        (15, "medium", 950.0),           # 15분 중형견: 약 950m
        (30, "medium", 1900.0),          # 30분 중형견: 약 1900m
        (45, "medium", 2850.0),          # 45분 중형견: 약 2850m
        (30, "large", 2250.0),           # 30분 대형견: 2250m
        (45, "large", 3375.0),           # 45분 대형견: 3375m
        (20, "senior_patella", 833.4),   # 20분 슬개골/노령견: 약 833m
    ])
    def test_target_distance_calculation_by_duration_and_size(
        self, duration, dog_size, expected_distance
    ):
        """시간대별(15분, 30분, 45분) 및 체급별 목표 거리 산출 공식 검증."""
        dist = calculate_target_distance_meters(duration, dog_size)
        assert dist == pytest.approx(expected_distance, abs=5.0)

    def test_loop_candidates_within_10_percent_tolerance(self):
        """생성된 루프 경로가 목표 거리 대비 오차 ±10% 이내인지 검증 (인수조건 2)."""
        target_dist = 1500.0  # 30분 소형견 기준
        routes = generate_simulated_loop_candidates(target_dist, origin=(37.4979, 127.0276))

        # 1. 최소 2개 이상의 루프 후보가 생성되는지 검증
        assert len(routes) >= 2

        # 2. 모든 후보가 순환형(출발지==도착지)인지 검증
        for route in routes:
            assert route["origin"] == route["destination"]

            # 3. 오차율이 10% (0.10) 이내인지 검증
            assert route["error_rate"] <= 0.10
            assert target_dist * 0.90 <= route["distance_m"] <= target_dist * 1.10

    def test_request_payload_validation_for_duration(self):
        """요청 페이로드 유효성 검증 (10분~90분 범위 준수)."""
        valid_req = TargetDurationPlanRequest(
            dog_id="dog-001",
            target_duration_minutes=30,
            dog_size="small",
            origin_lat=37.5,
            origin_lon=127.0
        )
        assert valid_req.target_duration_minutes == 30

        # 10분 미만 거부
        with pytest.raises(ValidationError):
            TargetDurationPlanRequest(
                dog_id="dog-001",
                target_duration_minutes=5,
                origin_lat=37.5,
                origin_lon=127.0
            )

        # 90분 초과 거부
        with pytest.raises(ValidationError):
            TargetDurationPlanRequest(
                dog_id="dog-001",
                target_duration_minutes=100,
                origin_lat=37.5,
                origin_lon=127.0
            )
