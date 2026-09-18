# [개발 지침서] PawTrail 아키텍처 리팩토링 및 구현 가이드 (for Gemini Code Assist)

## 1. 프로젝트 개요 및 리팩토링 배경

* **프로젝트명**: PawTrail (반려견 맞춤형 안심 노면 산책 에이전트 및 기록·공유 플랫폼)
* **리팩토링 목적**:
  1. **현장 실시간 촬영 우회의 비현실성 극복**: 산책 중 발밑의 위험 노면(파쇄석, 유리 등)을 리드줄을 잡은 채 촬영하여 실시간 재탐색을 받는 방식은 즉시성 결여 및 극히 좁은 가시거리(반경 1~2m)로 인해 실효성이 떨어짐.
  2. **국내 OSM 노면(`surface`) 속성 결측(Missing Values) 해결**: 국내 도심지 OSM 데이터의 노면 속성 결측률이 80% 이상이므로 순수 OSM에만 의존할 수 없음.
  3. **위성 데이터의 현실적 융합**: 원시 위성 영상의 해상도 한계 및 가로수 수관 차폐(Tree Canopy Occlusion) 문제를 극복하기 위해, 항공·위성사진 판독 기반 **'환경부 토지피복지도(Land Cover Map) 세분류'** 공공 공간정보를 결합한 고정밀·경량 노면 분류 파이프라인 구축.
  4. **AI Native 핵심 가치 집중**: 바닥부터 복잡한 GIS 엔진을 코딩하는 대신, **AI Agent가 도구(Routing API, 공간 데이터)를 자율 제어하고 Vision AI가 지도의 빈틈을 채우는 데이터 선순환 구조**로 개편.

---

## 2. 3대 핵심 아키텍처 및 기능 변경 사항

### ① 멀티모달(Vision AI)의 역할 전환 (Pivot)
* ❌ **기존**: 산책 도중 발밑 사진 촬영 ➔ 실시간 턴바이턴 우회로 계산 (폐기)
* ⭕ **개선 (2가지 모드 지원)**:
  1. **사전 진입 시: 공원 종합안내판 비전 판독 (`ParkBoardInspector`)**
     - 공원 입구 오프라인 안내판 사진을 업로드하면 Gemini 1.5 Flash가 안내판 내 산책로 다이어그램과 범례(흙길, 잔디밭, 포장로, 반려견 출입 금지 구역)를 시각적으로 판독하여 구조화된 구역 데이터로 변환.
  2. **산책 완주 후: 커뮤니티 노면 제보 검증 및 지도 라벨링 (`CommunityMapEnricher`)**
     - 사용자가 완주 후 "이 구간 흙길/공사 중" 사진 후기를 남기면, 비전 모델이 노면 재질을 자동 검증·분류하여 결측되어 있던 지도 링크 속성을 영구 보정.

### ② 지도 데이터 파이프라인 개편 (위성 판독 토지피복도 + 공공 폴리곤 + 시드 데이터)
* **원시 위성사진 직접 CV 분석 배제 및 토지피복지도 세분류 융합 (핵심 개선)**:
  - 위성/항공사진 직접 판독 시 발생하는 수관 차폐(가로수 잎사귀에 가려진 바닥 식별 불가) 및 10m급 저해상도 한계를 기술적으로 우회.
  - 환경부(EGIS)가 항공·위성사진을 고정밀 판독하여 벡터화한 **'토지피복지도 세분류'** 공공데이터 연계:
    - `인공포장지(아스팔트/콘크리트)` ➔ `asphalt` / `paved` 매핑
    - `나지(흙/모래)` ➔ `dirt` 매핑
    - `초지(잔디밭/풀밭)` ➔ `grass` 매핑
* **OSM 보행 선형 + 토지피복/공원 폴리곤 공간 결합 (Spatial Join)**:
  - OSM에서 보행로 뼈대 선형(`highway=footway, pedestrian, path`) 추출.
  - 도로 링크와 환경부 토지피복 레이어 및 국가공간정보포털 **'도시공원 경계'**, **'하천구역도'** 폴리곤을 결합하여 결측 링크의 흙/잔디/포장 비율을 0.1초 만에 자동 계산.
* **테스트베드 시범구역 정사영상(항공사진) 육안 검증 시드(Seed) 데이터셋 구축**:
  - 5인 실사용자 테스트 구역(예: 대전 특정 공원 반경 1.5km)의 주요 링크를 카카오/네이버 위성 모드(스카이뷰) 및 로드뷰로 육안 교차 검증하여 100% 신뢰도의 SQLite/GeoJSON 시드 데이터셋 사전 탑재.

### ③ AI Agent 중심의 사전(Pre-walk) 최적화 및 간소화된 UX
* **출발 전 최적화**: LangGraph Agent가 사용자 요청(견종, 체급, 관절 상태, 선호 노면 칩 선택, 목표 시간)을 분석해 흙길/잔디길 비중이 극대화된 Waypoint를 최적화하여 1회에 안전한 순환 경로 생성.
* **산책 중 & 완주 후 UX**: 지도 위 노면별 색상 Polyline 프리뷰를 보며 산책하고, 산책 종료 후 "체크인"을 통해 실제 노면 일치도 및 만족도 피드백을 수집하여 Agent Memory에 반영.

