# [계획서] 앱 백엔드 Firebase 전환 및 아키텍처·생명주기 문서 개선 계획

본 계획서는 PawTrail의 모바일 앱 백엔드 및 데이터 영속성 계층을 기존 **Supabase(PostgreSQL)**에서 **Firebase(Firebase Auth, Cloud Firestore, Cloud Storage, Cloud Functions/FCM)**로 전면 전환하고, 이에 따른 아키텍처 및 전 생명주기 문서(01, 03, 04, 05, 06, 08)를 일관되게 고도화하는 실행 계획을 정의합니다.

---

## 1. 전환 배경 및 아키텍처 개선 방향

### 1.1 Firebase 도입의 주요 이점
1. **React Native (Expo) 최적의 모바일 BaaS 연동**: `@react-native-firebase` 및 Firebase JS SDK를 통한 빠르고 안정적인 모바일 클라이언트 통합.
2. **Cloud Firestore의 실시간 동기화 & 강력한 오프라인 지속성**:
   - Firestore의 오프라인 캐시 기능이 기본 지원되므로 **US-15(통신 음영지역 산책 유지 및 오프라인 캐시)**를 별도 복잡한 로컬 DB 동기화 엔진 없이도 매끄럽게 충족.
   - **실시간 리스너(`onSnapshot`)**를 통해 커뮤니티 피드(US-09) 및 후기 사진 갱신을 실시간 반영.
3. **Firebase Cloud Storage**: 공원 종합안내판 원본 사진(US-04) 및 완주 노면 제보 사진(US-05)을 보안 규칙(Security Rules) 기반으로 안전하게 업로드 및 서빙.
4. **Firebase Cloud Messaging (FCM)**: n8n 지면열 워크플로우(US-12)와 연계하여 35℃ 이하 골든타임 모바일 푸시 알림을 네이티브로 지원.

### 1.2 시스템 아키텍처 구조 (하이브리드 백엔드 구성)
* **모바일 앱 백엔드 (BaaS Tier)**:
  - **Firebase Authentication**: 익명 로그인, 소셜(구글) 로그인, 견주 식별 토큰 발급.
  - **Cloud Firestore (NoSQL)**: 사용자/반려견 프로필, 산책 기록, 커뮤니티 피드, 즐겨찾기, 노면 제보 데이터 관리.
  - **Cloud Storage**: 안내판 및 노면 후기 이미지 버킷.
  - **Firebase Security Rules**: 사용자별 데이터 격리 및 RLS 대체.
* **AI & 공간 라우팅 엔진 (AI/GIS Tier)**:
  - **FastAPI / Cloud Run (또는 Firebase Cloud Functions for Python v2)**: LangGraph ReAct Agent, GeoPandas 토지피복 공간 결합, NetworkX/OSRM 루프 경로 생성, Gemini 1.5 Flash 비전 판독.
  - 모바일 앱은 Firebase Auth 토큰을 헤더에 담아 AI 라우팅 엔드포인트(`POST /api/routes/agent-plan`)를 호출.

---

## 2. 사용자 검토 필요 사항 (User Review Required)

> [!IMPORTANT]
> **NoSQL 문서 모델(Firestore) 전환에 따른 변경점**
> 1. 기존 PostgreSQL 관계형 스키마(외래키 제약조건)가 Cloud Firestore의 **컬렉션(Collection) - 문서(Document) 계층 구조**로 개편됩니다.
>    - `users/{userId}`: 사용자 프로필
>    - `users/{userId}/dogs/{dogId}`: 반려견 프로필 및 관절 케어 설정
>    - `walk_history/{walkId}`: 산책 완주 기록 및 노면 달성률 (경로 GeoJSON 포함)
>    - `community_feed/{feedId}`: 개인정보 마스킹된 공개 산책 코스 및 별점 후기
>    - `users/{userId}/favorites/{favId}`: 나만의 안심 코스 즐겨찾기
>    - `surface_reports/{reportId}`: 공원 안내판 및 커뮤니티 노면 제보
> 2. 전체 개발 공수(**334h**) 및 스토리 포인트(**62pt**)는 태스크 내용만 Firebase 도메인으로 최신화하고 규모는 그대로 유지합니다.

---

## 3. 문서별 상세 변경 계획 (Proposed Changes)

### Component 1: 기획 및 사용자 스토리
* #### [MODIFY] [01_PawTrail_Project_Proposal.md](file:///d:/코디세이/PawTrail/docs/01_PawTrail_Project_Proposal.md)
  - 4.2 시스템 아키텍처 및 기술 스택: `Supabase(PostgreSQL)` ➔ `Firebase (Auth, Cloud Firestore, Cloud Storage)`로 변경.
  - 기능 명세 및 검증 체계의 Supabase 데이터베이스 참조를 Cloud Firestore로 갱신.
