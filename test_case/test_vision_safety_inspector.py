"""[US-04, US-05] 비전 멀티모달 공원 안내판 판독 및 완주 후기 지도 보강 TDD 테스트 모듈.

4b06010 커밋 및 실행가능앱 아키텍처(docs/04) 기준:
- Vision 모델은 산책 중 비현실적인 실시간 리드줄 파지 바닥 촬영 우회를 지양하고 2대 축으로 운용:
  1. [US-04] 공원 입구 종합안내판 판독 (ParkBoardInspector, POST /api/walks/inspect-board):
     - park_name: str
     - has_dirt_trail: bool
     - has_grass_zone: bool
     - dog_restricted_zones: List[str] (예: 어린이놀이터, 생태연못 데크)
     - detected_surfaces: List[str]
     - confidence_score: float (0.0~1.0)
     - summary_comment: str
     - requires_recapture: bool
     - 안내판에서 추출된 반려견 금지 구역은 라우팅 차단(Blocked Nodes)으로 변환
  2. [US-05] 완주 후기 사진 비전 검증 및 지도 영구 보강 (CommunityMapEnricher, POST /api/walks/verify-surface):
     - verified_surface: str ('dirt', 'grass', 'rubber', 'paved', 'asphalt', 'gravel')
     - is_safe_for_paws: bool
     - hazard_detected: bool
     - hazards: List[str]
     - confidence: float (0.0~1.0)
     - admin_approval_suggested: bool
     - confidence >= 0.85 & 위험물 미검출 시 OSM DB 링크의 surface 속성을 'community_verified'로 즉시 영구 업데이트
     - confidence < 0.85 시 수동 검토 대기 큐(PENDING_REVIEW)로 격리
"""

import pytest
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ValidationError

SurfaceType = Literal["dirt", "grass", "rubber", "paved", "asphalt", "gravel"]


class ParkBoardInspectionResult(BaseModel):
    """[US-04] 공원 종합안내판 비전 판독 Pydantic V2 스키마."""
    park_name: str = Field(..., min_length=2, description="공원 명칭")
    has_dirt_trail: bool = Field(..., description="흙길/비포장 산책로 존재 여부")
    has_grass_zone: bool = Field(default=False, description="잔디밭/초지 구역 존재 여부")
    dog_restricted_zones: List[str] = Field(default_factory=list, description="반려견 출입 금지 구역")
    detected_surfaces: List[SurfaceType] = Field(default_factory=list, description="인식된 노면 범례 목록")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="비전 판독 신뢰도")
    summary_comment: str = Field(..., min_length=5, description="공원 산책로 요약 설명")
    requires_recapture: bool = Field(default=False, description="각도 왜곡/저조도 재촬영 필요 여부")


class SurfaceEnrichmentResult(BaseModel):
    """[US-05] 완주 후기 노면 사진 검증 Pydantic V2 스키마."""
    verified_surface: SurfaceType = Field(..., description="검증된 노면 재질")
    is_safe_for_paws: bool = Field(..., description="발바닥 안전 적합 여부")
    hazard_detected: bool = Field(default=False, description="위험물(유리, 뾰족한 돌 등) 감지 여부")
    hazards: List[str] = Field(default_factory=list, description="검출된 위험 요소")
    confidence: float = Field(..., ge=0.0, le=1.0, description="노면 판별 신뢰도 (0.0~1.0)")
    admin_approval_suggested: bool = Field(default=False, description="신뢰도 충족에 따른 자동 승인 제안")


def process_park_board_constraints(result: ParkBoardInspectionResult) -> Dict[str, Any]:
    """공원 안내판 판독 결과를 라우팅 제약조건으로 변환하는 핸들러 (US-04)."""
    if result.requires_recapture or result.confidence_score < 0.50:
        return {
            "success": False,
            "blocked_zones": [],
            "preferred_surfaces": [],
            "error_message": "안내판 사진이 흐리거나 신뢰도가 낮아 기본 라우팅 모드로 진행합니다."
        }

    return {
        "success": True,
        "blocked_zones": result.dog_restricted_zones,
        "has_dirt_trail": result.has_dirt_trail,
        "has_grass_zone": result.has_grass_zone,
        "prioritized_surfaces": [s for s in result.detected_surfaces if s in ["dirt", "grass"]],
        "routing_notice": f"{result.park_name} 진입: {', '.join(result.dog_restricted_zones) if result.dog_restricted_zones else '제한구역 없음'} 우회 적용"
    }


def handle_surface_enrichment(result: SurfaceEnrichmentResult, way_id: str) -> Dict[str, Any]:
    """완주 후기 비전 판독 결과에 따른 지도 노면 속성 영구 갱신 핸들러 (US-05)."""
    # 신뢰도 0.85 이상이며 위험물이 없을 때 지도에 영구 반영
    if result.confidence >= 0.85 and not result.hazard_detected:
        return {
            "status": "APPLIED",
            "way_id": way_id,
            "updated_surface": result.verified_surface,
            "source": "community_verified",
            "message": f"Way {way_id}의 노면이 {result.verified_surface}로 영구 보강되었습니다."
        }
    else:
        return {
            "status": "PENDING_REVIEW",
            "way_id": way_id,
            "updated_surface": None,
            "source": None,
            "message": "신뢰도 기준(0.85) 미달 또는 위험물이 감지되어 수동 검토 대기 큐로 격리되었습니다."
        }


