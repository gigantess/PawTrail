# PawTrail 문서 개정 지침
## for Gemini Code Assist

> 목적: PawTrail의 기존 프로젝트 문서 7종을 하나의 일관된 제품 정의와 기술 아키텍처를 기준으로 전면 정합화하기 위한 Gemini Code Assist용 개정 지침이다.
>
> **중요:** 이 작업의 목표는 단순한 문구 수정이나 MVP/데모 제작이 아니다. 실제 사용 가능한 PawTrail 서비스의 기획·요구사항·아키텍처·구현계획·작업량·발표 논리를 서로 일치시키는 것이다.

---

# 1. 개정 대상 문서

다음 7개 문서를 함께 검토하고 상호 정합성을 유지한다.

1. `01_PawTrail_Project_Proposal.md`
2. `02_PawTrail_Team_building.md`
3. `03_PawTrail_Agile_User_Stories.md`
4. `04_PawTrail_Architecture_Design.md`
5. `05_PawTrail_Detailed_Implementation_Plan.md`
6. `06_PawTrail_Task_Breakdown_and_Estimations.md`
7. `07_PawTrail_Presentation_Pain_Points.md`

## 개정 원칙

- 한 문서만 독립적으로 수정하지 않는다.
- 핵심 개념이 변경되면 7개 문서 전체의 관련 내용을 추적하여 수정한다.
- User Story가 변경되면 Architecture → Implementation Plan → Task Breakdown → Presentation까지 연쇄적으로 검토한다.
- 구현 가능성을 높이기 위해 기존 요구사항을 그대로 유지하지 말고, 충돌·과도한 복잡성·근거 부족을 발견하면 수정안을 제시한다.
- 기존 문서의 단순한 표현 변경으로 끝내지 말고, 서로 모순되는 수치·API·데이터 모델·기술 스택·일정·Story Point를 함께 정합화한다.

---

# 2. PawTrail의 최종 제품 방향

PawTrail은 다음과 같이 정의한다.

> **반려견의 상태와 산책 조건을 이해하는 AI Agent가 지도·라우팅·환경 데이터를 활용하여 계단과 과도한 경사를 회피하고, 가능한 범위에서 그늘을 우선하는 개인화 산책 코스를 생성하며, 산책 중 현장 위험 정보를 반영하고 산책 기록을 축적하는 실제 사용 가능한 서비스**

핵심 문제는 기존의 단순한 **“선호 노면을 많이 포함한 코스”**에서 다음으로 확장·재정의한다.

### 핵심 안전 요소

1. **계단 회피**
   - 반려견의 관절 부담을 줄이기 위한 핵심 경로 조건
   - OSM `highway=steps` 등 확인 가능한 지도 데이터를 활용
2. **완만한 경사 우선**
   - DEM 또는 라우팅 API의 고도 정보를 활용
   - 사용자 설정과 반려견 프로필에 따라 허용 경사 수준을 조정
3. **그늘 우선**
   - 산책 시간과 태양 위치를 고려하여 가능한 범위에서 그늘 구간을 우선
   - 건물 높이/형상 데이터가 확보되는 범위에서 그림자 계산
4. **현장 위험 확인**
   - Vision AI로 계단·높은 턱·장애물·공사·위험 요소 등을 확인
   - 사진만으로 실제 지면 온도를 측정한다고 표현하지 않는다.
5. **개인화**
   - 반려견 프로필, 과거 산책, 사용자 피드백을 기억하여 이후 계획에 반영

---

# 3. 절대적으로 지켜야 할 기술적 정정사항

기존 문서에 다음 표현이나 설계가 있으면 반드시 수정한다.

## 3.1 직접 A* GIS 엔진 구현 금지

기존의

> “OSM 그래프를 직접 구축하고 A*로 최적 경로를 계산”

중심 설계를 사용하지 않는다.

권장 구조:

```text
User Request
    ↓
AI Agent
    ↓
Waypoints / Routing Constraints 결정
    ↓
Routing API (ORS / OSRM 등)
    ↓
Candidate Routes
    ↓
Steps / Slope / Shade 분석 및 점수화
    ↓
Agent가 후보 경로 선택
    ↓
최종 Loop Route
```