---

## 3. Gemini Code Assist 구현 명세

### 3.1 Pydantic 스키마 및 DTO 정의

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from enum import Enum

class SurfaceType(str, Enum):
    DIRT = "dirt"           # 흙길/숲길 (환경부 토지피복: 나지)
    GRASS = "grass"         # 잔디길 (환경부 토지피복: 초지)
    RUBBER = "rubber"       # 탄성포장/우레탄
    PAVED = "paved"         # 보도블록
    ASPHALT = "asphalt"     # 아스팔트 (환경부 토지피복: 인공포장)
    GRAVEL = "gravel"       # 자갈/파쇄석

class SurfaceSourceType(str, Enum):
    LAND_COVER_MAP = "land_cover_map"   # 환경부 토지피복지도 기반 판정
    PARK_POLYGON = "park_polygon"       # 도시공원/하천 폴리곤 Spatial Join 추정
    SEED_VERIFIED = "seed_verified"     # 위성/로드뷰 육안 교차 검증 시드
    COMMUNITY = "community_verified"    # 사용자 비전 제보 검증
    ESTIMATED_FALLBACK = "estimated"    # 도로 위계 기본 Fallback

class DogProfile(BaseModel):
    breed: str
    weight_kg: float
    joint_care_level: int = Field(default=0, ge=0, le=4, description="관절 안심 케어 수준 0~4")
    preferred_surfaces: List[SurfaceType]

class WalkPlanRequest(BaseModel):
    dog_id: str
    origin_lat: float
    origin_lon: float
    target_duration_minutes: int = Field(ge=5, le=120)
    selected_surfaces: List[SurfaceType]
    use_parking_as_origin: bool = False

# 경로 세그먼트별 노면 추정 메타데이터
class RouteSegmentMetadata(BaseModel):
    link_id: str
    surface: SurfaceType
    surface_source: SurfaceSourceType
    confidence: float = Field(ge=0.0, le=1.0)
    land_cover_breakdown: Optional[Dict[str, float]] = None  # 예: {"grass": 0.7, "dirt": 0.3}

# 공원 종합안내판 분석 결과 스키마
class ParkBoardInspectionResult(BaseModel):
    park_name: Optional[str]
    has_dirt_trail: bool
    has_grass_zone: bool
    dog_restricted_zones: List[str] = Field(default_factory=list)
    detected_surfaces: List[SurfaceType]
    confidence_score: float = Field(ge=0.0, le=1.0)
    summary_comment: str

# 커뮤니티 노면 제보 검증 스키마
class SurfaceEnrichmentResult(BaseModel):
    verified_surface: SurfaceType
    is_safe_for_paws: bool
    hazard_detected: bool
    hazards: List[str] = Field(default_factory=list)
    confidence: float
    admin_approval_suggested: bool
```

---

### 3.2 토지피복 공간정보 연동 서비스 구현 가이드 (Spatial Service)

```python
# app/services/spatial_service.py
import geopandas as gpd
from shapely.geometry import LineString, Point
from app.schemas import SurfaceType, SurfaceSourceType

class LandCoverSpatialService:
    """
    환경부 토지피복지도(세분류) 및 도시공원 폴리곤과의 Spatial Join을 통해
    OSM 보행로 링크의 노면 재질을 즉각 판별하는 서비스 모듈
    """
    def __init__(self, land_cover_geojson_path: str, park_polygon_path: str):
        # 5주 프로젝트용 시범구역 벡터 레이어 사전 로드 (GeoDataFrame)
        self.land_cover_gdf = gpd.read_file(land_cover_geojson_path)
        self.park_gdf = gpd.read_file(park_polygon_path)

    def resolve_link_surface(self, link_geom: LineString, osm_surface: Optional[str] = None) -> tuple[SurfaceType, SurfaceSourceType, float]:
        # 1. OSM 태그가 명확한 경우 우선 사용
        if osm_surface in ["dirt", "ground", "earth"]:
            return SurfaceType.DIRT, SurfaceSourceType.SEED_VERIFIED, 0.95
        if osm_surface == "grass":
            return SurfaceType.GRASS, SurfaceSourceType.SEED_VERIFIED, 0.95

        # 2. 환경부 토지피복지도(Land Cover Map)와의 공간 교차 검사
        intersected = self.land_cover_gdf[self.land_cover_gdf.intersects(link_geom)]
        if not intersected.empty:
            # 가장 많이 겹치는 토지피복 대분류/세분류 코드 확인
            dominant_cover = intersected.iloc[0].get("cover_code", "")
            if dominant_cover in ["초지", "grassland"]:
                return SurfaceType.GRASS, SurfaceSourceType.LAND_COVER_MAP, 0.90
            elif dominant_cover in ["나지", "bare_soil"]:
                return SurfaceType.DIRT, SurfaceSourceType.LAND_COVER_MAP, 0.90
            elif dominant_cover in ["인공포장", "paved_road"]:
                return SurfaceType.ASPHALT, SurfaceSourceType.LAND_COVER_MAP, 0.85

        # 3. 도시공원 폴리곤 경계 내부인 경우 흙길(기본) 추정
        park_intersected = self.park_gdf[self.park_gdf.intersects(link_geom)]
        if not park_intersected.empty:
            return SurfaceType.DIRT, SurfaceSourceType.PARK_POLYGON, 0.75

        # 4. Fallback (일반 도로망)
        return SurfaceType.PAVED, SurfaceSourceType.ESTIMATED_FALLBACK, 0.50
