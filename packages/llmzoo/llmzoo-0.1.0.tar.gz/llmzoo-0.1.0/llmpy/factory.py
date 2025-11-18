from typing import Any, Dict

from .providers.zhipu import ZhipuChat, ZhipuEmbedding
from .providers.moonshot import MoonshotChat, MoonshotEmbedding
from .providers.bedrock import BedrockChat, BedrockEmbedding
from .vectorstores.chroma import ChromaVectorStore
from .vectorstores.milvus_lite import MilvusLiteVectorStore
from .vectorstores.pgvector import PgVectorVectorStore
from .vectorstores.elasticsearch import ElasticsearchVectorStore
from .vectorstores.opensearch import OpenSearchVectorStore


CHAT_PROVIDERS = {
    "zhipu": ZhipuChat,
    "moonshot": MoonshotChat,
    "bedrock": BedrockChat,
}

EMBEDDING_PROVIDERS = {
    "zhipu": ZhipuEmbedding,
    "moonshot": MoonshotEmbedding,
    "bedrock": BedrockEmbedding,
}

VECTOR_STORES = {
    "chroma": ChromaVectorStore,
    "milvus-lite": MilvusLiteVectorStore,
    "pgvector": PgVectorVectorStore,
    "elasticsearch": ElasticsearchVectorStore,
    "opensearch": OpenSearchVectorStore,
}


def build_chat(provider: str, /, **config: Dict[str, Any]):
    cls = CHAT_PROVIDERS.get(provider)
    if cls is None:
        raise ValueError(f"Unknown chat provider: {provider}")
    return cls(**config)


def build_embedding(provider: str, /, **config: Dict[str, Any]):
    cls = EMBEDDING_PROVIDERS.get(provider)
    if cls is None:
        raise ValueError(f"Unknown embedding provider: {provider}")
    return cls(**config)


def build_vector_store(backend: str, /, **config: Dict[str, Any]):
    cls = VECTOR_STORES.get(backend)
    if cls is None:
        raise ValueError(f"Unknown vector store: {backend}")
    return cls(**config)


