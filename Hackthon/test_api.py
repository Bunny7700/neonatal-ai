import requests
import json

try:
    response = requests.get('http://127.0.0.1:5001/api/dashboard', timeout=5)
    print("STATUS CODE:", response.status_code)
    text = response.text
    print("RAW TEXT SNIPPET:", text[:200], "...", text[-200:])
    
    # Try parsing manually
    data = json.loads(text)
    print("JSON PARSED SUCCESSFULLY!")
except Exception as e:
    print("ERROR:", str(e))