```

---

### 3.3 Vision AI 프롬프트 가이드 (Gemini 1.5 Flash)

#### 1) 공원 안내판 판독 프롬프트 (`inspect_park_board`)
```text
You are an expert GIS and park information board analyst.
Analyze the uploaded park map/information board image and extract detailed trail information for dog walking.

Tasks:
1. Identify if the park has unpaved paths (흙길/산책로), grass areas (잔디마당), or paved walking paths.
2. Detect any specific regulations or pet-restricted zones (반려견 출입 제한 구역/생태보존지역).
3. Cross-reference visual representations of trails and match with ground surface textures.
4. Return the output in strict accordance with the ParkBoardInspectionResult JSON schema.
```

#### 2) 커뮤니티 노면 제보 검증 프롬프트 (`verify_surface_image`)
```text
You are an expert surface inspection system for canine safety.
Analyze the photo taken on the walking path and verify the exact surface material and foot-pad hazards.

Rules:
- Classify into: dirt, grass, rubber, paved, asphalt, gravel.
- Check for sharp stones, broken glass, construction debris, or excessive mud.
- Return the output in strict accordance with the SurfaceEnrichmentResult JSON schema.
```

---

### 3.4 핵심 API 엔드포인트 구현 명세 (FastAPI)

```python
# app/api/walks.py
from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas import WalkPlanRequest, ParkBoardInspectionResult, SurfaceEnrichmentResult

router = APIRouter(prefix="/api/walks", tags=["walks"])

@router.post("/plan")
async def create_walk_plan(req: WalkPlanRequest):
    """
    1. Long-term Memory에서 견공 건강 이력 조회
    2. 사용자 지정 시간(target_duration_minutes) 기반 목표 거리 계산
    3. LandCoverSpatialService를 활용해 선호 노면(초지, 나지) 가중치 Waypoint 후보 선정
    4. Routing API(OpenRouteService 등) 호출하여 순환 GeoJSON 생성
    5. 노면별 구간 분기 Polyline 메타데이터 및 surface_source 투명성 정보 반환
    """
    pass

@router.post("/inspect-board", response_model=ParkBoardInspectionResult)
async def inspect_park_board(file: UploadFile = File(...)):
    """
    공원 입구 종합안내판 사진을 분석하여 흙길/잔디길 구간 및 반려견 출입 정보 추출
    """
    pass

@router.post("/verify-surface", response_model=SurfaceEnrichmentResult)
async def verify_surface_report(file: UploadFile = File(...), link_id: str = None):
    """
    산책 완료 후 견주가 제보한 노면 사진을 분석하여 지도 링크 메타데이터 갱신
    """
    pass
```

---

## 4. 코드 생성 시 Gemini Code Assist 주의사항

1. **위성 원시 영상 CV 처리 절대 금지**:
   - Sentinel-2나 위성 원시 타일 이미지를 다운로드받아 U-Net/SAM 등으로 시맨틱 세그멘테이션을 수행하는 고비용 CV 코드를 작성하지 말 것.
   - 대신 **환경부 토지피복지도(Land Cover Map) 세분류 벡터 데이터셋(GeoJSON/SHP)을 로드하여 `geopandas`의 공간 교차(Spatial Join)로 노면을 0.1초 만에 판별하는 코드**를 우선 작성할 것.
2. **복잡한 GIS 엔진 직접 구현 배제**:
   - 다익스트라나 A* 그래프 탐색 알고리즘을 바닥부터 직접 구현하지 말고, **OpenRouteService / OSRM 도보 라우팅 API 도구 래퍼**와 Waypoint 최적화 함수를 작성할 것.
3. **모바일 백그라운드 GPS 제외**:
   - OS 정책상 백그라운드 수신이 차단되는 모바일 브라우저의 한계를 인정하고, **Screen Wake Lock API 기반 포켓 모드** 및 **상용 지도(네이버/카카오) 딥링크 URL 생성 유틸리티**를 구현할 것.
4. **Pydantic V2 호환성 및 투명성**:
   - 모든 스키마 및 LangGraph Tool 입력 정의 시 Pydantic V2 문법(`model_validate`, `Field(ge=...)`)을 준수할 것.
   - 추정된 노면 데이터는 반드시 `surface_source` 필드(`land_cover_map`, `park_polygon`, `estimated`)를 명시하여 사용자에게 데이터 출처를 투명하게 공개할 것.
