# API 헬스 체크 자동화 프로젝트

## 1. 프로젝트 개요
**목표**: 사용자 여정 로그(HAR 파일)를 분석하여 API를 자동으로 식별하고 상태 모니터링을 자동화합니다.
**핵심 가치**: 실제 네트워크 트래픽에서 테스트 케이스를 생성함으로써 수동 API 문서 관리의 필요성을 제거합니다.
**현재 상태**: **상용 수준 프로토타입** (웹 기반 대시보드 + Pytest 엔진).

## 2. 시스템 아키텍처

### 2.1 기술 스택
- **백엔드 프레임워크**: FastAPI (Python 3.8+)
- **테스트 엔진**: Pytest
- **HTTP 클라이언트**: Requests
- **프론트엔드**: Vanilla JS + CSS (모던 다크 모드 / Postman 스타일 UI)
- **데이터 포맷**: JSON (인벤토리 및 결과 저장)

### 2.2 작동 흐름
1.  **수집 (Ingest)**: 사용자가 웹 대시보드를 통해 `.har` 파일을 업로드합니다.
2.  **처리 (Process)**: `HARProcessor`가 파일을 파싱하고, 정적 리소스(이미지, CSS 등)를 필터링하며 API 엔드포인트를 정규화합니다.
    - *로직*: 빈 요청보다는 Body가 있는 API 요청을 우선하여 테스트 품질을 확보합니다.
3.  **생성 (Generate)**: 분석된 API 목록이 `data/api_inventory.json`에 저장됩니다.
4.  **실행 (Execute)**: FastAPI가 서브프로세스를 통해 `pytest`를 실행합니다.
    - `tests/test_dynamic.py`: 인벤토리의 각 항목에 대해 동적으로 테스트 케이스를 생성합니다.
    - `tests/conftest.py`: 테스트 실행 결과를 실시간으로 훅(Hook)하여 상태, 응답 시간, Body 등을 캡처합니다.
5.  **보고 (Report)**: 결과가 `data/health_check_results.json`으로 집계되어 대시보드에 렌더링됩니다.

## 3. 기능 요구사항

### 1단계: 데이터 수집 및 처리 (완료)
- [x] **HAR 파일 파싱**: 표준 HAR 파일에서 HTTP 요청 추출.
- [x] **노이즈 필터링**: 정적 자산(png, jpg, css, js, woff 등) 자동 제외.
- [x] **중복 제거**: 중복 URL 처리 시 Payload(본문)가 있는 요청을 우선순위로 두는 지능형 처리.
- [x] **화이트/블랙리스트**: `config/settings.json`을 통한 도메인 필터링 설정.

### 2단계: 실행 엔진 (완료 - Pytest 통합)
- [x] **동적 테스트 생성**: 인벤토리 파일을 기반으로 Pytest 케이스 자동 생성.
- [x] **표준 검증**:
    - 상태 코드 검사 (200-299 범위).
    - 응답 시간 측정.
    - 네트워크 연결 및 타임아웃 처리.
- [x] **Payload 재생**: 원본 HAR 로그의 `POST`/`PUT` 본문을 정확하게 재현.

### 3단계: 웹 대시보드 및 리포팅 (완료)
- [x] **인터랙티브 UI**: 파일 드래그 앤 드롭 업로드.
- [x] **시각적 리포팅**: 
    - Postman 스타일의 다크 테마.
    - 메서드별 컬러 코딩 (GET=초록, POST=주황 등).
    - 성공/실패 상태 배지.
- [x] **상세 검사**:
    - 행을 확장하여 전체 Request 및 Response Body 확인 기능.
    - JSON 문법 하이라이팅 및 포맷팅.
    - 원클릭 클립보드 복사.
    - HTML 응답 렌더링 방지를 위한 이스케이프 처리.

### 4단계: 추후 로드맵 (To-Do)
- [ ] **인증 처리**: HAR 토큰 만료 시, 검사 실행 전 재인증(토큰 갱신) 로직 지원.
- [ ] **고급 검증**: 사용자 정의 성공 기준(예: "응답 본문에 'success' 포함") 설정 기능.
- [ ] **히스토리 및 추세**: API 안정성을 시간대별로 추적하기 위한 결과 저장.
- [ ] **CI/CD 통합**: Jenkins/GitHub Actions 연동을 위한 JUNIT 포맷 결과 내보내기.
- [ ] **알림 (Alerting)**: 실패 시 Slack/이메일 알림 발송.

## 4. 프로젝트 구조
```
api_health_check/
├── app.py                 # 메인 FastAPI 웹 서버
├── requirements.txt       # 의존성 라이브러리 목록
├── data/                  # 데이터 저장소 (Git 제외)
│   ├── api_inventory.json
│   └── health_check_results.json
├── config/
│   └── settings.json      # 필터링 및 환경 설정
├── scripts/
│   └── processor.py       # 핵심 HAR 처리 로직
├── tests/
│   ├── test_dynamic.py    # Pytest 동적 테스트 생성기
│   └── conftest.py        # 결과 캡처용 Pytest 훅 설정
└── static/                # 프론트엔드 자산
    ├── index.html
    ├── app.js
    └── style.css
```

## 5. 사용 가이드
1. **서버 시작**: `python3 app.py` (http://localhost:8000 접속)
2. **HAR 업로드**: Chrome 개발자 도구 Network 탭에서 저장한 HAR 파일을 드래그 앤 드롭.
3. **검사 실행**: "Run Health Check" 버튼 클릭.
4. **결과 분석**: 성공/실패 상태를 확인하고 상세 내용을 펼쳐서 디버깅.
