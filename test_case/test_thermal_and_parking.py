"""[US-12, US-13] n8n 지면열 수지식 연산 및 공영주차장 P&R 코스 연계 TDD 테스트 모듈.

명세서 기준:
- 지면열 추정 수지식:
  Estimated Surface Temp = Air Temp + (Insolation Weight * 15)
  - Insolation Weight (일사량 가중치):
    - 맑음(Clear): 1.0
    - 구름많음(Partly Cloudy): 0.6
    - 흐림(Overcast): 0.2
- 안전 산책 골든타임 기준: 지면열 <= 35℃
- 공영주차장(P&R) 필터링 (반경 1.5km 이내 주차장 검색)
"""

import pytest
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

INSOLATION_WEIGHTS = {
    "clear": 1.0,
    "partly_cloudy": 0.6,
    "overcast": 0.2,
    "rainy": 0.0,
}


def calculate_estimated_surface_temperature(
    air_temp_celsius: float,
    sky_condition: str
) -> float:
    """기상청 단기예보 기반 지면열 추정 수지식 연산 (US-12)."""
    weight = INSOLATION_WEIGHTS.get(sky_condition.lower(), 0.5)
    return round(air_temp_celsius + (weight * 15.0), 1)


def is_safe_walk_temperature(surface_temp_celsius: float) -> bool:
    """35℃ 이하 안전 산책 가능 여부 판별."""
    return surface_temp_celsius <= 35.0


def filter_nearby_parking_lots(
    parking_lots: List[Dict[str, Any]],
    max_distance_m: float = 1500.0
) -> List[Dict[str, Any]]:
    """출발지 기준 반경 1.5km 이내 주차장 필터링 (US-13)."""
    return [p for p in parking_lots if p.get("distance_m", 9999.0) <= max_distance_m]


class TestSurfaceThermalEstimation:
    """기상 데이터 연동 지면열 추정 및 골든타임 테스트 (US-12)."""

    def test_clear_sky_noon_heat_exceeds_safe_threshold(self):
        """한여름 낮 기온 30℃, 맑음(1.0)일 때 지면열 45℃로 안전 기준(35℃)을 초과해야 함."""
        temp = calculate_estimated_surface_temperature(air_temp_celsius=30.0, sky_condition="clear")
        assert temp == 45.0
        assert is_safe_walk_temperature(temp) is False

    def test_overcast_day_within_safe_threshold(self):
        """기온 28℃, 흐림(0.2)일 때 지면열 31.0℃로 안전 산책 가능 판정 검증."""
        temp = calculate_estimated_surface_temperature(air_temp_celsius=28.0, sky_condition="overcast")
        assert temp == 31.0  # 28.0 + (0.2 * 15) = 31.0
        assert is_safe_walk_temperature(temp) is True

    def test_evening_cool_down_becomes_golden_time(self):
        """저녁 시간대 기온 24℃, 맑음(1.0)일 때 지면열 39℃ -> 일몰 후(가중치 0.0) 24℃로 골든타임 진입 검증."""
        day_temp = calculate_estimated_surface_temperature(24.0, "clear")
        night_temp = calculate_estimated_surface_temperature(24.0, "rainy")  # 일사량 0

        assert day_temp == 39.0
        assert night_temp == 24.0
        assert is_safe_walk_temperature(night_temp) is True


class TestParkingLotPnRSearch:
    """공영주차장 P&R(Park & Walk) 코스 탐색 테스트 (US-13)."""

    def test_filter_parking_lots_within_1500m(self):
        """1.5km 이내 주차장만 필터링되고 원거리 주차장은 제외되는지 검증."""
        mock_lots = [
            {"id": "pkg-01", "name": "한강시민공원 제1주차장", "distance_m": 450.0, "fee_type": "paid"},
            {"id": "pkg-02", "name": "올림픽공원 북2문 주차장", "distance_m": 1200.0, "fee_type": "free"},
            {"id": "pkg-03", "name": "성수동 공영주차장", "distance_m": 2500.0, "fee_type": "paid"},  # 제외 대상
        ]

        filtered = filter_nearby_parking_lots(mock_lots, max_distance_m=1500.0)
        assert len(filtered) == 2
        assert any(p["id"] == "pkg-01" for p in filtered)
        assert any(p["id"] == "pkg-02" for p in filtered)
        assert not any(p["id"] == "pkg-03" for p in filtered)
