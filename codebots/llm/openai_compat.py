from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import TypeVar
from pydantic import BaseModel

from .provider import LLMResponse

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMHTTPError(Exception):
    pass


@dataclass(frozen=True)
class OpenAICompatProvider:
    base_url: str
    model: str
    api_key_env: str
    timeout_seconds: float = 60.0
    name: str = "openai_compat"

    def _headers(self) -> dict[str, str]:
        key = os.environ.get(self.api_key_env, "")
        if not key:
            raise LLMHTTPError(f"Missing API key env var: {self.api_key_env}")
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def chat(self, system: str, user: str) -> LLMResponse:
        url = self.base_url.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), headers=self._headers(), method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise LLMHTTPError(str(e)) from e

        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage")
        return LLMResponse(text=text, usage=usage)

    def chat_json(self, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        # Ask model for strict JSON and validate.
        instruction = (
            "Return ONLY valid JSON that matches this schema. Do not include markdown.\n"
            f"Schema: {schema.model_json_schema()}"
        )
        resp = self.chat(system, user + "\n\n" + instruction)
        # Best-effort parse (strip common wrappers)
        txt = resp.text.strip()
        if txt.startswith("```"):
            txt = txt.strip("`")
        try:
            obj = json.loads(txt)
        except Exception as e:
            raise LLMHTTPError(f"JSON parse failed: {e}\nRaw:\n{resp.text[:2000]}") from e
        return schema.model_validate(obj)
