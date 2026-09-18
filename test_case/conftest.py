"""PawTrail TDD 공통 Fixture 및 Mock 데이터 정의 모듈.

애자일 사용자 스토리(US-01 ~ US-13) 및 시스템 아키텍처에 정의된
핵심 데이터 모델과 테스트 환경을 구성합니다.
"""

import pytest
from typing import Dict, Any, List


@pytest.fixture
def sample_dog_profiles() -> Dict[str, Dict[str, Any]]:
    """5인 CBT 시나리오 테스터용 반려견 프로필 Fixture."""
    return {
        "tester1_maltese": {
            "dog_id": "dog-maltese-001",
            "name": "코코",
            "breed": "말티즈",
            "age": 4,
            "weight_kg": 3.2,
            "joint_care_level": 2,  # 관절 안심 케어 집중 (안심 보행 2단계)
            "patella_luxation_stage": 2,
            "default_preferred_surfaces": ["dirt", "grass"],
        },
        "tester2_retriever": {
            "dog_id": "dog-retriever-002",
            "name": "보리",
            "breed": "골든 리트리버",
            "age": 3,
            "weight_kg": 29.5,
            "joint_care_level": 0,
            "patella_luxation_stage": 0,
            "default_preferred_surfaces": ["grass", "rubber", "paved"],
        },
        "tester3_senior_poodle": {
            "dog_id": "dog-poodle-003",
            "name": "초코",
            "breed": "토이 푸들",
            "age": 11,
            "weight_kg": 4.1,
            "joint_care_level": 3,  # 노령견 관절 집중 안심 케어
            "patella_luxation_stage": 3,
            "default_preferred_surfaces": ["rubber", "dirt"],
        },
    }


@pytest.fixture
def mock_osm_network_links() -> List[Dict[str, Any]]:
    """가상의 OSM 보행 네트워크 링크 세트 Fixture."""
    return [
        {"id": "link-01", "length_m": 120.0, "surface": "grass", "highway": "footway", "in_park": True},
        {"id": "link-02", "length_m": 150.0, "surface": "dirt", "highway": "path", "in_park": True},
        {"id": "link-03", "length_m": 80.0, "surface": "rubber", "highway": "footway", "in_park": False},
        {"id": "link-04", "length_m": 200.0, "surface": "paved", "highway": "pedestrian", "in_park": False},
        {"id": "link-05", "length_m": 300.0, "surface": "asphalt", "highway": "residential", "in_park": False},
        {"id": "link-06", "length_m": 50.0, "surface": "gravel", "highway": "track", "in_park": False},
        # 태그 누락 (결측치) 링크
        {"id": "link-missing-footway", "length_m": 100.0, "surface": None, "highway": "footway", "in_park": False},
        {"id": "link-missing-park", "length_m": 150.0, "surface": None, "highway": "footway", "in_park": True},
        {"id": "link-missing-road", "length_m": 250.0, "surface": None, "highway": "residential", "in_park": False},
    ]


@pytest.fixture
def sample_geojson_route() -> Dict[str, Any]:
    """경로 렌더링 및 통계 계산을 위한 표준 GeoJSON FeatureCollection Fixture."""
    return {
        "type": "FeatureCollection",
        "properties": {
            "total_distance_m": 1200.0,
            "estimated_duration_minutes": 20,
            "preferred_surfaces": ["dirt", "grass"],
            "surface_breakdown": {
                "grass": 450.0,   # 37.5%
                "dirt": 350.0,    # 29.2% -> 선호 노면 합계 66.7%
                "paved": 250.0,   # 20.8%
                "asphalt": 150.0  # 12.5%
            }
        },
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [127.0276, 37.4979],
                        [127.0285, 37.4985],
                    ]
                },
                "properties": {
                    "surface_type": "grass",
                    "length_m": 450.0,
                    "safety_score": 95
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [127.0285, 37.4985],
                        [127.0298, 37.4992],
                    ]
                },
                "properties": {
                    "surface_type": "dirt",
                    "length_m": 350.0,
                    "safety_score": 90
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [127.0298, 37.4992],
                        [127.0276, 37.4979],
                    ]
                },
                "properties": {
                    "surface_type": "paved",
                    "length_m": 400.0,
                    "safety_score": 80
                }
            }
        ]
    }
