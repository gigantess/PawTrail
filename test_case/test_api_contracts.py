"""FastAPI 백엔드 REST API 입출력 계약(Contract) TDD 테스트 모듈.

실행가능앱 개발지침(섹션 8) 기준:
- POST /api/walks/plan (산책 코스 계획)
- POST /api/surface/analyze (노면 사진 시각적 위험 분석)
- POST /api/walks (산책 완주 기록 저장)
- POST /api/feedback (피드백 저장)
- Pydantic V2 Strict Validation 및 타입 정합성 검증
"""

import pytest
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ValidationError


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


class SurfaceAnalyzeResponseDTO(BaseModel):
    """POST /api/surface/analyze 응답 계약 DTO (지침 섹션 5)."""
    primary_surface: str
    safety_level: Literal["SAFE", "MEDIUM", "DANGER"]
    safety_score: int = Field(..., ge=0, le=100)
    hazard_detected: bool
    hazards: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    ai_comment: str


class CheckInResponseDTO(BaseModel):
    """POST /api/walks 또는 /api/feedback 응답 계약 DTO."""
    success: bool
    walk_history_id: str
    achievement_rate_percent: float = Field(..., ge=0.0, le=100.0)
    message: str


class TestApiContracts:
    """REST API 응답 스키마 계약 일관성 검증 테스트."""


    def test_walk_plan_response_contract(self):
        """산책로 생성 API 응답 DTO 규격 검증."""
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
                        "distance_m": 450.0,
                        "safety_score": 95
                    }
                }
            ],
            "total_distance_m": 1200.0,
            "estimated_duration_minutes": 20,
            "preferred_surfaces": ["grass", "dirt"],
            "surface_breakdown": {"grass": 600.0, "dirt": 400.0, "paved": 200.0},
            "ai_recommendation_comment": "코코의 슬개골 부담을 줄이기 위해 흙길과 잔디 비중 83%로 순환 경로를 구성했습니다.",
            "status": "SUCCESS"
        }
        res = WalkPlanResponseDTO(**payload)
        assert res.status == "SUCCESS"
        assert res.total_distance_m == 1200.0
        assert len(res.features) == 1

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

    def test_surface_analyze_response_contract(self):
        """노면 사진 분석 API 응답 DTO 규격 검증 (지침 섹션 5)."""
        payload = {
            "primary_surface": "asphalt",
            "safety_level": "MEDIUM",
            "safety_score": 72,
            "hazard_detected": True,
            "hazards": ["puddle", "surface_damage"],
            "confidence": 0.86,
            "ai_comment": "노면 일부에 물이 고여 있어 주의가 필요합니다."
        }
        res = SurfaceAnalyzeResponseDTO(**payload)
        assert res.primary_surface == "asphalt"
        assert res.safety_score == 72
        assert res.safety_level == "MEDIUM"
        assert res.hazard_detected is True


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


class TestFavoriteRouteContract:
    """US-14 나만의 코스 즐겨찾기 계약 검증 테스트."""

    def test_favorite_route_contract_valid(self):
        """즐겨찾기 코스 DTO 유효성 검증."""
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

