from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.base import BaseVectorStore


class ElasticsearchVectorStore(BaseVectorStore):
    def __init__(
        self,
        *,
        hosts: List[str],
        index: str,
        dim: int,
        similarity: str = "cosine",  # "cosine" | "l2_norm" | "dot_product"
        num_candidates: int = 100,
        **config: Any,
    ) -> None:
        if not hosts or not isinstance(hosts, list):
            raise ValueError("hosts must be a non-empty list of host URLs, e.g. ['http://localhost:9200']")
        if not index:
            raise ValueError("index is required and must be non-empty for Elasticsearch.")
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError("dim must be a positive integer.")

        super().__init__(hosts=hosts, index=index, dim=dim, similarity=similarity, num_candidates=num_candidates, **config)

        try:
            from elasticsearch import Elasticsearch  # type: ignore
            from elasticsearch.exceptions import NotFoundError  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            raise ImportError("elasticsearch is required. Install with `pip install llmpy[es]`.") from exc

        self._es = Elasticsearch(hosts)
        self._index = index
        self._dim = dim
        self._similarity = similarity
        self._num_candidates = num_candidates

        # ensure index with mapping
        if not self._es.indices.exists(index=self._index):
            mapping = {
                "mappings": {
                    "properties": {
                        "embedding": {
                            "type": "dense_vector",
                            "dims": self._dim,
                            "index": True,
                            "similarity": self._similarity,
                        },
                        "metadata": {"type": "object", "enabled": True},
                        "document": {"type": "text"},
                    }
                }
            }
            self._es.indices.create(index=self._index, **mapping)

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

        actions = []
        for i, emb in enumerate(embeddings):
            doc = {"embedding": emb, "metadata": metadatas[i], "document": documents[i]}
            actions.append({"index": {"_index": self._index, "_id": ids[i]}})
            actions.append(doc)
        # bulk
        body_lines: List[str] = []
        for a in actions:
            body_lines.append(__import__("json").dumps(a))
        body = "\n".join(body_lines) + "\n"
        resp = self._es.bulk(body=body)
        if resp.get("errors"):
            raise RuntimeError(f"Elasticsearch bulk indexing had errors: {resp}")
        try:
            self._es.indices.refresh(index=self._index)
        except Exception:
            pass
        return ids

    def similarity_search_by_vector(self, query_vector: List[float], *, k: int = 5) -> List[Dict[str, Any]]:
        body = {
            "knn": {
                "field": "embedding",
                "query_vector": query_vector,
                "k": k,
                "num_candidates": max(k, self._num_candidates),
            },
            "_source": ["metadata", "document"],
        }
        res = self._es.search(index=self._index, body=body)
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
        actions = []
        for _id in ids:
            actions.append({"delete": {"_index": self._index, "_id": _id}})
        if actions:
            body_lines = [__import__("json").dumps(a) for a in actions]
            self._es.bulk(body="\n".join(body_lines) + "\n")

    def count(self) -> int:  # type: ignore[override]
        try:
            res = self._es.count(index=self._index)
            return int(res.get("count", 0))
        except Exception:
            return 0


