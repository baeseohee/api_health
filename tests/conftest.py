import pytest
import requests
import json
import os
import time

# Global list to store full results including bodies
msg_queue = []

def pytest_sessionstart(session):
    # Clear temp file if exists
    if os.path.exists("data/health_check_results_pytest.json"):
        os.remove("data/health_check_results_pytest.json")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        # Extract API data from the test item
        api_data = item.callspec.params.get("api_data", {})
        
        # Check if we attached extra info to the item (we will do this in the test function)
        response_info = getattr(item, "response_info", {})
        
        result_entry = {
            "method": api_data.get("method"),
            "url": api_data.get("url"),
            "status_code": response_info.get("status_code"),
            "success": report.passed,
            "response_time": round(report.duration, 3), # Duration of the test call phase
            "request_body": api_data.get("request_body"),
            "response_body": response_info.get("response_body"),
            "error": str(report.longrepr) if report.failed else None,
            "short_error": str(report.longrepr.reprcrash.message) if report.failed and hasattr(report.longrepr, "reprcrash") else None,
            "result": response_info.get("result_msg")
        }
        
        # Save to a temporary file or append to list
        # Since plugins run in the same process, we can write to a file incrementally
        with open("data/health_check_results_pytest.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(result_entry) + "\n")

    
def pytest_sessionfinish(session, exitstatus):
    # Consolidate results
    full_results = []
    if os.path.exists("data/health_check_results_pytest.json"):
        with open("data/health_check_results_pytest.json", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    full_results.append(json.loads(line))
    
    # Write final JSON array
    with open("data/health_check_results.json", "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)
    
    # Clean up temp file
    if os.path.exists("data/health_check_results_pytest.json"):
        os.remove("data/health_check_results_pytest.json")
