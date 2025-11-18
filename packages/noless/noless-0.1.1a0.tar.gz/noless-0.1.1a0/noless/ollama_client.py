"""Utilities for talking to a local Ollama server."""

from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Optional

import requests


class OllamaClientError(Exception):
    """Raised when an Ollama request fails."""


class OllamaClient:
    """Simple HTTP client for the Ollama REST API.

    The client intentionally keeps the surface area small – we only expose
    endpoints that the CLI currently needs (listing models and generating text).
    """

    def __init__(self, host: Optional[str] = None, timeout: int = 300):
        self.base_url = (host or os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def is_available(self) -> bool:
        """Return True if the Ollama server responds to a quick ping."""
        try:
            _ = self.list_models()
            return True
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """Return all models reported by the local Ollama instance."""
        response = self._request("get", "/api/tags")
        payload = response.json()
        return [model.get("name", "") for model in payload.get("models", []) if model.get("name")]

    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        temperature: float = 0.2,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate text with the specified model.

        The method requests a non-streaming response so that the CLI can parse
        the complete payload as JSON.
        """
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        if system:
            payload["system"] = system

        if options:
            payload["options"].update(options)

        response = self._request("post", "/api/generate", json=payload)
        data = response.json()
        return data.get("response", "").strip()

    def chat(self, model: str, messages: List[Dict[str, str]], *, options: Optional[Dict[str, Any]] = None) -> str:
        """Minimal chat endpoint wrapper."""
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options

        response = self._request("post", "/api/chat", json=payload)
        data = response.json()
        return data.get("message", {}).get("content", "").strip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:  # pragma: no cover - network errors
            raise OllamaClientError(f"Ollama request failed: {exc}") from exc


def pretty_json(payload: Dict[str, Any]) -> str:
    """Utility helper used across the CLI for debugging."""
    return json.dumps(payload, indent=2, ensure_ascii=False)
