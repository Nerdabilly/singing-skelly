
import httpx

try:
    response = httpx.put(
        "http://127.0.0.1:8001/v1/player/resume",  # ⬅️ Replace with your real URL
        
        timeout=5.0
    )
    print(f"[HTTP] PUT status: {response.status_code}")
except httpx.RequestError as e:
    print(f"[HTTP ERROR] {e}")
