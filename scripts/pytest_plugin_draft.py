import pytest
import json
import time

class JSONReportPlugin:
    def __init__(self, inventory):
        self.results = []
        self.inventory = inventory
        self.start_times = {}

    def pytest_runtest_protocol(self, item, nextitem):
        self.start_times[item.nodeid] = time.time()
        return None

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            duration = report.duration
            # Match report to inventory item based on parameter index
            # This is a bit tricky with parametrization, but we can access item.callspec.params
            
            # Since we can't easily get the 'api' object back from just the report object strictly without hacking,
            # We will rely on the order or reconstruction. 
            # Better approach: The test item has 'funcargs' but report doesn't directly.
            # But wait, we are in a plugin class instance that persists.
            pass

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        
        if report.when == "call":
            api_data = item.callspec.params.get("api_data", {})
            
            # Capture captured stdout/stderr if any (for debugging)
            # We need to perform the request again? NO. We need to capture the response data.
            # Pytest doesn't easily let us pass objects out from test function to report.
            # Workaround: Use `record_property` fixture in the test, or simpler:
            # For now, let's just record pass/fail status and duration.
            # To get Request/Response body, we really should execute the request inside the test function 
            # and append to a global/shared results list, OR use a custom fixture.

            # Let's use a simpler approach: The test_dynamic.py will populate a shared list.
            pass

# Simpler approach: Create a robust runner script that invokes pytest and parses the output, 
# OR use a custom script that IS the test runner.

# Let's rewrite the runner to use pytest programmatically but handle results explicitly.
