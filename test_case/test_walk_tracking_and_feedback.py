"""[US-08, US-09, US-11] 산책 기록, 선호 노면 달성률 계산 및 체크인 피드백 TDD 테스트 모듈.

명세서 기준:
- 선호 노면 달성률 공식:
  Achievement Rate (%) = (선호 노면 구간 총 이동 거리 / 전체 이동 거리) * 100
- 산책 완료 체크인 스키마 (US-09, US-11):
  - walk_history_id: str
  - surface_satisfaction_rating: int 1~5
  - surface_accuracy_match: bool
  - feedback_comment: Optional[str]
- 5인 CBT 피드백 반영 모델 (평점 3점 이하 시 가중치 조정 플래그)
"""

import pytest
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ValidationError


class WalkCheckInRequest(BaseModel):
    """US-09, US-11 산책 완료 체크인 및 피드백 요청 스키마."""
    walk_history_id: str
    user_id: str
    dog_id: str
    surface_satisfaction_rating: int = Field(..., ge=1, le=5, description="노면 만족도 (1~5점)")
    surface_accuracy_match: bool = Field(..., description="추천 노면과 실제 노면 일치 여부")
    comment: Optional[str] = Field(None, max_length=500)


def calculate_preferred_surface_achievement_rate(
    surface_segments: List[Dict[str, Any]],
    preferred_surfaces: List[str]
) -> float:
    """산책 경로의 선호 노면 달성률(%) 연산 함수 (US-08)."""
    if not surface_segments:
        return 0.0

    total_dist = sum(seg["distance_m"] for seg in surface_segments)
    if total_dist <= 0:
        return 0.0

    pref_dist = sum(
        seg["distance_m"]
        for seg in surface_segments
        if seg["surface_type"] in preferred_surfaces
    )

    return round((pref_dist / total_dist) * 100.0, 2)


def evaluate_feedback_for_weight_calibration(rating: int, accuracy_match: bool) -> dict:
    """CBT 피드백 기반 노면 가중치 재조정 필요 여부 평가 (Week 5 피드백 반영 로직)."""
    needs_recalibration = False
    action_type = "MAINTAIN"

    if rating <= 2 or not accuracy_match:
        needs_recalibration = True
        action_type = "INCREASE_DISCOUNT"  # 선호 노면 할인율 강화 및 아스팔트 페널티 상향

    return {
        "needs_recalibration": needs_recalibration,
        "action_type": action_type
    }


class TestWalkTrackingAndAchievement:
    """실시간 트래킹 및 선호 노면 달성률(%) 계산 테스트 (US-08)."""

    def test_achievement_rate_calculation_accurate(self):
        """총 1,000m 중 흙길 400m, 잔디 350m일 때 선호 노면 달성률이 75%로 정확히 산출되는지 검증."""
        segments = [
            {"surface_type": "dirt", "distance_m": 400.0},
            {"surface_type": "grass", "distance_m": 350.0},
            {"surface_type": "paved", "distance_m": 150.0},
            {"surface_type": "asphalt", "distance_m": 100.0},
        ]
        preferred = ["dirt", "grass"]

        rate = calculate_preferred_surface_achievement_rate(segments, preferred)
        assert rate == 75.0

    def test_zero_distance_returns_zero_rate(self):
        """이동 거리가 0이거나 세그먼트가 없는 경우 0% 반환 (0으로 나누기 방어)."""
        assert calculate_preferred_surface_achievement_rate([], ["dirt"]) == 0.0
        assert calculate_preferred_surface_achievement_rate([{"surface_type": "dirt", "distance_m": 0.0}], ["dirt"]) == 0.0

    def test_full_preferred_path_returns_100_percent(self):
        """모든 경로가 선호 노면일 경우 100% 반환 검증."""
        segments = [
            {"surface_type": "dirt", "distance_m": 500.0},
            {"surface_type": "grass", "distance_m": 500.0},
        ]
        rate = calculate_preferred_surface_achievement_rate(segments, ["dirt", "grass"])
        assert rate == 100.0


