"""[US-01, US-06] AI Agent 입력 파싱, Pydantic V2 스키마 및 Memory 주입 TDD 테스트 모듈.

명세서 기준:
- 사용자 발화에서 DogBreed, TargetDuration, Condition, PreferredSurfaces 추출
- Pydantic V2 BaseModel 엄격 검증:
  - target_duration_minutes: 5 이상 120 이하
  - lat: -90.0 ~ 90.0, lon: -180.0 ~ 180.0
  - preferred_surfaces: 최소 1개 이상, 허용된 enum 목록
- 필수값(위치, 노면, 시간) 누락 시 Clarification 트리거
- Supabase Long-term Memory: 견종, 체중, 관절 질환 단계(0~4) 및 최근 5회 산책 요약 주입
"""

import pytest
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError

AllowedSurface = Literal["grass", "dirt", "rubber", "paved", "asphalt", "gravel"]


class WalkPlanRequestSchema(BaseModel):
    """US-01 산책 생성 요청 Pydantic V2 스키마 (엄격 검증)."""
    dog_id: str = Field(..., min_length=1, description="반려견 식별자")
    target_duration_minutes: int = Field(..., ge=5, le=120, description="목표 산책 시간(분)")
    preferred_surfaces: List[AllowedSurface] = Field(..., min_length=1, description="선호 노면 목록")
    origin_lat: float = Field(..., ge=-90.0, le=90.0, description="출발지 위도")
    origin_lon: float = Field(..., ge=-180.0, le=180.0, description="출발지 경도")
    user_query: Optional[str] = Field(None, description="원문 사용자 자연어 발화")


class CanineMemoryContext(BaseModel):
    """US-06 에이전트에 주입되는 반려견 롱텀 메모리 맥락 DTO."""
    dog_id: str
    name: str
    breed: str
    patella_luxation_stage: int = Field(..., ge=0, le=4)
    recommended_max_duration: int = Field(..., ge=5, le=120)
    caution_surfaces: List[AllowedSurface]
    recent_walk_count: int = Field(default=0, ge=0)


def evaluate_agent_clarification_need(
    duration: Optional[int],
    surfaces: Optional[List[str]],
    lat: Optional[float],
    lon: Optional[float]
) -> Dict[str, Any]:
    """에이전트 Clarification(되물음) 필요 여부 판단 로직 (US-01 인수조건 2)."""
    missing_fields = []
    if duration is None:
        missing_fields.append("target_duration_minutes")
    if not surfaces:
        missing_fields.append("preferred_surfaces")
    if lat is None or lon is None:
        missing_fields.append("origin_coordinates")

    if missing_fields:
        return {
            "needs_clarification": True,
            "missing_fields": missing_fields,
            "clarification_prompt": f"안전한 산책 경로를 위해 다음 정보를 알려주세요: {', '.join(missing_fields)}"
        }
    return {"needs_clarification": False, "missing_fields": []}


class TestWalkPlanAgentSchema:
    """Pydantic V2 스키마 유효성 및 제약 조건 테스트 (US-01)."""

    def test_valid_request_passes_validation(self):
        """정상적인 요청 페이로드는 검증을 통과해야 함."""
        payload = {
            "dog_id": "dog-123",
            "target_duration_minutes": 25,
            "preferred_surfaces": ["grass", "dirt"],
            "origin_lat": 37.4979,
            "origin_lon": 127.0276,
            "user_query": "3살 말티즈 25분 흙길/잔디 코스 짜줘"
        }
        req = WalkPlanRequestSchema(**payload)
        assert req.dog_id == "dog-123"
        assert req.target_duration_minutes == 25
        assert len(req.preferred_surfaces) == 2

    @pytest.mark.parametrize("invalid_duration", [4, 125, 0, -10])
    def test_invalid_duration_raises_validation_error(self, invalid_duration):
        """산책 시간이 5분 미만이거나 120분 초과일 때 ValidationError 발생 검증."""
        payload = {
            "dog_id": "dog-123",
            "target_duration_minutes": invalid_duration,
            "preferred_surfaces": ["dirt"],
            "origin_lat": 37.4979,
            "origin_lon": 127.0276
        }
        with pytest.raises(ValidationError):
            WalkPlanRequestSchema(**payload)

    def test_empty_preferred_surfaces_rejected(self):
        """선호 노면이 빈 배열인 경우 거부되어야 함 (최소 1개 필수)."""
        payload = {
            "dog_id": "dog-123",
            "target_duration_minutes": 30,
            "preferred_surfaces": [],
            "origin_lat": 37.4979,
            "origin_lon": 127.0276
        }
        with pytest.raises(ValidationError):
            WalkPlanRequestSchema(**payload)

    def test_invalid_surface_enum_rejected(self):
        """허용되지 않은 노면 타입(예: 'concrete', 'snow') 입력 시 거부되어야 함."""
        payload = {
            "dog_id": "dog-123",
            "target_duration_minutes": 30,
            "preferred_surfaces": ["concrete"],
            "origin_lat": 37.4979,
            "origin_lon": 127.0276
        }
        with pytest.raises(ValidationError):
            WalkPlanRequestSchema(**payload)

    @pytest.mark.parametrize("lat,lon", [(95.0, 127.0), (-95.0, 127.0), (37.5, 185.0)])
    def test_invalid_coordinates_rejected(self, lat, lon):
        """위도(-90~90) 및 경도(-180~180) 유효 범위를 벗어난 경우 거부되어야 함."""
        payload = {
            "dog_id": "dog-123",
            "target_duration_minutes": 30,
            "preferred_surfaces": ["dirt"],
            "origin_lat": lat,
            "origin_lon": lon
        }
        with pytest.raises(ValidationError):
            WalkPlanRequestSchema(**payload)


