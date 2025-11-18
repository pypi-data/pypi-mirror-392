from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional


class BaseConfigurable(ABC):
    def __init__(self, **config: Any) -> None:
        self._config: Dict[str, Any] = dict(config) if config else {}

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)


class BaseEmbedding(BaseConfigurable, ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_text(self, text: str) -> List[float]:
        vectors = self.embed_texts([text])
        return vectors[0] if vectors else []


class BaseChat(BaseConfigurable, ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError

    def complete(self, prompt: str) -> str:
        return self.chat([{"role": "user", "content": prompt}])


class BaseVectorStore(BaseConfigurable, ABC):
    @abstractmethod
    def add_embeddings(
        self,
        embeddings: List[List[float]],
        *,
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
    ) -> List[str]:
        raise NotImplementedError

    def add_texts(
        self,
        texts: List[str],
        *,
        embeddings: List[List[float]],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        return self.add_embeddings(
            embeddings,
            ids=ids,
            metadatas=metadatas,
            documents=texts,
        )

    @abstractmethod
    def similarity_search_by_vector(
        self, query_vector: List[float], *, k: int = 5
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def delete(self, ids: Iterable[str]) -> None:  # optional
        raise NotImplementedError

    def count(self) -> int:  # optional
        raise NotImplementedError

    def persist(self) -> None:  # optional
        pass


