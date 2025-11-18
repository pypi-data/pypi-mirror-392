from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import requests

from ..core.base import BaseChat, BaseEmbedding


class _HTTPClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.extra_headers = extra_headers or {}

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.extra_headers)
        return headers

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise RuntimeError(f"HTTP {resp.status_code} POST {url}: {detail}")
        return resp.json()


class ChatOpenAICompat(BaseChat):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 30.0,
        extra_headers: Optional[Dict[str, str]] = None,
        **_: Any,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        self._client = _HTTPClient(base_url=base_url, api_key=api_key, timeout=timeout, extra_headers=extra_headers)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(self, messages: List[Dict[str, str]]) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        # Assume base_url already includes version (e.g., /v1 or /v4)
        # So just append endpoint path consistently
        data = self._client.post("/chat/completions", payload)
        # normalize both /v1 and base variations
        choice = data.get("choices", [{}])[0]
        message = choice.get("message") or choice.get("delta") or {}
        return message.get("content", "")


class EmbeddingsOpenAICompat(BaseEmbedding):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 30.0,
        extra_headers: Optional[Dict[str, str]] = None,
        **_: Any,
    ) -> None:
        super().__init__(api_key=api_key, base_url=base_url, model=model, timeout=timeout)
        self._client = _HTTPClient(base_url=base_url, api_key=api_key, timeout=timeout, extra_headers=extra_headers)
        self.model = model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        payload: Dict[str, Any] = {"model": self.model, "input": texts}
        # Assume base_url already includes version (e.g., /v1 or /v4)
        data = self._client.post("/embeddings", payload)
        vectors: List[List[float]] = []
        for item in data.get("data", []):
            vectors.append(item.get("embedding", []))
        return vectors