class TestAgentClarificationLoop:
    """필수 파라미터 누락 시 Clarification(되물음) 대화 루프 테스트 (US-01 인수조건 2)."""

    def test_missing_duration_triggers_clarification(self):
        """시간 파라미터 누락 시 되물음이 정상 트리거되어야 함."""
        result = evaluate_agent_clarification_need(
            duration=None,
            surfaces=["dirt"],
            lat=37.4979,
            lon=127.0276
        )
        assert result["needs_clarification"] is True
        assert "target_duration_minutes" in result["missing_fields"]

    def test_missing_surfaces_triggers_clarification(self):
        """선호 노면 누락 시 되물음 트리거 검증."""
        result = evaluate_agent_clarification_need(
            duration=20,
            surfaces=[],
            lat=37.4979,
            lon=127.0276
        )
        assert result["needs_clarification"] is True
        assert "preferred_surfaces" in result["missing_fields"]

    def test_all_fields_present_proceeds_without_clarification(self):
        """모든 필수 항목이 존재할 경우 Clarification 없이 실행 단계로 진입해야 함."""
        result = evaluate_agent_clarification_need(
            duration=20,
            surfaces=["grass"],
            lat=37.4979,
            lon=127.0276
        )
        assert result["needs_clarification"] is False
        assert len(result["missing_fields"]) == 0


class TestCanineMemoryContextInjection:
    """반려견 건강 프로필 및 과거 산책 맥락 주입 테스트 (US-06)."""

    def test_senior_patella_dog_generates_correct_constraints(self, sample_dog_profiles):
        """슬개골 2기 소형견 프로필 조회 시 주의 노면 및 시간 제약 조건 생성 검증."""
        dog = sample_dog_profiles["tester1_maltese"]
        
        # 비즈니스 로직: 슬개골 2기 이상인 경우 아스팔트/자갈 주의 노면 자동 지정
        caution = ["asphalt", "gravel"] if dog["patella_luxation_stage"] >= 2 else []
        max_dur = 25 if dog["patella_luxation_stage"] >= 2 else 45

        context = CanineMemoryContext(
            dog_id=dog["dog_id"],
            name=dog["name"],
            breed=dog["breed"],
            patella_luxation_stage=dog["patella_luxation_stage"],
            recommended_max_duration=max_dur,
            caution_surfaces=caution,
            recent_walk_count=5
        )

        assert context.patella_luxation_stage == 2
        assert "asphalt" in context.caution_surfaces
        assert context.recommended_max_duration <= 30


def calculate_target_walk_distance(
    duration_minutes: int,
    dog_size: Literal["small", "medium", "large"],
    patella_stage: int = 0
) -> float:
    """US-16: 사용자가 지정한 산책 시간 및 반려견 체급/건강 상태 기반 목표 거리(m) 산출."""
    # 보행 속도 (m/min): 소형견 50 (3.0km/h), 중형견 60 (3.6km/h), 대형견 70 (4.2km/h)
    speed_map = {"small": 50.0, "medium": 60.0, "large": 70.0}
    base_speed = speed_map.get(dog_size, 50.0)

    # 슬개골 2기 이상 또는 노령견은 20% 감속 (안전 보행)
    if patella_stage >= 2:
        base_speed *= 0.8  # 40.0 m/min (2.4 km/h)

    return round(base_speed * duration_minutes, 1)


class TestTargetDurationCourseScheduler:
    """US-16 사용자 지정 시간(Target Duration) 기반 코스 거리 산출 테스트."""

    def test_small_dog_30min_walk_distance(self):
        """소형견 30분 산책 시 목표 거리가 1,500m로 산출되는지 검증."""
        dist = calculate_target_walk_distance(duration_minutes=30, dog_size="small")
        assert dist == 1500.0

    def test_large_dog_45min_walk_distance(self):
        """대형견 45분 산책 시 목표 거리가 3,150m로 산출되는지 검증."""
        dist = calculate_target_walk_distance(duration_minutes=45, dog_size="large")
        assert dist == 3150.0

    def test_patella_dog_duration_distance_mitigation(self):
        """슬개골 2기 반려견은 속도가 감속(40m/min)되어 20분 기준 800m로 산출되는지 검증."""
        dist = calculate_target_walk_distance(duration_minutes=20, dog_size="small", patella_stage=2)
        assert dist == 800.0