즉,

> **Agent가 경로 후보와 조건을 결정하고, 전문 Routing API가 실제 도로망 경로를 계산한다.**

라우팅 API를 교체할 수 있도록 Adapter/Tool 계층을 둔다.

---

## 3.2 “계단 100% 식별” 또는 “무계단 100% 보장” 금지

OSM의 `highway=steps`는 **지도 데이터에 등록된 계단을 식별하는 수단**이지 실제 세상의 모든 계단을 보장하는 데이터가 아니다.

따라서 다음 표현은 사용하지 않는다.

- 계단 100% 식별
- 계단 100% 배제 보장
- 무계단 100% 보장
- Zero-Stairs Guaranteed

대신 다음과 같이 표현한다.

- “지도 데이터에서 확인된 계단 구간 회피”
- “확인 가능한 계단 구간을 우선 배제”
- “계단 데이터 신뢰도/출처를 함께 표시”
- “계단 없는 후보 경로가 없을 경우 대체 경로와 제한사항을 안내”

API/DB에도 다음과 같은 구조를 선호한다.

```text
stairs_detected
stairs_data_source
stairs_data_confidence
stairs_avoidance_applied
```

`zero_stairs_guaranteed: bool` 같은 보장형 필드는 사용하지 않는다.

---

## 3.3 경사도는 “평균 경사도”만으로 판단하지 않는다

평균 경사도만 낮아도 특정 구간에 급경사가 존재할 수 있다.

가능하면 다음 정보를 구분한다.

```text
max_slope_percent
average_slope_percent
steep_segment_ratio
slope_data_source
slope_data_confidence
```

사용자 UI에서는 복잡한 숫자를 직접 요구하지 않고 다음과 같은 수준으로 추상화한다.

- 매우 완만
- 완만
- 제한 없음

내부적으로는 프로젝트에서 검증된 경사 기준값으로 변환한다.

---

## 3.4 그늘 계산은 가장 높은 기술 리스크로 취급한다

기존 문서처럼

> “공공 3D 건물 데이터가 있으므로 실시간 그늘을 정확하게 계산할 수 있다”

고 단정하지 않는다.

다음 순서로 구현 가능성을 검증한다.

### Level 1
- 현재 위치
- 날짜/시간
- SunCalc 등 태양 위치 계산
- 확보 가능한 건물 위치/높이 데이터

### Level 2
- 건물 그림자 추정
- 보행 경로 구간과 그림자 영역 교차
- 구간별 예상 그늘 비율 계산

### Level 3
- 수목
- 지형
- 날씨/구름
- 실제 현장 영상
- 고정밀 3D 도시 모델

Level 3은 핵심 제품 기능으로 당연히 포함시키지 않는다.

문서에는 반드시 다음을 구분한다.

```text
계산 가능한 데이터
vs
추정 데이터
vs
현장에서 확인해야 하는 데이터
```

그늘 정보도 가능하면

```text
shade_ratio
shade_estimation_source
shade_confidence
```

형태로 관리한다.

---

## 3.5 그늘과 지면 온도를 동일한 개념으로 취급하지 않는다

Vision AI가 사진을 보고 실제 지면 온도를 측정한다고 표현하지 않는다.

구분:

```text
Vision
→ 현장 시각적 위험요소 분석

Weather / Time / Solar Model
→ 시간대별 열 위험 추정

User Feedback
→ 실제 현장 체감 정보
```

“그늘이 많으므로 지면 온도가 정확히 몇 ℃이다”와 같은 표현은 금지한다.

---

## 3.6 선호 노면은 핵심 안전 조건보다 하위 조건으로 취급

기존의

```text
preferred_surfaces
→ 라우팅의 최우선 조건
```

을 그대로 유지하지 않는다.

권장 우선순위:

```text
1. 통행 가능성
2. 계단 회피
3. 과도한 경사 회피
4. 시간대별 그늘 우선
5. 반려견별 선호/노면 선호
6. 거리·시간·편의성
```

노면 데이터가 없는 구간은 추정값일 수 있으므로 확정 정보처럼 표시하지 않는다.

