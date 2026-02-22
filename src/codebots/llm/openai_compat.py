from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass

from codebots.llm.base import LLMClient, LLMError


@dataclass
class OpenAICompatClient(LLMClient):
    """OpenAI-compatible Chat Completions client.

    This is intentionally minimal and uses stdlib `urllib` to avoid extra dependencies.
    It should work with any provider that implements an OpenAI-compatible
    `/v1/chat/completions` endpoint.

    Required environment/config:
    - api_key via env var (see config.llm.api_key_env)
    - base_url (e.g., https://api.openai.com)
    - model (e.g., gpt-4.1-mini, etc.)
    """

    base_url: str
    model: str
    api_key_env: str = "CODEBOTS_API_KEY"
    timeout_s: int = 120

    def complete(self, prompt: str) -> str:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise LLMError(f"Missing API key in env var {self.api_key_env}")

        url = self.base_url.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"Request failed: {e}") from e

        try:
            parsed = json.loads(raw)
            return parsed["choices"][0]["message"]["content"]
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"Unexpected response shape. Raw: {raw[:1000]}") from e
