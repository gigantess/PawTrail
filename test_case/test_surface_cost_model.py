"""[US-02, US-03] 노면 비용 모델 및 환경부 토지피복 공간 결합 TDD 테스트 모듈.

4b06010 커밋 및 실행가능앱 아키텍처(docs/04) 기준:
- 비용 함수 공식: Cost(e) = Length(e) * W_base(surface) * W_pref(surface, SelectedPref)
- 선호 노면 선택 시 할인 계수: 0.4 ~ 0.5 (표준 0.45)
- 아스팔트 페널티: 2.5
- 자갈/파쇄석 페널티: 3.5
- 환경부 세분류 토지피복지도(Land Cover Map) 기반 공간 결합 및 5단계 노면 출처 투명성 체계:
  1. seed_verified (신뢰도 0.95): 항공/로드뷰 육안 교차 검증 1.5km 시드
  2. land_cover_map (신뢰도 0.85~0.90): 환경부 토지피복 세분류 (초지=잔디, 나지=흙길, 인공포장=보도블록/아스팔트)
  3. community_verified (신뢰도 0.80~0.90): 완주 후기 사진 비전 검증 반영 데이터
  4. park_polygon (신뢰도 0.75): 도시공원 경계 내부 흙길 기본 추정
  5. estimated (신뢰도 0.50): 일반 도로망 위계 기반 기본 Fallback
- 생성 경로 내 선호 노면 비율 >= 50% 검증 및 미달 시 투명한 사유 안내
"""

import pytest
from typing import List, Dict, Any, Optional, Tuple

# TDD 대상 비즈니스 상수 정의 (도메인 명세)
SURFACE_BASE_WEIGHTS = {
    "grass": 0.6,
    "dirt": 0.6,
    "rubber": 0.7,
    "paved": 1.0,
    "asphalt": 2.5,
    "gravel": 3.5,
}
PREF_DISCOUNT_FACTOR = 0.45  # 0.4 ~ 0.5


def resolve_surface_fallback(surface: Optional[str], highway: str, in_park: bool) -> str:
    """기본 OSM 노면 결측치 Fallback 해결 함수 (US-03 레거시 호환)."""
    if surface is not None and surface.strip() != "":
        return surface

    if in_park:
        return "dirt"
    if highway in ["footway", "pedestrian", "path"]:
        return "paved"
    if highway in ["residential", "tertiary", "secondary", "primary"]:
        return "asphalt"
    return "paved"


def resolve_surface_with_land_cover(
    osm_surface: Optional[str] = None,
    land_cover_code: Optional[str] = None,
    community_verified_surface: Optional[str] = None,
    in_park: bool = False,
    highway: str = "footway"
) -> Tuple[str, str, float]:
    """환경부 세분류 토지피복지도 결합 및 5단계 노면 출처 투명성 해소 로직 (US-03 신규 아키텍처)."""
    # 1. 시드 검증 / OSM 명확 태그 우선
    if osm_surface in ["dirt", "grass", "paved", "asphalt", "rubber", "gravel"]:
        return osm_surface, "seed_verified", 0.95

    # 2. 커뮤니티 검증 데이터 우선
    if community_verified_surface is not None:
        return community_verified_surface, "community_verified", 0.90

    # 3. 환경부 세분류 토지피복지도 결합 (초지=잔디, 나지=흙길, 인공포장=보도블록)
    if land_cover_code in ["초지", "grassland"]:
        return "grass", "land_cover_map", 0.90
    elif land_cover_code in ["나지", "bare_soil"]:
        return "dirt", "land_cover_map", 0.90
    elif land_cover_code in ["인공포장", "built_up"]:
        return "paved", "land_cover_map", 0.85

    # 4. 도시공원 폴리곤 내부 Fallback (흙길 기본 추정)
    if in_park:
        return "dirt", "park_polygon", 0.75

    # 5. 일반 도로망 Fallback
    if highway in ["residential", "tertiary", "secondary", "primary"]:
        return "asphalt", "estimated", 0.50
    return "paved", "estimated", 0.50


def calculate_link_cost(
    length_m: float,
    surface: str,
    selected_preferred_surfaces: List[str]
) -> float:
    """노면 가중치 비용 산출 함수 (US-02 명세 구현)."""
    base_weight = SURFACE_BASE_WEIGHTS.get(surface, 1.0)
    
    # 선호 노면 선택 여부에 따른 보정 계수 W_pref
    if surface in selected_preferred_surfaces:
        pref_factor = PREF_DISCOUNT_FACTOR
    elif surface == "paved":
        pref_factor = 1.0  # 중립 노면
    elif surface in ["asphalt", "gravel"]:
        pref_factor = 1.0  # 이미 base_weight에 높은 페널티가 부여됨
    else:
        pref_factor = 1.0

    return length_m * base_weight * pref_factor