class TestWalkCheckInAndCbtFeedback:
    """산책 완료 체크인 및 5인 CBT 피드백 수집 테스트 (US-09, US-11)."""

    def test_valid_checkin_request_accepted(self):
        """정상적인 만족도 평가 및 체크인 데이터는 검증을 통과해야 함."""
        payload = {
            "walk_history_id": "walk-hist-001",
            "user_id": "user-cbt-1",
            "dog_id": "dog-maltese-001",
            "surface_satisfaction_rating": 5,
            "surface_accuracy_match": True,
            "comment": "흙길 비율이 높아 슬개골에 무리 없이 완주했습니다!"
        }
        checkin = WalkCheckInRequest(**payload)
        assert checkin.surface_satisfaction_rating == 5
        assert checkin.surface_accuracy_match is True

    @pytest.mark.parametrize("invalid_rating", [0, 6, -1, 10])
    def test_out_of_range_rating_rejected(self, invalid_rating):
        """별점이 1~5점 범위를 벗어날 경우 ValidationError 발생 검증."""
        payload = {
            "walk_history_id": "walk-hist-001",
            "user_id": "user-cbt-1",
            "dog_id": "dog-maltese-001",
            "surface_satisfaction_rating": invalid_rating,
            "surface_accuracy_match": True
        }
        with pytest.raises(ValidationError):
            WalkCheckInRequest(**payload)

    def test_low_rating_triggers_recalibration_flag(self):
        """CBT 테스터가 2점 이하를 부여한 경우 가중치 재조정 플래그가 활성화되어야 함."""
        eval_result = evaluate_feedback_for_weight_calibration(rating=2, accuracy_match=True)
        assert eval_result["needs_recalibration"] is True
        assert eval_result["action_type"] == "INCREASE_DISCOUNT"

    def test_high_rating_maintains_weights(self):
        """만족도 4~5점인 경우 기존 가중치 유지 평가 검증."""
        eval_result = evaluate_feedback_for_weight_calibration(rating=5, accuracy_match=True)
        assert eval_result["needs_recalibration"] is False
        assert eval_result["action_type"] == "MAINTAIN"


def apply_feedback_feedforward_penalty(
    base_weights: Dict[str, float],
    disliked_surfaces: List[str]
) -> Dict[str, float]:
    """US-06 피드백 피드포워드: 직전 산책에서 불만족 노면에 대한 회피 페널티 강화."""
    updated = base_weights.copy()
    for surface in disliked_surfaces:
        if surface in updated:
            updated[surface] = round(updated[surface] * 1.5, 2)
    return updated


class TestFeedbackFeedforward:
    """US-06 과거 산책 피드백 기반 노면 페널티 피드포워드 검증."""

    def test_disliked_surface_penalty_enhancement(self):
        """자갈길(gravel, 기본 3.5)에 불만족 피드백 시 페널티가 5.25로 강화되는지 검증."""
        initial_weights = {"grass": 0.6, "dirt": 0.6, "paved": 1.0, "asphalt": 2.5, "gravel": 3.5}
        calibrated = apply_feedback_feedforward_penalty(initial_weights, disliked_surfaces=["gravel"])
        assert calibrated["gravel"] == 5.25
        assert calibrated["grass"] == 0.6  # 선호 노면은 유지


class OfflineCheckInQueueItem(BaseModel):
    """US-15 오프라인 상태에서 IndexedDB에 임시 저장되는 체크인 큐 DTO."""
    local_queue_id: str
    walk_history_id: str
    user_id: str
    dog_id: str
    surface_satisfaction_rating: int = Field(..., ge=1, le=5)
    surface_accuracy_match: bool
    is_synced: bool = False
    captured_offline_at: str


class TestOfflineResilience:
    """US-15 네트워크 단절 시 오프라인 캐싱 및 동기화 테스트."""

    def test_offline_checkin_queue_creation_and_sync(self):
        """오프라인 체크인 큐 아이템이 정상 생성되고 온라인 복구 시 동기화 플래그 전환 검증."""
        item = OfflineCheckInQueueItem(
            local_queue_id="queue-local-001",
            walk_history_id="walk-offline-101",
            user_id="user-cbt-1",
            dog_id="dog-maltese-001",
            surface_satisfaction_rating=5,
            surface_accuracy_match=True,
            is_synced=False,
            captured_offline_at="2026-09-18T13:45:00Z"
        )
        assert item.is_synced is False
        assert item.surface_satisfaction_rating == 5

        # 온라인 재연결 동기화 시뮬레이션
        synced_item = item.model_copy(update={"is_synced": True})
        assert synced_item.is_synced is True

