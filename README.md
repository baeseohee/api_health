
# API Health Check Automation

## 프로젝트 개요
사용자 여정 로그(HAR 파일)를 분석하여 API를 자동으로 식별하고 상태 모니터링을 자동화하는 도구입니다. 실제 네트워크 트래픽에서 테스트 케이스를 생성함으로써 수동 API 문서 관리의 필요성을 제거하고, 빠르고 정확하게 서버 상태를 점검할 수 있습니다.

## 주요 기능
*   **HAR 파일 파싱 및 분석**: 브라우저 네트워크 로그(.har)에서 API 요청을 자동으로 추출하고 정적 리소스(이미지, CSS 등)를 필터링합니다.
*   **지능형 API 인벤토리**: 중복 URL 중에서도 실제 Payload(요청 본문)가 있는 유의미한 요청을 우선적으로 선별하여 테스트 케이스를 생성합니다.
*   **자동화된 헬스 체크**: 생성된 인벤토리를 기반으로 `Pytest`를 통해 동적으로 API 상태를 검사합니다.
*   **직관적인 웹 대시보드**:
    *   **Drag & Drop 업로드**: 간편하게 HAR 파일을 업로드할 수 있습니다.
    *   **Postman 스타일 UI**: 개발자에게 친숙한 인터페이스로 요청/응답 본문을 상세히 확인할 수 있습니다.
    *   **상세 디버깅**: 성공/실패 여뿐만 아니라, Status Code 범위 검증 결과와 에러 로그까지 시각적으로 제공합니다.

## 프로젝트 구조
```bash
api_health_check/
├── app.py                 # FastAPI 메인 서버
├── requirements.txt       # 프로젝트 의존성 라이브러리
├── data/                  # 데이터 저장 폴더 (Git 제외 권장)
│   ├── api_inventory.json # 추출된 API 목록
│   └── health_check_results.json # 테스트 결과
├── config/
│   └── settings.json      # 필터링 설정 (제외 확장자 등)
├── scripts/
│   └── processor.py       # HAR 파싱 및 처리 엔진
├── tests/
│   ├── test_dynamic.py    # 동적 Pytest 테스트 러너
│   └── conftest.py        # 테스트 결과 캡처 및 후처리 로직
└── static/                # 웹 프론트엔드 리소스
    ├── index.html
    ├── app.js
    └── style.css
```

## 설치 및 실행 방법

### 1. 필수 요구사항
*   Python 3.8 이상
*   Chrome 브라우저 (HAR 파일 추출용)

### 2. 설치
```bash
# 저장소 복제
git clone https://github.com/QA-kim/API_health_check.git
cd API_health_check

# 의존성 설치
pip install -r requirements.txt
```

### 3. 실행
```bash
# 서버 시작
python3 app.py
```
서버가 시작되면 브라우저에서 `http://localhost:8000` 으로 접속합니다.

### 4. 사용법
1.  **HAR 파일 준비**: 
    *   Chrome 브라우저에서 검사가 필요한 웹사이트에 접속합니다.
    *   `F12`를 눌러 개발자 도구를 엽니다.
    *   `Network` 탭으로 이동한 뒤, 원하는 동작(로그인, 검색 등)을 수행합니다.
    *   네트워크 리스트 우측 상단의 다운로드 아이콘(`Export HAR...`)을 클릭하여 파일을 저장합니다.
2.  **업로드 및 실행**:
    *   웹 대시보드(`http://localhost:8000`)에 HAR 파일을 드래그하여 업로드합니다.
    *   "Run Health Check" 버튼을 클릭합니다.
3.  **결과 확인**:
    *   테스트 진행 상황이 로딩 바로 표시됩니다.
    *   완료 후, 각 API별 성공(Pass)/실패(Fail) 여부와 상세 Request/Response 내용을 확인합니다.

## 기술 스택
*   **Backend**: FastAPI, Python
*   **Testing**: Pytest, Requests
*   **Frontend**: Vanilla JavaScript, CSS (Dark Mode Design)

## 라이선스
This project is licensed under the MIT License.