class TestSurfaceCostModel:
    """노면 가중치 비용 모델 단위 테스트 (US-02)."""

    def test_preferred_surface_discount_applied(self):
        """선호 노면(흙길, 잔디길) 선택 시 비용 할인이 정상 적용되는지 검증."""
        length = 100.0
        selected = ["dirt", "grass"]

        # 잔디길: base(0.6) * discount(0.45) = 0.27
        cost_grass = calculate_link_cost(length, "grass", selected)
        assert cost_grass == pytest.approx(100.0 * 0.6 * 0.45, rel=1e-3)
        assert cost_grass == pytest.approx(27.0, rel=1e-3)

        # 흙길: base(0.6) * discount(0.45) = 0.27
        cost_dirt = calculate_link_cost(length, "dirt", selected)
        assert cost_dirt == pytest.approx(27.0, rel=1e-3)

    def test_unselected_paved_surface_is_neutral(self):
        """선택되지 않은 보도블록은 기본 가중치 1.0(중립)이 유지되어야 함."""
        length = 100.0
        selected = ["dirt"]

        cost_paved = calculate_link_cost(length, "paved", selected)
        assert cost_paved == pytest.approx(100.0 * 1.0 * 1.0, rel=1e-3)

    def test_asphalt_and_gravel_penalties(self):
        """아스팔트(2.5) 및 자갈/파쇄석(3.5) 페널티가 정상 작동하여 비용이 크게 증가해야 함."""
        length = 100.0
        selected = ["dirt", "grass"]

        cost_asphalt = calculate_link_cost(length, "asphalt", selected)
        cost_gravel = calculate_link_cost(length, "gravel", selected)

        # 잔디 비용(27.0) 대비 아스팔트는 9배 이상, 자갈은 12배 이상의 비용을 가져야 함
        assert cost_asphalt == pytest.approx(250.0, rel=1e-3)
        assert cost_gravel == pytest.approx(350.0, rel=1e-3)

    def test_surface_cost_ranking(self):
        """동일한 길이(100m)일 때 선호 노면 선택에 따른 비용 순위 검증."""
        selected = ["grass"]
        costs = {
            "grass": calculate_link_cost(100.0, "grass", selected),
            "dirt": calculate_link_cost(100.0, "dirt", selected),
            "paved": calculate_link_cost(100.0, "paved", selected),
            "asphalt": calculate_link_cost(100.0, "asphalt", selected),
            "gravel": calculate_link_cost(100.0, "gravel", selected),
        }

        # 비용 순위: 잔디(선호, 최저 비용) < 흙길 < 보도블록 < 아스팔트 < 자갈(최고 비용)
        assert costs["grass"] < costs["dirt"] < costs["paved"] < costs["asphalt"] < costs["gravel"]


class TestOsmSurfaceFallback:
    """OSM 노면 결측치 보정(Fallback) 규칙 테스트 (US-03 레거시 호환)."""

    def test_existing_surface_not_overwritten(self):
        """이미 surface 태그가 존재하는 경우 Fallback에 의해 덮어써지지 않아야 함."""
        assert resolve_surface_fallback("grass", "footway", in_park=False) == "grass"
        assert resolve_surface_fallback("asphalt", "residential", in_park=False) == "asphalt"

    def test_park_interior_missing_surface_fallback_to_dirt(self):
        """공원 폴리곤 내부의 surface 누락 링크는 흙길(dirt)로 보정되어야 함."""
        resolved = resolve_surface_fallback(None, highway="footway", in_park=True)
        assert resolved == "dirt"

    def test_footway_missing_surface_fallback_to_paved(self):
        """공원 외곽 보행로의 surface 누락 링크는 보도블록(paved)으로 보정되어야 함."""
        resolved = resolve_surface_fallback(None, highway="footway", in_park=False)
        assert resolved == "paved"

    def test_residential_road_missing_surface_fallback_to_asphalt(self):
        """일반 도로(residential)의 surface 누락 링크는 아스팔트(asphalt)로 보정되어야 함."""
        resolved = resolve_surface_fallback(None, highway="residential", in_park=False)
        assert resolved == "asphalt"


