import os
import sys
import requests

url=os.getenv("APP_URL","").rstrip("/")
if not url:
    print("Falta APP_URL, por ejemplo https://miapp.onrender.com")
    sys.exit(2)

try:
    r=requests.get(url + "/ping", timeout=30)
    print("PING", r.status_code, r.text[:120])
    r.raise_for_status()
except Exception as e:
    print("PING ERROR:", e)
    sys.exit(1)