---

# 4. 라우팅 비용 모델 개정 원칙

기본 개념은 다음과 같이 정리한다.

```text
Cost(segment, time)
=
Length
× Steps Factor
× Slope Factor
× Shade Factor
× Optional Preference Factor
```

## 계단

`avoid_stairs=true`인 경우:

```text
확인된 steps segment → hard constraint / 후보에서 배제
```

단, 모든 후보가 계단을 포함하면 오류를 발생시키지 말고:

```text
1. 무계단 후보 탐색
2. 없으면 가장 적은 제약 위반 후보 탐색
3. 사용자에게 제한사항 명시
```

## 경사

경사는 hard constraint 또는 soft penalty로 분리한다.

```text
사용자/반려견 상태에 따라
max_slope_percent를 제한조건으로 사용
```

## 그늘

그늘은 기본적으로 soft preference로 취급한다.

```text
그늘이 많은 경로 → 비용 감소
직사광선 구간 → 비용 증가
```

단, 데이터 신뢰도가 낮은 경우 과도한 가중치를 적용하지 않는다.

---

# 5. AI Native 구조

PawTrail의 AI Native 핵심 흐름은 다음을 유지한다.

```text
사용자 자연어 / UI 입력
        ↓
LangGraph Agent
        ↓
Dog Context / Memory 조회
        ↓
요구사항 구조화 및 검증
        ↓
Routing Tool
        ├─ Routing API
        ├─ OSM Steps
        ├─ Elevation / DEM
        └─ Shade Estimation
        ↓
Candidate Route 평가
        ↓
Agent 선택 및 설명
        ↓
지도 표시 / 외부 내비게이션
        ↓
산책 기록 / 사용자 피드백
        ↓
Memory 업데이트
```

Agent는 GIS 엔진 자체가 아니다.

Agent의 역할:

- 자연어 이해
- 사용자 조건 구조화
- 반려견 Context 조회
- Tool 선택
- 후보 경로 평가
- 결과 설명
- 예외 상황 대응
- 사용자 피드백 반영

---

# 6. Vision AI 역할 재정의

기존의 “노면 재질 및 온도 진단” 중심 기능을 다음으로 변경한다.

### 주요 기능

- 높은 턱
- 계단
- 보행 장애물
- 공사 구간
- 깨진 유리/날카로운 물체
- 통행 방해 요소
- 안내판/주의 표지
- 반려견 통행 제한 관련 시각 정보

출력 예:

```json
{
  "hazards": [
    {
      "type": "high_curb",
      "severity": "high",
      "confidence": 0.91
    }
  ],
  "route_action": "avoid_recommended",
  "comment": "높은 턱이 확인되어 우회를 권장합니다."
}
```

`surface_type`, `safety_score`가 필요하다면 보조 정보로 사용하되, 단일 점수 하나가 실제 안전성을 완전히 나타내는 것처럼 표현하지 않는다.

---

# 7. GPS / 모바일 UX 원칙

실제 사용 가능한 서비스가 목표이므로 모바일 환경에서 실현 가능한 방식으로 설계한다.

## 기본 원칙

- 모바일 웹/PWA의 백그라운드 GPS를 핵심 기능으로 고정하지 않는다.
- 산책 세션 중 사용자가 화면을 열어 사용하는 Foreground 위치 기록을 우선한다.
- 필요하면 Android Native/Foreground Service는 별도 제품 단계로 분리한다.
- 외부 지도 앱 연동을 적극 활용한다.
- 산책 종료 후 실제 이동 경로와 사용자 피드백을 저장한다.

권장 흐름:

```text
코스 생성
→ 지도 Preview
→ 외부 지도 길찾기
→ 산책 시작
→ Foreground 위치 기록
→ 산책 종료
→ 기록 저장
→ 사용자 피드백
```

---

# 8. API / DB 설계 원칙

## API

핵심 API는 REST 기반으로 설계한다.

불필요한 SSE/WebSocket을 핵심 요구사항으로 만들지 않는다.

예:

