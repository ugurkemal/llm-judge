from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .models import Answer


class DecisionAPIError(RuntimeError):
    pass


def _parse_answer(raw: dict) -> Answer:
    kind = raw.get("type")
    if kind == "noul":
        return Answer(float(raw["noul"]), raw.get("confidence"))
    if kind == "score":
        return Answer(float(raw["score"]), raw.get("confidence"), raw.get("probabilities"))
    raise DecisionAPIError(f"Unsupported answer type: {kind!r}")


class OllamaBackend:
    """tev1 (or another System One model) on a local Ollama (POST {host}/v1/systemone).

    Env: OLLAMA_HOST (default http://localhost:11434), OLLAMA_MODEL (default tev1).
    """

    def __init__(self, host: str | None = None, model: str | None = None, timeout: float = 120):
        self.host = (host or os.environ.get("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        if not self.host.startswith("http"):
            self.host = f"http://{self.host}"
        self.model = model or os.environ.get("OLLAMA_MODEL", "tev1")
        self.timeout = timeout

    def ask(self, state: Any, questions: dict[str, dict]) -> dict[str, Answer]:
        body = json.dumps({"model": self.model, "state": state, "questions": questions}).encode()
        req = urllib.request.Request(
            f"{self.host}/v1/systemone",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise DecisionAPIError(f"Ollama returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise DecisionAPIError(f"Couldn't reach Ollama: {exc.reason}") from exc
        answers = payload.get("answers")
        if not isinstance(answers, dict):
            raise DecisionAPIError("Response has no 'answers' object")
        return {name: _parse_answer(a) for name, a in answers.items()}
