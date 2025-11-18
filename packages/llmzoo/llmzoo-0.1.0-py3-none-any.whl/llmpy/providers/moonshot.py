from __future__ import annotations

from typing import Any, Optional

from .openai_compat import ChatOpenAICompat, EmbeddingsOpenAICompat


MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"


class MoonshotChat(ChatOpenAICompat):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "moonshot-v1-8k",
        base_url: str = MOONSHOT_BASE_URL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 30.0,
        **config: Any,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            **config,
        )


class MoonshotEmbedding(EmbeddingsOpenAICompat):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "text-embedding-3-small",
        base_url: str = MOONSHOT_BASE_URL,
        timeout: float = 30.0,
        **config: Any,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url,
            timeout=timeout,
            **config,
        )