```text
POST /api/v1/walk/plan
POST /api/v1/walk/reroute
POST /api/v1/surface/inspect
POST /api/v1/walk/checkin
GET  /api/v1/walk/history
GET  /api/v1/parking/nearby
```

실제 구현 환경에 맞춰 기존 API를 재사용할 수 있으며, 문서 전체에서 endpoint 이름을 일관되게 유지한다.

## DB

최소한 다음 개념을 명확하게 분리한다.

```text
User
Dog
Dog Preferences
Walk Plan
Walk History
Walk Feedback
Surface / Hazard Report
Route Metadata
```

Memory는 처음부터 복잡한 Vector DB를 전제로 하지 않는다.

구조화된 Supabase/PostgreSQL 데이터를 우선 사용하고, 실제 필요성이 확인되는 경우에만 Semantic Memory를 추가한다.

---

# 9. 실제 서비스 품질 및 안전 원칙

PawTrail은 실제 사용 가능한 서비스로 정의하되 다음 표현은 금지한다.

### 금지

- 관절 질환을 치료한다.
- 슬개골 질환을 예방한다.
- 화상을 예방한다.
- 100% 안전하다.
- 100% 무계단이다.
- AI가 수의학적 판단을 내린다.
- 사진만으로 실제 지면 온도를 측정한다.

### 권장

- “관절 부담을 줄이는 산책 조건을 우선 고려”
- “지도 데이터에서 확인된 계단 구간 회피”
- “과도한 경사를 피하는 경로 우선”
- “예상 그늘 구간을 우선”
- “현장 위험요소가 확인되면 우회 권장”
- “AI가 제공하는 정보는 참고용이며 현장 상황을 함께 확인”

---

# 10. 7개 문서별 개정 지침

## 10.1 01_PawTrail_Project_Proposal.md

다음을 전면 재정렬한다.

- 프로젝트 제목/부제를 “노면 재질 중심”에서 “무계단·완만한 경사·그늘 우선” 중심으로 변경
- Pain Point를 `계단 → 과도한 경사 → 직사광선/열 위험 → 현장 장애물 → 반려견별 조건 미반영` 구조로 재정의
- 기존 “흙길 부족”을 핵심 문제에서 제거
- 핵심 기술을 `AI Agent + Routing API + OSM Steps + DEM/Elevation + Shade Estimation + Vision + Memory`로 변경
- 기존 A* 직접 구현 설명 제거
- 데이터 가용성은 “100% 확보”가 아니라 실제 확인된 범위와 한계를 기술
- 실제 사용 가능한 제품임을 명확히 하되 안전을 보장하는 표현은 사용하지 않는다.

## 10.2 02_PawTrail_Team_building.md

팀 구성은 다음 역할을 중심으로 재정의한다.

```text
Member A: AI Agent / Product Logic
Member B: Vision / Multimodal AI
Member C: Backend / Routing / GIS Data
Member D: Frontend / Mobile UX
Member E: Infra / Data / QA
```

각 역할에는 실제 API 연동, 오류 처리, 테스트, 데이터 신뢰도 관리, 보안, 배포, 문서 정합성 책임을 포함한다.

“노면 재질 크롤링”처럼 데이터 확보가 불확실한 작업을 핵심 업무로 두지 않는다.

## 10.3 03_PawTrail_Agile_User_Stories.md

User Story는 단순 번호 수정이 아니라 제품 흐름을 기준으로 재구성한다.

권장 Epic:

```text
Epic A. 산책 조건 입력 및 개인화
Epic B. 무계단·완만한 경사·그늘 우선 경로 생성
Epic C. 지도 표시 및 외부 내비게이션
Epic D. 현장 위험 분석 및 재탐색
Epic E. 산책 기록 및 Memory
Epic F. 기상/열 위험 정보
Epic G. 주차/커뮤니티/부가 서비스
Epic H. 실사용 검증 및 운영
```

핵심 User Story:

- 자연어 산책 요청
- 반려견 프로필
- 계단 회피
- 경사도 선호
- 그늘 우선
- 목표 시간/거리
- 후보 경로 생성
- 경로 지도 표시
- 외부 지도 연동
- 현장 위험 사진 분석
- 위험 구간 우회
- 산책 기록
- 사용자 피드백
- Memory 반영

