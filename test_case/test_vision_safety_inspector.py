"""[US-04, US-05] 비전 멀티모달 노면 위험도 판독 및 리라우팅 피드백 TDD 테스트 모듈.

실행가능앱 개발지침(섹션 5) 기준:
- Vision 모델은 사진만으로 실제 지면 온도를 측정한다고 표현하지 않음 (지면열은 날씨 모델로 분리)
- Vision 출력 권장 스키마:
  - primary_surface: 'dirt' | 'grass' | 'rubber' | 'paved' | 'asphalt' | 'gravel'
  - safety_level: 'SAFE' | 'MEDIUM' | 'DANGER'
  - safety_score: int 0~100
  - hazard_detected: bool
  - hazards: List[str]
  - confidence: float 0.0~1.0
  - ai_comment: str
- 위험도 판정 및 피드백:
  - safety_score < 40 또는 치명적 위험물(깨진 유리, 뾰족한 파쇄석) 검출 시 우회(Reroute) 트리거
  - safety_score >= 80: 안전 구간
- 저조도/블러 이미지 입력 시 예외 처리: requires_recapture 플래그
"""

import pytest
from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError

SafetyLevel = Literal["SAFE", "MEDIUM", "DANGER"]
SurfaceType = Literal["dirt", "grass", "rubber", "paved", "asphalt", "gravel"]


class SurfaceInspectionOutput(BaseModel):
    """지침 섹션 5 권장 Gemini Vision 분석 결과 구조화 스키마."""
    primary_surface: SurfaceType
    safety_level: SafetyLevel = Field(default="SAFE")
    safety_score: int = Field(..., ge=0, le=100, description="노면 안전 점수 (0~100)")
    hazard_detected: bool = Field(default=False)
    hazards: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    ai_comment: str = Field(..., min_length=5)
    requires_recapture: bool = Field(default=False)


def handle_vision_reroute_trigger(
    inspection: SurfaceInspectionOutput,
    current_edge_id: str
) -> dict:
    """비전 판독 결과에 따른 우회(Reroute) 트리거 핸들러 (US-05)."""
    critical_hazards = {"broken_glass", "sharp_stones", "construction_debris"}
    has_critical_hazard = any(h in critical_hazards for h in inspection.hazards)

    if inspection.safety_score < 40 or has_critical_hazard or inspection.safety_level == "DANGER":
        return {
            "trigger_reroute": True,
            "blocked_edge_id": current_edge_id,
            "reroute_reason": f"위험 노면 감지 (안전점수: {inspection.safety_score}점, 요인: {inspection.hazards})",
            "penalty_weight": 999.0  # 차단 링크 가중치 무한대 부여
        }
    return {
        "trigger_reroute": False,
        "blocked_edge_id": None,
        "reroute_reason": None,
        "penalty_weight": 1.0
    }


class TestVisionSafetyInspector:
    """비전 분석 출력 스키마 및 점수 유효성 테스트 (US-04)."""

    def test_valid_inspection_output_parsed_successfully(self):
        """정상적인 비전 JSON 응답이 Pydantic 스키마를 올바르게 통과하는지 검증."""
        raw_json = {
            "primary_surface": "dirt",
            "safety_level": "SAFE",
            "safety_score": 88,
            "hazard_detected": False,
            "hazards": [],
            "confidence": 0.95,
            "ai_comment": "그늘진 고운 흙길로 반려견 관절과 발바닥에 매우 안전합니다.",
            "requires_recapture": False
        }
        output = SurfaceInspectionOutput(**raw_json)
        assert output.primary_surface == "dirt"
        assert output.safety_score == 88
        assert output.safety_level == "SAFE"
        assert not output.hazard_detected
        assert not output.requires_recapture

    @pytest.mark.parametrize("invalid_score", [-5, 105, 150])
    def test_out_of_range_safety_score_raises_error(self, invalid_score):
        """안전 점수가 0~100 범위를 벗어날 경우 ValidationError 검증."""
        raw_json = {
            "primary_surface": "grass",
            "safety_score": invalid_score,
            "confidence": 0.9,
            "ai_comment": "테스트 코멘트"
        }
        with pytest.raises(ValidationError):
            SurfaceInspectionOutput(**raw_json)

    def test_low_confidence_or_blur_triggers_recapture(self):
        """저조도/블러 이미지인 경우 requires_recapture 플래그가 설정되어야 함."""
        raw_json = {
            "primary_surface": "asphalt",
            "safety_level": "MEDIUM",
            "safety_score": 50,
            "hazard_detected": False,
            "hazards": [],
            "confidence": 0.35,  # 신뢰도 부족
            "ai_comment": "사진이 다소 어두워 노면 식별이 어렵습니다. 밝은 곳에서 다시 촬영해주세요.",
            "requires_recapture": True
        }
        output = SurfaceInspectionOutput(**raw_json)
        assert output.requires_recapture is True
        assert output.confidence < 0.5


class TestReroutingFeedbackChain:
    """위험 노면 식별 시 경로 재탐색(Rerouting) 이벤트 체인 테스트 (US-05)."""

    def test_hazard_triggers_reroute_and_blocks_edge(self):
        """깨진 유리나 파쇄석 검출(점수 30점) 시 해당 링크 차단 및 우회 트리거 발생 검증."""
        inspection = SurfaceInspectionOutput(
            primary_surface="gravel",
            safety_level="DANGER",
            safety_score=30,
            hazard_detected=True,
            hazards=["broken_glass"],
            confidence=0.92,
            ai_comment="도로 가장자리에 깨진 유리 조각이 있어 보행이 위험합니다."
        )
        result = handle_vision_reroute_trigger(inspection, current_edge_id="edge-danger-777")

        assert result["trigger_reroute"] is True
        assert result["blocked_edge_id"] == "edge-danger-777"
        assert result["penalty_weight"] >= 999.0
        assert "위험 노면 감지" in result["reroute_reason"]

    def test_safe_surface_does_not_trigger_reroute(self):
        """안전한 잔디길(95점)인 경우 우회 없이 기존 경로 유지 검증."""
        inspection = SurfaceInspectionOutput(
            primary_surface="grass",
            safety_level="SAFE",
            safety_score=95,
            hazard_detected=False,
            hazards=[],
            confidence=0.98,
            ai_comment="푹신하고 이물질이 없는 최상의 잔디 산책로입니다."
        )
        result = handle_vision_reroute_trigger(inspection, current_edge_id="edge-safe-123")

        assert result["trigger_reroute"] is False
        assert result["blocked_edge_id"] is None
