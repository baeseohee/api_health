# API Health Check Automation Project

## 1. Project Overview
**Objective**: Automate the discovery and health monitoring of APIs by analyzing user user-journey logs (HAR files).
**Core Value**: Eliminate the need for manual API documentation maintenance by generating test cases directly from actual network traffic.
**Current Status**: **Production-Ready Prototype** (Web-based Dashboard + Pytest Engine).

## 2. System Architecture

### 2.1 Technology Stack
- **Backend Framework**: FastAPI (Python 3.8+)
- **Test Engine**: Pytest (with `pytest-xdist` capability)
- **HTTP Client**: Requests
- **Frontend**: Vanilla JS + CSS (Modern Dark Mode / Postman-like UI)
- **Data Format**: JSON (Inventory & Results)

### 2.2 Workflow
1.  **Ingest**: User uploads a `.har` file via the Web Dashboard.
2.  **Process**: `HARProcessor` parses the file, filters static resources (images, css, js), and normalizes API endpoints.
    - *Logic*: Prefers API calls with Request Bodies over empty ones to ensure test quality.
3.  **Generate**: API Inventory is saved to `data/api_inventory.json`.
4.  **Execute**: FastAPI triggers a subprocess to run `pytest`.
    - `tests/test_dynamic.py`: Dynamically generates a test case for each API entry in the inventory.
    - `tests/conftest.py`: Hooks into the test execution to capture real-time results (Status, Duration, Request/Response Bodies).
5.  **Report**: Results are aggregated into `data/health_check_results.json` and rendered on the Dashboard.

## 3. Functional Requirements

### Phase 1: Data Ingestion & Processing (Completed)
- [x] **HAR File Parsing**: Extract HTTP requests from standard HAR files.
- [x] **Noise Filtering**: Automatically exclude static assets (png, jpg, css, js, woff, etc.).
- [x] **Deduplication**: Intelligent handling of duplicate URLs (prioritizing requests with payloads).
- [x] **Whitelist/Blacklist**: Configurable domain filtering via `config/settings.json`.

### Phase 2: Execution Engine (Completed - Pytest Integrated)
- [x] **Dynamic Test Generation**: Automatically create Pytest cases based on the inventory file.
- [x] **Standard Validations**:
    - Status Code Check (200-299 Range).
    - Response Time Measurement.
    - Network Connectivity / Timeout handling.
- [x] **Payload Replay**: Accurately replay `POST`/`PUT` bodies from the original HAR log.

### Phase 3: Web Dashboard & Reporting (Completed)
- [x] **Interactive UI**: Drag-and-drop file upload.
- [x] **Visual Reporting**: 
    - Postman-style Dark Theme.
    - Color-coded methods (GET=Green, POST=Orange, etc.).
    - Pass/Fail status badges.
- [x] **Detailed Inspection**:
    - Expandable rows to view full Request and Response bodies.
    - JSON Syntax Formatting.
    - One-click Copy to Clipboard.
    - HTML Escaping to prevent rendering issues with web responses.

### Phase 4: Future Roadmap (To-Do)
- [ ] **Authentication Handling**: Support for re-authenticating (getting new tokens) before running checks, as HAR tokens expire.
- [ ] **Advanced Assertions**: Allow users to define custom success criteria (e.g., "Response body must contain 'success'").
- [ ] **History & Trends**: Save historical results to track API stability over time.
- [ ] **CI/CD Integration**: Export Pytest results in JUNIT format for Jenkins/GitHub Actions.
- [ ] **Alerting**: Slack/Email notifications on failure.

## 4. Project Structure
```
api_health_check/
├── app.py                 # Main FastAPI Web Server
├── requirements.txt       # Dependencies
├── data/                  # Data storage (ignored by git)
│   ├── api_inventory.json
│   └── health_check_results.json
├── config/
│   └── settings.json      # Filtering & Configuration
├── scripts/
│   └── processor.py       # Core HAR processing logic
├── tests/
│   ├── test_dynamic.py    # Pytest dynamic test generator
│   └── conftest.py        # Pytest hooks for result capturing
└── static/                # Frontend Assets
    ├── index.html
    ├── app.js
    └── style.css
```

## 5. Usage Guide
1. **Start Server**: `python3 app.py` (Runs on http://localhost:8000)
2. **Upload HAR**: Drag & drop a HAR file from Chrome DevTools Network tab.
3. **Run Check**: Click "Run Health Check".
4. **Analyze**: Review pass/fail status and inspect bodies for debugging.