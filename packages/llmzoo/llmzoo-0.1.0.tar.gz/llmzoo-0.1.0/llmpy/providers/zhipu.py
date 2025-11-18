from __future__ import annotations

from typing import Any, Dict, List, Optional

from .openai_compat import ChatOpenAICompat, EmbeddingsOpenAICompat


ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"


class ZhipuChat(ChatOpenAICompat):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "glm-4",
        base_url: str = ZHIPU_BASE_URL,
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


class ZhipuEmbedding(EmbeddingsOpenAICompat):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "embedding-2",
        base_url: str = ZHIPU_BASE_URL,
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