`preferred_surfaces`는 핵심 안전 조건보다 낮은 우선순위로 조정한다.

또한 다음을 보장 조건으로 사용하지 않는다.

- 계단 통과 0개 보장
- 평균 경사도 5% 이하 절대 보장
- 그늘 70% 이상 보장
- 선호 노면 50% 이상 보장

Acceptance Criteria는 실제 데이터의 불확실성을 반영한다.

## 10.4 04_PawTrail_Architecture_Design.md

Architecture는 반드시 다음 구조를 표현한다.

```text
Next.js / PWA
    ↓
FastAPI REST
    ↓
LangGraph Agent
    ↓
Tool Layer
 ├─ Routing Adapter
 ├─ Elevation/Slope Analyzer
 ├─ Steps Detector
 ├─ Shade Estimator
 ├─ Vision Inspector
 ├─ Memory Tool
 └─ Parking / Weather Tool
    ↓
Supabase / External APIs
```

핵심 변경:

- 직접 A* 엔진 제거
- Routing API Adapter 추가
- Steps / Slope / Shade 분석 계층 분리
- route candidate scoring 계층 추가
- 데이터 source/confidence 필드 추가
- Vision과 heat-risk 모델 분리
- REST API 기준 유지
- Foreground GPS 기준
- DB/Memory를 지나치게 복잡하게 만들지 않는다.

## 10.5 05_PawTrail_Detailed_Implementation_Plan.md

권장 5주 구현 순서:

### Week 1
- 개발환경
- Auth
- Supabase
- 기본 Agent
- Routing API 연결
- 기본 지도 표시

### Week 2
- Dog Profile / Memory
- Steps 데이터
- Elevation / Slope 분석
- 경로 후보 평가

### Week 3
- Shade Estimation
- Vision
- 위험 구간 재탐색
- Frontend 통합

### Week 4
- GPS 산책 기록
- Weather / heat-risk
- Parking / 부가 기능
- 실사용 테스트

### Week 5
- 오류 수정
- 보안
- 성능
- UX
- 사용자 피드백 반영
- 배포/운영 문서

5주는 “MVP 완성”이 아니라 **실제 사용 가능한 1차 제품 버전의 구현·검증 기간**으로 표현한다.

## 10.6 06_PawTrail_Task_Breakdown_and_Estimations.md

기존 공수와 Story Point를 그대로 유지하지 않는다.

특히 직접 A*, OSM 그래프 구축, 실시간/백그라운드 GPS, 복잡한 그림자 연산, Vision+Routing 실시간 결합 등의 숨은 복잡도를 다시 평가한다.

각 Task는:

```text
개발
+ 외부 API 연동
+ 데이터 검증
+ 오류 처리
+ 테스트
+ 통합
+ 배포
```

를 포함하여 추정한다.

반드시 재추정할 핵심 작업:

1. Routing API Adapter
2. OSM Steps 데이터 처리
3. Elevation/Slope 분석
4. Shade Estimation
5. Candidate Route Scoring
6. Vision Hazard Detection
7. Rerouting
8. Foreground GPS
9. Supabase Memory
10. Weather/Heat Risk
11. Mobile UX
12. E2E 테스트
13. 배포 및 운영

**기존 292h를 유지하기 위해 작업량을 축소하지 않는다.**

## 10.7 07_PawTrail_Presentation_Pain_Points.md

발표자료는 다음 흐름으로 정렬한다.

```text
1. 반려견 산책의 실제 문제
   ↓
2. 계단/경사/직사광선/현장 장애물
   ↓
3. 기존 지도 서비스의 한계
   ↓
4. PawTrail의 데이터 융합 방식
   ↓
5. AI Agent가 조건을 이해하고 경로를 선택
   ↓
6. 현장 Vision → 위험 확인 → 우회
   ↓
7. 산책 기록 → Memory → 다음 산책 개인화
```

“100% 무계단”, “정확한 실시간 지면 온도”, “AI 질환 진단”, “모든 계단 자동 발견”, “모든 그늘 정확 계산” 등의 표현은 사용하지 않는다.

