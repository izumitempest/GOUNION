import requests
import json

try:
    response = requests.get("http://127.0.0.1:8001/posts/?limit=1")
    response.raise_for_status()
    data = response.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
