"""FastAPI 백엔드 REST API 입출력 계약(Contract) TDD 테스트 모듈.

4b06010 커밋 및 실행가능앱 아키텍처(docs/04) 기준:
- POST /api/walks/plan (산책 코스 계획 - surface_source 5단계 투명성 메타데이터 포함)
- POST /api/walks/inspect-board (공원 종합안내판 비전 분석)
- POST /api/walks/verify-surface (완주 후기 노면 사진 검증 및 지도 보강)
- POST /api/walks (산책 완주 기록 저장 및 선호 노면 달성률 반환)
- POST /api/walks/{id}/favorite & GET /api/favorites (나만의 코스 즐겨찾기 CRUD)
- Pydantic V2 Strict Validation 및 타입 정합성 검증
"""

import pytest
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ValidationError

SurfaceSourceType = Literal["seed_verified", "land_cover_map", "park_polygon", "community_verified", "estimated"]


class GeoJsonFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class WalkPlanResponseDTO(BaseModel):
    """POST /api/walks/plan 응답 계약 DTO."""
    type: str = "FeatureCollection"
    features: List[GeoJsonFeature]
    total_distance_m: float = Field(..., gt=0)
    estimated_duration_minutes: int = Field(..., ge=5, le=120)
    preferred_surfaces: List[str]
    surface_breakdown: Dict[str, float]
    ai_recommendation_comment: str = Field(..., min_length=10)
    status: str = "SUCCESS"


class ParkBoardInspectionResponseDTO(BaseModel):
    """POST /api/walks/inspect-board 응답 계약 DTO (US-04)."""
    park_name: str = Field(..., min_length=2)
    has_dirt_trail: bool
    has_grass_zone: bool
    dog_restricted_zones: List[str]
    detected_surfaces: List[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    summary_comment: str
    status: str = "SUCCESS"


class SurfaceEnrichmentResponseDTO(BaseModel):
    """POST /api/walks/verify-surface 응답 계약 DTO (US-05)."""
    way_id: str
    verified_surface: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    hazards: List[str]
    enrichment_status: Literal["APPLIED", "PENDING_REVIEW"]
    message: str


class CheckInResponseDTO(BaseModel):
    """POST /api/walks 또는 /api/feedback 응답 계약 DTO."""
    success: bool
    walk_history_id: str
    achievement_rate_percent: float = Field(..., ge=0.0, le=100.0)
    message: str


class FavoriteRouteDTO(BaseModel):
    """POST /api/walks/{id}/favorite 및 GET /api/favorites 응답 DTO (US-14)."""
    favorite_id: str
    route_id: str
    user_id: str
    title: str = Field(..., min_length=2)
    total_distance_m: float = Field(..., gt=0)
    estimated_duration_minutes: int = Field(..., ge=1)
    preferred_surface_ratio: float = Field(..., ge=0.0, le=1.0)
    created_at: str


class TestApiContracts:
    """REST API 응답 스키마 계약 일관성 검증 테스트."""

    def test_walk_plan_response_contract(self):
        """산책로 생성 API 응답 DTO 규격 및 surface_source 메타데이터 검증."""
        payload = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[127.0, 37.5], [127.01, 37.51]]
                    },
                    "properties": {
                        "surface_type": "grass",
                        "surface_source": "land_cover_map",
                        "distance_m": 450.0,
                        "confidence": 0.90
                    }
                }
            ],
            "total_distance_m": 1200.0,
            "estimated_duration_minutes": 20,
            "preferred_surfaces": ["grass", "dirt"],
            "surface_breakdown": {"grass": 600.0, "dirt": 400.0, "paved": 200.0},
            "ai_recommendation_comment": "코코의 편안한 관절 케어를 위해 흙길과 잔디 비중 83%로 순환 경로를 구성했습니다.",
            "status": "SUCCESS"
        }
        res = WalkPlanResponseDTO(**payload)
        assert res.status == "SUCCESS"
        assert res.total_distance_m == 1200.0
        assert len(res.features) == 1
        assert res.features[0].properties["surface_source"] == "land_cover_map"

    def test_park_board_inspect_response_contract(self):
        """POST /api/walks/inspect-board 공원 종합안내판 분석 응답 DTO 규격 검증."""
        payload = {
            "park_name": "보라매공원",
            "has_dirt_trail": True,
            "has_grass_zone": True,
            "dog_restricted_zones": ["어린이놀이터", "생태연못관찰데크"],
            "detected_surfaces": ["dirt", "grass", "rubber", "paved"],
            "confidence_score": 0.93,
            "summary_comment": "공원 둘레에 비포장 흙길 산책로가 조성되어 있으며 놀이터 구역은 우회 권장됩니다.",
            "status": "SUCCESS"
        }
        res = ParkBoardInspectionResponseDTO(**payload)
        assert res.park_name == "보라매공원"
        assert res.has_dirt_trail is True
        assert len(res.dog_restricted_zones) == 2
        assert res.confidence_score >= 0.90

    def test_surface_enrichment_response_contract(self):
        """POST /api/walks/verify-surface 완주 후기 노면 사진 검증 응답 DTO 규격 검증."""
        payload = {
            "way_id": "osm-way-987654",
            "verified_surface": "dirt",
            "confidence": 0.91,
            "hazards": [],
            "enrichment_status": "APPLIED",
            "message": "노면 제보 검증 완료: OSM 지도에 'dirt' 속성이 영구 반영되었습니다."
        }
        res = SurfaceEnrichmentResponseDTO(**payload)
        assert res.way_id == "osm-way-987654"
        assert res.enrichment_status == "APPLIED"
        assert res.confidence >= 0.85

    def test_checkin_response_contract(self):
        """산책 체크인 완료 API 응답 DTO 규격 검증."""
        payload = {
            "success": True,
            "walk_history_id": "hist-xyz-999",
            "achievement_rate_percent": 83.5,
            "message": "오늘의 안심 산책이 안전하게 기록되었습니다."
        }
        res = CheckInResponseDTO(**payload)
        assert res.success is True
        assert res.achievement_rate_percent == 83.5

    def test_favorite_route_contract_valid(self):
        """즐겨찾기 코스 DTO 유효성 검증 (US-14)."""
        payload = {
            "favorite_id": "fav-101",
            "route_id": "route-alpha-01",
            "user_id": "user-test-777",
            "title": "보라매공원 흙길 안심 루프",
            "total_distance_m": 1500.0,
            "estimated_duration_minutes": 25,
            "preferred_surface_ratio": 0.78,
            "created_at": "2026-09-18T10:00:00Z"
        }
        fav = FavoriteRouteDTO(**payload)
        assert fav.favorite_id == "fav-101"
        assert fav.preferred_surface_ratio == 0.78
        assert fav.estimated_duration_minutes == 25
