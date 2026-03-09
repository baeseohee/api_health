import json
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

class APIHealthChecker:
    def __init__(self, inventory_path='data/api_inventory.json'):
        self.inventory_path = inventory_path
        self.timeout = 10 # Default timeout in seconds
        self.auth_token = os.getenv('API_AUTH_TOKEN')
        self.api_key = os.getenv('API_KEY')

    def load_inventory(self):
        if not os.path.exists(self.inventory_path):
            print(f"Error: Inventory file {self.inventory_path} not found.")
            return []
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run_checks(self):
        inventory = self.load_inventory()
        if not inventory:
            return

        results = []
        print(f"Starting health check for {len(inventory)} APIs...\n")

        for item in inventory:
            method = item.get('method')
            url = item.get('url')
            
            # Prepare headers
            headers = item.get('headers', {})
            if self.auth_token:
                headers['Authorization'] = f"Bearer {self.auth_token}"
            if self.api_key:
                headers['X-API-KEY'] = self.api_key

            # Prepare request body
            request_body = item.get('request_body')

            start_time = time.time()
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=request_body,
                    timeout=self.timeout
                )
                duration = round(time.time() - start_time, 3)
                status_code = response.status_code
                is_success = 200 <= status_code < 300
                
                try:
                    resp_body = response.json()
                except:
                    resp_body = response.text

                results.append({
                    "method": method,
                    "url": url,
                    "status_code": status_code,
                    "success": is_success,
                    "response_time": duration,
                    "request_body": request_body,
                    "response_body": resp_body,
                    "error": None
                })
                
                status_symbol = "✅" if is_success else "❌"
                print(f"{status_symbol} {method} {url} - Status: {status_code} ({duration}s)")

            except requests.exceptions.Timeout:
                print(f"❌ {method} {url} - Status: TIMEOUT")
                results.append({
                    "method": method,
                    "url": url,
                    "status_code": None,
                    "success": False,
                    "response_time": None,
                    "error": "Timeout"
                })
            except Exception as e:
                print(f"❌ {method} {url} - Error: {str(e)}")
                results.append({
                    "method": method,
                    "url": url,
                    "status_code": None,
                    "success": False,
                    "response_time": None,
                    "error": str(e)
                })

        self.save_results(results)

    def save_results(self, results):
        output_path = 'data/health_check_results.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count
        
        print(f"\n--- Health Check Summary ---")
        print(f"Total: {len(results)}")
        print(f"Success: {success_count}")
        print(f"Failure: {fail_count}")
        print(f"Detailed results saved to {output_path}")

if __name__ == "__main__":
    checker = APIHealthChecker()
    checker.run_checks()