class TestLandCoverSpatialService:
    """환경부 세분류 토지피복지도 공간 결합 및 5단계 노면 출처 투명성 테스트 (US-03)."""

    def test_seed_verified_takes_highest_priority(self):
        """시드 검증 데이터셋이 존재할 때 최우선(seed_verified, 신뢰도 0.95) 반영 검증."""
        surface, source, conf = resolve_surface_with_land_cover(
            osm_surface="dirt",
            land_cover_code="초지",
            in_park=False
        )
        assert surface == "dirt"
        assert source == "seed_verified"
        assert conf == 0.95

    def test_community_verified_takes_second_priority(self):
        """시드 데이터가 없을 때 커뮤니티 비전 검증 결과가 차순위로 반영되는지 검증."""
        surface, source, conf = resolve_surface_with_land_cover(
            osm_surface=None,
            community_verified_surface="grass",
            land_cover_code="나지",
            in_park=False
        )
        assert surface == "grass"
        assert source == "community_verified"
        assert conf == 0.90

    def test_land_cover_grassland_mapped_to_grass(self):
        """환경부 피복도 '초지' 폴리곤과 결합 시 잔디길(grass, land_cover_map) 판정 검증."""
        surface, source, conf = resolve_surface_with_land_cover(
            osm_surface=None,
            land_cover_code="초지",
            in_park=False
        )
        assert surface == "grass"
        assert source == "land_cover_map"
        assert conf == 0.90

    def test_land_cover_bare_soil_mapped_to_dirt(self):
        """환경부 피복도 '나지' 폴리곤과 결합 시 흙길(dirt, land_cover_map) 판정 검증."""
        surface, source, conf = resolve_surface_with_land_cover(
            osm_surface=None,
            land_cover_code="나지",
            in_park=False
        )
        assert surface == "dirt"
        assert source == "land_cover_map"
        assert conf == 0.90

    def test_park_polygon_fallback_when_land_cover_absent(self):
        """피복도 데이터가 없는 공원 구역은 park_polygon 흙길(dirt, 0.75)로 Fallback 검증."""
        surface, source, conf = resolve_surface_with_land_cover(
            osm_surface=None,
            land_cover_code=None,
            in_park=True
        )
        assert surface == "dirt"
        assert source == "park_polygon"
        assert conf == 0.75

    def test_general_road_estimated_fallback(self):
        """모든 데이터 결측 시 일반 도로망 위계에 따라 estimated(0.50)로 안전하게 Fallback 검증."""
        surface, source, conf = resolve_surface_with_land_cover(
            osm_surface=None,
            land_cover_code=None,
            in_park=False,
            highway="residential"
        )
        assert surface == "asphalt"
        assert source == "estimated"
        assert conf == 0.50


def evaluate_preferred_surface_ratio_and_explain(
    total_dist: float,
    breakdown: Dict[str, float],
    preferred: List[str],
    target_ratio: float = 0.50
) -> Dict[str, Any]:
    """선호 노면 비율 평가 및 목표 미달 시 투명한 사유 안내 생성 (지침 4조 반영)."""
    preferred_dist = sum(breakdown.get(s, 0.0) for s in preferred)
    actual_ratio = (preferred_dist / total_dist) if total_dist > 0 else 0.0
    is_target_met = actual_ratio >= target_ratio

    explanation = None
    if not is_target_met:
        explanation = (
            f"현재 지역에서는 {', '.join(preferred)} 비율을 {int(target_ratio*100)}%까지 "
            f"확보하기 어려워 약 {int(actual_ratio*100)}%로 구성했습니다."
        )

    return {
        "actual_ratio": actual_ratio,
        "is_target_met": is_target_met,
        "explanation": explanation
    }


class TestLoopRouteRequirements:
    """순환형(Loop) 산책로 생성 및 선호 노면 점유율 테스트 (US-02, US-03)."""

    def test_loop_route_start_and_end_points_match(self, sample_geojson_route):
        """순환 경로는 첫 번째 좌표와 마지막 좌표가 일치(폐곡선)해야 함."""
        features = sample_geojson_route["features"]
        first_coord = features[0]["geometry"]["coordinates"][0]
        last_coord = features[-1]["geometry"]["coordinates"][-1]

        assert first_coord == pytest.approx(last_coord, abs=1e-5), "시작점과 종료점이 일치해야 합니다."

    def test_preferred_surface_ratio_when_rich_environment(self, sample_geojson_route):
        """선호 노면이 충분한 공원 환경에서 목표 비율(50%) 이상 달성 검증."""
        props = sample_geojson_route["properties"]
        result = evaluate_preferred_surface_ratio_and_explain(
            total_dist=props["total_distance_m"],
            breakdown=props["surface_breakdown"],
            preferred=props["preferred_surfaces"],
            target_ratio=0.50
        )
        assert result["is_target_met"] is True
        assert result["actual_ratio"] >= 0.50
        assert result["explanation"] is None

    def test_insufficient_surface_environment_provides_explanation_without_error(self):
        """도심지 등 선호 노면이 50% 미만(예: 35%)인 경우에도 크래시 없이 사유를 투명하게 안내해야 함 (지침 4조 준수)."""
        urban_breakdown = {
            "grass": 100.0,
            "dirt": 250.0,    # 선호 노면 합계 350m / 1000m = 35%
            "paved": 450.0,
            "asphalt": 200.0
        }
        result = evaluate_preferred_surface_ratio_and_explain(
            total_dist=1000.0,
            breakdown=urban_breakdown,
            preferred=["grass", "dirt"],
            target_ratio=0.50
        )
        assert result["is_target_met"] is False
        assert result["actual_ratio"] == pytest.approx(0.35, rel=1e-2)
        assert result["explanation"] is not None
        assert "50%까지 확보하기 어려워 약 35%로 구성" in result["explanation"]