실제 구현된 기술과 발표 메시지가 일치하도록 한다.

---

# 11. 데이터 신뢰도 원칙

모든 문서에서 다음을 구분한다.

## ① 관측/공식 데이터

예:
- 공공 API
- OSM 태그
- DEM
- 사용자 GPS

## ② 계산/추정 데이터

예:
- 경사도 계산
- 건물 그림자 추정
- 예상 그늘 비율
- 예상 열 위험

## ③ AI 분석 데이터

예:
- Vision 위험요소
- 안내판 판독
- 자연어 의도 분석

②와 ③을 공식 사실처럼 표현하지 않는다.

가능하면 결과 객체에 다음 메타데이터를 포함한다.

```text
source
confidence
observed_at
estimated
```

---

# 12. 문서 간 정합성 관리

다음 항목은 7개 문서에서 일관되게 표현되어야 한다.

| 변경 항목 | 01 기획 | 02 팀 | 03 US | 04 아키텍처 | 05 구현 | 06 Task | 07 발표 |
|---|---|---|---|---|---|---|---|
| 계단 회피 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 경사도 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 그늘 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Routing API | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Vision 위험 분석 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Foreground GPS | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Memory | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Weather/Heat Risk | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

하나의 문서에만 존재하는 핵심 기술/기능이 있다면 정합성 검토 대상이다.

---

# 13. Gemini Code Assist 작업 절차

## Step 1. 전체 문서 읽기

7개 문서를 모두 읽고 다음을 추출한다.

- 프로젝트 목적
- 핵심 사용자
- User Story
- Story Point
- 기술 스택
- API
- DB
- 외부 서비스
- 일정
- 담당자
- 발표 메시지

## Step 2. 충돌 목록 작성

```text
항목 | 현재 정의 | 문제 | 수정 방향 | 영향 문서
```

형식으로 먼저 정리한다.

## Step 3. 기준 문서 결정

기본 순서는:

```text
Project Proposal
→ User Stories
→ Architecture
→ Implementation Plan
→ Task Breakdown
→ Team Building
→ Presentation
```

단, Architecture가 User Story의 기술적 충돌을 발견하면 User Story까지 함께 수정한다.

## Step 4. 핵심 데이터 모델 정합성 확인

다음 개념이 문서마다 다르게 정의되지 않았는지 확인한다.

```text
DogProfile
WalkPlanRequest
RouteSegment
WalkPlanResponse
WalkHistory
Feedback
HazardReport
```

## Step 5. 기술 구현 가능성 검토

각 기능에 대해:

```text
실제 데이터가 있는가?
API가 실제 존재하는가?
정확도/커버리지 한계는 무엇인가?
5주 내 구현 가능한가?
운영 비용은 감당 가능한가?
모바일에서 실제 동작하는가?
오류 상황을 처리하는가?
```

를 검토한다.

## Step 6. 문서 수정

권장 순서:

```text
01 Project Proposal
→ 03 User Stories
→ 04 Architecture
→ 05 Implementation Plan
→ 06 Task Breakdown
→ 02 Team Building
→ 07 Presentation
```

## Step 7. 최종 정합성 검사

- 동일 기능의 이름이 같은가?
- API endpoint가 같은가?
- DTO 필드가 같은가?
- Story Point와 Task가 일치하는가?
- 일정과 Task가 일치하는가?
- 담당자가 일치하는가?
- 발표 내용이 실제 구현 내용과 일치하는가?
- 과장된 안전 보장 표현이 없는가?
- 실제 데이터와 추정 데이터를 구분했는가?

---

# 14. 구현 가능성 검증 원칙

요구사항이 기술적으로 위험하거나 비현실적이면 그대로 확정하지 않는다.

다음 형식으로 제안한다.

```text
[문제]
현재 요구사항:
...

[영향]
Frontend / Backend / GIS / AI / DB / Infra

[위험]
...

[권장 대안]
...

[문서 영향]
01 / 03 / 04 / 05 / 06 / 07
```

특히 다음을 검토한다.

