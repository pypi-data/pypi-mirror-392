from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.base import BaseVectorStore


class OpenSearchVectorStore(BaseVectorStore):
    def __init__(
        self,
        *,
        hosts: List[str],
        index: str,
        dim: int,
        method: str = "hnsw",  # "hnsw" or "ivf" depending on plugin
        space_type: str = "cosinesimil",  # cosinesimil | l2 | innerproduct
        m: int = 16,
        ef_construction: int = 128,
        ef_search: int = 64,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **config: Any,
    ) -> None:
        if not hosts or not isinstance(hosts, list):
            raise ValueError("hosts must be a non-empty list, e.g. ['https://...:9200']")
        if not index:
            raise ValueError("index is required and must be non-empty for OpenSearch.")
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError("dim must be a positive integer.")

        super().__init__(hosts=hosts, index=index, dim=dim, method=method, space_type=space_type, m=m, ef_construction=ef_construction, ef_search=ef_search, **config)

        try:
            from opensearchpy import OpenSearch  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            raise ImportError("opensearch-py is required. Install with `pip install llmpy[opensearch]`.") from exc

        http_auth = (username, password) if username and password else None
        self._os = OpenSearch(hosts, http_auth=http_auth)
        self._index = index
        self._dim = dim
        self._space_type = space_type
        self._ef_search = ef_search

        # ensure index with knn mapping
        if not self._os.indices.exists(index=self._index):
            mapping = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.m": m,
                        "knn.algo_param.ef_construction": ef_construction,
                    }
                },
                "mappings": {
                    "properties": {
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": self._dim,
                            "method": {
                                "name": method,
                                "space_type": space_type,
                                "engine": "nmslib"
                            }
                        },
                        "metadata": {"type": "object", "enabled": True},
                        "document": {"type": "text"},
                    }
                }
            }
            self._os.indices.create(index=self._index, body=mapping)

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        *,
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
    ) -> List[str]:
        if ids is None:
            ids = [str(i) for i in range(self.count(), self.count() + len(embeddings))]
        metadatas = metadatas or [None] * len(embeddings)
        documents = documents or [None] * len(embeddings)
        for i, emb in enumerate(embeddings):
            doc = {"embedding": emb, "metadata": metadatas[i], "document": documents[i]}
            self._os.index(index=self._index, id=ids[i], body=doc, refresh=True)
        return ids

    def similarity_search_by_vector(self, query_vector: List[float], *, k: int = 5) -> List[Dict[str, Any]]:
        body = {
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_vector,
                        "k": k,
                    }
                }
            },
            "_source": ["metadata", "document"],
        }
        res = self._os.search(index=self._index, body=body)
        hits = res.get("hits", {}).get("hits", [])
        results: List[Dict[str, Any]] = []
        for h in hits:
            results.append({
                "id": h.get("_id"),
                "metadata": (h.get("_source", {}).get("metadata")),
                "document": (h.get("_source", {}).get("document")),
                "distance": h.get("_score"),
            })
        return results

    def delete(self, ids):  # type: ignore[override]
        for _id in ids:
            try:
                self._os.delete(index=self._index, id=_id, refresh=True)
            except Exception:
                pass

    def count(self) -> int:  # type: ignore[override]
        try:
            res = self._os.count(index=self._index)
            return int(res.get("count", 0))
        except Exception:
            return 0