* #### [MODIFY] [03_PawTrail_Agile_User_Stories.md](file:///d:/코디세이/PawTrail/docs/03_PawTrail_Agile_User_Stories.md)
  - US-06(반려견 프로필/산책 이력): Supabase Memory ➔ Firebase Firestore 기반 프로필 영속 저장 및 조회.
  - US-08(핸즈프리 길안내): 산책 완료 인포그래픽 리포트의 Firestore `walk_history` 컬렉션 저장.
  - US-09(커뮤니티 피드): 마스킹 처리된 경로의 Firestore `community_feed` 컬렉션 적재.
  - US-14(나만의 코스): Supabase RLS ➔ Firestore Security Rules 기반 `users/{userId}/favorites` 저장.
  - US-15(오프라인 지도 캐시): Firestore의 내장 Offline Persistence 기능과 연계하여 오프라인 연속성 보장 명시.

### Component 2: 아키텍처 및 시스템 설계
* #### [MODIFY] [04_PawTrail_Architecture_Design.md](file:///d:/코디세이/PawTrail/docs/04_PawTrail_Architecture_Design.md)
  - 2.1 시스템 블록 다이어그램: `Data & Persistence Tier`를 `Firebase (Auth, Cloud Firestore, Cloud Storage, FCM)`로 전면 개편.
  - 3.5 데이터베이스 및 영속성 계층:
    - 기존 관계형 ERD를 **Cloud Firestore NoSQL 컬렉션/문서 스키마 구조 다이어그램**으로 교체.
    - `users`, `dogs`, `walk_history`, `feedback`, `favorites`, `surface_reports`의 JSON/문서 스키마 명세.
    - **Firestore Security Rules** 및 **Storage Security Rules** 선언적 보안 가드레일 추가.
  - 4. 핵심 시퀀스 워크플로우: `Supabase Memory` ➔ `Firebase Cloud Firestore` 상호작용으로 갱신.
  - 5. DevOps / 인프라 명세표: `Database & Auth`를 `Firebase (GCP)`로 갱신.

### Component 3: 상세 일정, 작업 분할, 추적표 동기화
* #### [MODIFY] [05_PawTrail_Detailed_Implementation_Plan.md](file:///d:/코디세이/PawTrail/docs/05_PawTrail_Detailed_Implementation_Plan.md)
  - Sprint 1 (Week 2) 및 Sprint 2 (Week 3~4) 마일스톤: Supabase 프로비저닝/DDL ➔ Firebase 프로젝트 생성, Firestore 컬렉션 초기화 및 Security Rules 설정으로 갱신.
* #### [MODIFY] [06_PawTrail_Task_Breakdown_and_Estimations.md](file:///d:/코디세이/PawTrail/docs/06_PawTrail_Task_Breakdown_and_Estimations.md)
  - **TASK-06-1**: Supabase DDL ➔ Cloud Firestore 컬렉션 스키마 및 인덱스 설계 (4h)
  - **TASK-06-2**: Firestore CRUD 및 Firebase Admin SDK 연동 (6h)
  - **TASK-08-4**: 완주 인포그래픽의 Firestore 저장 연동 (6h)
  - **TASK-09-3**: 피드백/피드 데이터 Firestore 저장 및 좌표 마스킹 (6h)
  - **TASK-14-1**: `favorites` 하위 컬렉션 CRUD 및 Security Rules (5h)
  - **TASK-15-1**: Firestore Offline Persistence 활성화 및 오프라인 캐시 연동 (5h)
* #### [MODIFY] [08_PawTrail_Traceability_Matrix.md](file:///d:/코디세이/PawTrail/docs/08_PawTrail_Traceability_Matrix.md)
  - Section 2, 3, 5의 DB 엔터티 및 아키텍처 모듈 표에서 Supabase 항목을 Cloud Firestore 컬렉션 및 Firebase 서비스로 전면 동기화.

---

## 4. 검증 계획 (Verification Plan)

### 4.1 정합성 자동 검사
* ripgrep(`grep_search`)을 실행하여 `docs` 폴더 내 모든 핵심 산출물(01, 03, 04, 05, 06, 08)에서 이전 스택(`Supabase`) 잔존 여부 전수 검사 (오래된 백업 폴더 제외).
* 사용자 스토리(03), 아키텍처(04), 구현 계획(05), 작업 분할(06), 추적표(08) 간의 컬렉션명, API 명칭, 공수(334h), 스토리포인트(62pt) 일치 검증.

### 4.2 사용자 승인 절차
* 본 계획서에 대한 사용자 검토 및 승인 후 위 6개 문서에 대한 변경 작업을 순차적으로 일괄 적용합니다.
