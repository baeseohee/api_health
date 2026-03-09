import requests
import json
from datetime import datetime

class TeamsNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_report(self, results):
        if not self.webhook_url:
            print("Warning: No Teams Webhook URL provided.")
            return

        total = len(results)
        passed = sum(1 for r in results if r.get('success'))
        failed = total - passed
        
        # Color: Good (Green) if 0 fails, else Attention (Red)
        theme_color = "00FF00" if failed == 0 else "FF0000"
        status_text = "All Systems Operational" if failed == 0 else f"{failed} Issues Detected"

        # Build Fact Set for Summary
        facts = [
            {"name": "Total APIs", "value": str(total)},
            {"name": "Passed", "value": str(passed)},
            {"name": "Failed", "value": str(failed)},
            {"name": "Timestamp", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ]

        # Build Section for Failed Items
        sections = [{
            "activityTitle": "API Health Check Summary",
            "activitySubtitle": status_text,
            "facts": facts,
            "markdown": True
        }]

        if failed > 0:
            failed_items = [r for r in results if not r.get('success')]
            # Limit to top 5 failures to avoid huge messages
            display_limit = 5
            failed_text = "**Failed APIs (Top 5):**\n\n"
            
            for item in failed_items[:display_limit]:
                failed_text += f"- [{item.get('status_code', 'ERR')}] {item.get('method')} {item.get('url')}\n"
                if item.get('error'):
                    failed_text += f"  - Error: {item.get('error')}\n"
            
            if failed > display_limit:
                failed_text += f"\n...and {failed - display_limit} more."

            sections.append({
                "text": failed_text,
                "markdown": True
            })

        # Construct Message Card payload
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": theme_color,
            "summary": "API Health Check Result",
            "sections": sections
        }

        try:
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            print("Teams notification sent successfully.")
        except Exception as e:
            print(f"Failed to send Teams notification: {str(e)}")
