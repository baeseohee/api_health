
import json
import requests
import os

INVENTORY_PATH = "data/api_inventory.json"

def load_apis():
    if not os.path.exists(INVENTORY_PATH):
        return []
    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

apis = load_apis()
if not apis:
    print("No APIs found")
    exit()

# Pick one GET and one POST
target_api = None
for api in apis:
    if api['method'] == 'GET' and 'naver.com' in api['url']:
        target_api = api
        break

if target_api:
    print(f"Testing GET: {target_api['url']}")
    try:
        response = requests.request(
            method=target_api['method'],
            url=target_api['url'],
            headers=target_api['headers'],
            data=target_api['request_body'],
            timeout=5
        )
        print("Status:", response.status_code)
        print("Body prefix:", response.text[:200])
    except Exception as e:
        print("Error:", e)

# Pick a POST if exists
post_api = None
for api in apis:
    if api['method'] == 'POST':
        post_api = api
        break

if post_api:
    print(f"\nTesting POST: {post_api['url']}")
    print(f"Request Body: {post_api['request_body']}")
    try:
        response = requests.request(
            method=post_api['method'],
            url=post_api['url'],
            headers=post_api['headers'],
            data=post_api['request_body'],
            timeout=5
        )
        print("Status:", response.status_code)
        try:
            print("Response JSON:", response.json())
        except:
            print("Response Text prefix:", response.text[:200])
    except Exception as e:
        print("Error:", e)