class TestParkBoardInspector:
    """공원 종합안내판 비전 분석 유효성 및 제약조건 변환 테스트 (US-04)."""

    def test_valid_park_board_output_parsed_successfully(self):
        """정상적인 보라매공원 안내판 JSON 응답이 Pydantic 스키마를 올바르게 통과하는지 검증."""
        raw_json = {
            "park_name": "보라매공원",
            "has_dirt_trail": True,
            "has_grass_zone": True,
            "dog_restricted_zones": ["생태연못 관찰데크", "어린이 놀이터"],
            "detected_surfaces": ["dirt", "grass", "rubber", "paved"],
            "confidence_score": 0.92,
            "summary_comment": "공원 둘레에 비포장 흙길 산책로가 조성되어 있으며 북동쪽 잔디마당 이용이 가능합니다.",
            "requires_recapture": False
        }
        output = ParkBoardInspectionResult(**raw_json)
        assert output.park_name == "보라매공원"
        assert output.has_dirt_trail is True
        assert "생태연못 관찰데크" in output.dog_restricted_zones
        assert output.confidence_score == 0.92
        assert output.requires_recapture is False

    def test_park_board_constraints_block_restricted_zones(self):
        """안내판에서 추출된 반려견 출입 금지 구역이 라우팅 차단 목록에 정확히 매핑되는지 검증."""
        result = ParkBoardInspectionResult(
            park_name="올림픽공원",
            has_dirt_trail=True,
            has_grass_zone=False,
            dog_restricted_zones=["장미광장", "야외수영장"],
            detected_surfaces=["dirt", "paved"],
            confidence_score=0.88,
            summary_comment="토성 둘레길 흙길 코스가 권장됩니다."
        )
        constraints = process_park_board_constraints(result)
        assert constraints["success"] is True
        assert constraints["blocked_zones"] == ["장미광장", "야외수영장"]
        assert constraints["has_dirt_trail"] is True
        assert "dirt" in constraints["prioritized_surfaces"]
        assert "장미광장, 야외수영장 우회 적용" in constraints["routing_notice"]

    def test_low_confidence_park_board_triggers_fallback(self):
        """안내판 사진이 흐려 신뢰도 0.50 미만인 경우 기본 라우팅 모드로 안전하게 Fallback되는지 검증."""
        result = ParkBoardInspectionResult(
            park_name="불명 공원",
            has_dirt_trail=False,
            has_grass_zone=False,
            dog_restricted_zones=[],
            detected_surfaces=[],
            confidence_score=0.35,
            summary_comment="조도가 낮아 텍스트 인식이 불가능합니다.",
            requires_recapture=True
        )
        constraints = process_park_board_constraints(result)
        assert constraints["success"] is False
        assert "신뢰도가 낮아" in constraints["error_message"]


class TestCommunitySurfaceEnrichment:
    """완주 후기 사진 비전 검증 및 지도 속성 보강 테스트 (US-05)."""

    def test_high_confidence_review_permanently_enriches_osm_way(self):
        """신뢰도 0.89의 고화질 흙길 후기 사진 제출 시 지도 속성이 영구 업데이트(APPLIED)되는지 검증."""
        result = SurfaceEnrichmentResult(
            verified_surface="dirt",
            is_safe_for_paws=True,
            hazard_detected=False,
            hazards=[],
            confidence=0.89,
            admin_approval_suggested=True
        )
        outcome = handle_surface_enrichment(result, way_id="osm-way-998822")
        assert outcome["status"] == "APPLIED"
        assert outcome["way_id"] == "osm-way-998822"
        assert outcome["updated_surface"] == "dirt"
        assert outcome["source"] == "community_verified"

    def test_low_confidence_or_hazard_review_routes_to_pending_queue(self):
        """신뢰도 미달(0.70) 또는 깨진 유리 검출 시 즉각 반영되지 않고 검토 대기 큐(PENDING_REVIEW)로 격리되는지 검증."""
        # 케이스 1: 신뢰도 부족
        result_low_conf = SurfaceEnrichmentResult(
            verified_surface="grass",
            is_safe_for_paws=True,
            hazard_detected=False,
            confidence=0.72,
            admin_approval_suggested=False
        )
        outcome1 = handle_surface_enrichment(result_low_conf, way_id="osm-way-111111")
        assert outcome1["status"] == "PENDING_REVIEW"
        assert outcome1["updated_surface"] is None

        # 케이스 2: 위험물(깨진 유리) 검출
        result_hazard = SurfaceEnrichmentResult(
            verified_surface="paved",
            is_safe_for_paws=False,
            hazard_detected=True,
            hazards=["broken_glass"],
            confidence=0.95,
            admin_approval_suggested=False
        )
        outcome2 = handle_surface_enrichment(result_hazard, way_id="osm-way-222222")
        assert outcome2["status"] == "PENDING_REVIEW"
        assert outcome2["updated_surface"] is None
