import requests
from datetime import datetime


def send_teams_notification(teams_webhook_url: str, job_name: str, results: list[str]):
    """Send Adaptive Card summary to Teams."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    failed = [r.split(" -> ")[0] for r in results if "FAILED" in r]

    if failed:
        color, message = "Attention", f"Failed tables: {', '.join(failed)}"
    else:
        color, message = "Good", "All tables ingested successfully ✅"

    payload = {
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "size": "Medium", "weight": "Bolder",
                     "text": f"{job_name} - Import Job Report"},
                    {"type": "TextBlock", "text": f"Executed at {current_time}", "wrap": True},
                    {"type": "TextBlock", "text": message, "wrap": True, "color": color}
                ]
            }
        }]
    }

    try:
        r = requests.post(teams_webhook_url, json=payload, timeout=10)
        if r.status_code == 202:
            print(f"✅ Teams notification sent for {job_name}")
        else:
            print(f"❌ Teams notification failed [{r.status_code}] {r.text}")
    except Exception as e:
        print(f"⚠️ Teams webhook error in {job_name}: {e}")
