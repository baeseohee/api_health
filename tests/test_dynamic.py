import pytest
import requests
import json
import os

# Load API Inventory
INVENTORY_PATH = os.environ.get("API_INVENTORY", "data/api_inventory.json")

def load_apis():
    if not os.path.exists(INVENTORY_PATH):
        return []
    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

apis = load_apis()

class TestDynamicAPI:
    @pytest.mark.parametrize("api_data", apis)
    def test_api_health(self, api_data, request):
        """
        Dynamically run health check for each API in inventory.
        """
        method = api_data.get("method")
        url = api_data.get("url")
        headers = api_data.get("headers", {})
        request_body = api_data.get("request_body")

        # Inject Auth if needed
        auth_token = os.getenv('API_AUTH_TOKEN')
        if auth_token:
            headers['Authorization'] = f"Bearer {auth_token}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=request_body,
                timeout=10
            )
            
            # Capture Response Body
            try:
                resp_body = response.json()
            except:
                resp_body = response.text

            # Prepare result message
            if 200 <= response.status_code < 400:
                result_msg = f"PASS: Status {response.status_code} is within valid range [200, 400)."
            else:
                result_msg = f"FAIL: Status {response.status_code} is NOT within valid range [200, 400)."

            request.node.response_info = {
                "status_code": response.status_code,
                "response_body": resp_body,
                "result_msg": result_msg
            }

            # Assertion
            assert 200 <= response.status_code < 400, f"Failed with status {response.status_code}"
            
        except Exception as e:
            # Attach error metadata even if it fails before response
            request.node.response_info = {
                "status_code": None,
                "response_body": str(e),
                "result_msg": f"ERROR: Exception occurred - {str(e)}"
            }
            raise e
