import json
import os
from urllib.parse import urlparse, urlunparse

class HARProcessor:
    def __init__(self, config_path='config/settings.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
    def is_api_call(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Check extensions
        for ext in self.config.get('excluded_extensions', []):
            if path.endswith(ext):
                return False
        
        # Check whitelist domains if any
        whitelist = self.config.get('whitelist_domains', [])
        if whitelist:
            domain = parsed_url.netloc
            if domain not in whitelist:
                return False
                
        return True

    def normalize_url(self, url):
        parsed = urlparse(url)
        # Remove query and fragment for normalization
        normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        return normalized

    def process(self, har_file_path):
        print("DEBUG: version 2 running")
        if not os.path.exists(har_file_path):
            print(f"Error: {har_file_path} not found.")
            return

        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)

        entries = har_data.get('log', {}).get('entries', [])
        api_inventory = {}

        for entry in entries:
            request = entry.get('request', {})
            url = request.get('url')
            method = request.get('method')
            
            if self.is_api_call(url):
                normalized_url = self.normalize_url(url)
                key = f"{method} {normalized_url}"
                
                # Enhanced logic: if key exists but current one has body and old one doesn't, update it
                should_update = False
                
                # Check for postData
                post_data = request.get('postData', {})
                req_text = post_data.get('text')
                
                # If text is empty, try to construct from params
                if not req_text and 'params' in post_data:
                    params = post_data['params']
                    # params is a list of {name, value}
                    # We can convert this to a dict or a query string? 
                    # Usually better to keep as string representation for consistency
                    import urllib.parse
                    param_pairs = {}
                    for p in params:
                        param_pairs[p['name']] = p.get('value', '')
                    
                    # If mimeType suggests form data, encode it
                    mime_type = post_data.get('mimeType', '')
                    if 'application/x-www-form-urlencoded' in mime_type:
                        req_text = urllib.parse.urlencode(param_pairs)
                    elif 'application/json' in mime_type:
                        req_text = json.dumps(param_pairs)
                    else:
                         # Fallback to just dumping the dict or string
                         req_text = json.dumps(param_pairs)
                
                if key not in api_inventory:
                    should_update = True
                else:
                    # If existing entry has no body but new one does, upgrade it
                    existing_body = api_inventory[key].get('request_body')
                    if not existing_body and req_text:
                        should_update = True

                if should_update:
                    api_inventory[key] = {
                        "method": method,
                        "url": normalized_url,
                        "headers": self.extract_relevant_headers(request.get('headers', [])),
                        "request_body": req_text,
                        "original_url": url 
                    }

        output_path = self.config.get('output_file', 'data/api_inventory.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        inventory_list = list(api_inventory.values())
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(inventory_list, f, indent=2, ensure_ascii=False)
            
        print(f"Processed {len(entries)} entries. Found {len(inventory_list)} unique API endpoints.")
        print(f"Inventory saved to {output_path}")

    def extract_relevant_headers(self, headers):
        # We might want to keep Content-Type or Auth headers for future use in Phase 3
        relevant_keys = ['content-type', 'authorization', 'x-api-key']
        extracted = {}
        for h in headers:
            name = h.get('name').lower()
            if name in relevant_keys:
                extracted[name] = h.get('value')
        return extracted

if __name__ == "__main__":
    import sys
    processor = HARProcessor()
    # If a file is passed as argument, process it
    if len(sys.argv) > 1:
        processor.process(sys.argv[1])
    else:
        print("Usage: python scripts/processor.py <path_to_har_file>")