- 데이터가 실제로 확보 가능한가?
- 지도 데이터의 커버리지가 충분한가?
- 외부 API 호출량/비용은 감당 가능한가?
- 그늘 계산의 정확도가 요구수준을 만족하는가?
- 모바일 브라우저에서 동작 가능한가?
- 사용자가 이해하기 쉬운 결과를 제공하는가?

---

# 15. 실제 서비스 기준의 Definition of Done

기능을 “완료”로 표시하려면 코드가 존재하는 것만으로 판단하지 않는다.

```text
[ ] 실제 API 또는 실제 DB 연결
[ ] 정상 입력 동작
[ ] 잘못된 입력 처리
[ ] 외부 API 실패 처리
[ ] 데이터 없음 처리
[ ] 위치 권한 거부 처리
[ ] 네트워크 오류 처리
[ ] 모바일 화면 검증
[ ] 보안 검증
[ ] 로그/오류 추적
[ ] 단위 테스트
[ ] 통합/E2E 테스트
[ ] 기존 기능 회귀 확인
[ ] 사용자에게 이해 가능한 오류 메시지
[ ] 문서/API/환경변수 갱신
```

Mock은 테스트나 외부 API 장애 대비용으로만 사용한다.

핵심 사용자 흐름을 Mock 데이터만으로 완성된 것으로 간주하지 않는다.

---

# 16. 절대 하지 말아야 할 것

- 기존 문구만 바꾸고 아키텍처를 그대로 두는 것
- 직접 A* GIS 엔진을 새로 만드는 것
- OSM의 계단 데이터가 현실의 모든 계단을 포함한다고 가정하는 것
- 건물 높이 데이터가 모든 지역에서 동일하게 제공된다고 가정하는 것
- 그늘 계산 정확도를 검증하지 않고 정밀 수치처럼 제시하는 것
- 사진으로 실제 지면 온도를 측정한다고 주장하는 것
- AI 분석을 수의학적 진단으로 표현하는 것
- 백그라운드 GPS를 모바일 웹의 필수 기능으로 고정하는 것
- SSE/WebSocket을 필요 이상으로 도입하는 것
- 기존 292h를 유지하기 위해 작업량을 축소해서 기록하는 것
- 5명 사용자 테스트 결과를 전체 사용자에 대한 AI 정확도로 일반화하는 것
- API Key를 Frontend에 노출하는 것
- 사용자 위치를 필요 이상으로 저장하는 것
- 오류를 무시하고 정상 결과로 처리하는 것
- 최신 기술이라는 이유만으로 안정적인 기술을 교체하는 것
- 실제 구현하지 않은 기능을 발표자료에서 구현된 것처럼 표현하는 것

---

# 17. 최종 출력 형식

Gemini Code Assist가 문서 개정을 완료한 후 다음을 출력한다.

## 1. 개정 요약

```text
- 프로젝트 정의 변경
- 핵심 User Story 변경
- Architecture 변경
- 구현계획 변경
- Task/공수 변경
- 발표 메시지 변경
```

## 2. 주요 설계 변경

`기존 → 변경` 형식의 표로 제공한다.

## 3. 구현 리스크

상위 5개를 다음 형식으로 제공한다.

```text
Risk
Impact
Mitigation
```

## 4. 문서 정합성 결과

7개 문서 각각에 대해:

```text
문서명 | 수정 여부 | 핵심 변경 | 정합성 확인
```

을 제공한다.

## 5. 남은 검증 과제

실제 개발 전에 반드시 확인해야 할 외부 데이터/API/성능/모바일 환경 검증 항목을 별도로 정리한다.

---

# 18. 핵심 원칙 한 줄 요약

> **PawTrail은 “노면 재질을 많이 포함하는 AI 산책 앱”이 아니라, 반려견의 상태와 산책 조건을 이해한 AI Agent가 실제 지도·라우팅·환경 데이터를 조합하여 계단과 과도한 경사를 회피하고 가능한 범위에서 그늘을 우선하는 산책 경로를 생성하고, 현장 피드백을 다시 개인화 맥락으로 축적하는 실제 사용 가능한 서비스로 설계한다.**
