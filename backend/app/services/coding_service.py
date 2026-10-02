import os

import httpx


class Judge0Client:
    def __init__(self):
        self.api_url = os.getenv("JUDGE0_API_URL", "https://judge0-ce.p.rapidapi.com")
        self.api_key = os.getenv("JUDGE0_API_KEY", "")
        self.host = os.getenv("JUDGE0_HOST", "judge0-ce.p.rapidapi.com")

    def execute(self, source_code: str, language_id: int, stdin: str = ""):
        if not self.api_key:
            raise RuntimeError("Judge0 API key is not configured. Set JUDGE0_API_KEY in your environment.")

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host,
            "content-type": "application/json",
        }
        payload = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin,
        }
        response = httpx.post(f"{self.api_url}/submissions?base64_encoded=false&wait=true", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
