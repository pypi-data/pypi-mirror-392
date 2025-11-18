from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.base import BaseVectorStore


class MilvusLiteVectorStore(BaseVectorStore):
    def __init__(
        self,
        *,
        collection_name: str,
        dim: int,
        uri: str,
        metric_type: str = "L2",
        index_type: str = "IVF_FLAT",
        nlist: int = 1024,
        nprobe: int = 16,
        **config: Any,
    ) -> None:
        super().__init__(
            collection_name=collection_name,
            dim=dim,
            uri=uri,
            metric_type=metric_type,
            index_type=index_type,
            nlist=nlist,
            nprobe=nprobe,
            **config,
        )
        try:
            from pymilvus import MilvusClient  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            raise ImportError("pymilvus is required. Install with `pip install llmpy[milvus]`." ) from exc

        if not uri:
            raise ValueError("uri is required and must be non-empty for Milvus Lite.")
        if not collection_name:
            raise ValueError("collection_name is required and must be non-empty.")
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError("dim must be a positive integer.")

        self._client = MilvusClient(uri=uri)
        self._collection_name = collection_name
        self._dim = dim
        # create collection if not exists
        if not self._client.has_collection(collection_name):
            self._client.create_collection(
                collection_name=collection_name,
                dimension=dim,
                metric_type=metric_type,
            )
            self._client.create_index(
                collection_name=collection_name,
                index_params={
                    "index_type": index_type,
                    "metric_type": metric_type,
                    "params": {"nlist": nlist},
                },
            )

        self._nprobe = nprobe

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        *,
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
    ) -> List[str]:
        if ids is None:
            # let milvus assign auto ids when ids not provided (but lite client often requires ids)
            ids = [str(i) for i in range(self.count(), self.count() + len(embeddings))]
        data = {"vector": embeddings}
        if metadatas:
            data.update({k: [m.get(k) for m in metadatas] for k in metadatas[0].keys()})
        self._client.insert(collection_name=self._collection_name, data=data, ids=ids)
        return ids

    def similarity_search_by_vector(self, query_vector: List[float], *, k: int = 5) -> List[Dict[str, Any]]:
        res = self._client.search(
            collection_name=self._collection_name,
            data=[query_vector],
            limit=k,
            search_params={"metric_type": self.get("metric_type", "L2"), "params": {"nprobe": self.get("nprobe", 16)}},
            output_fields=["*"]
        )
        results: List[Dict[str, Any]] = []
        hits = res[0] if res else []
        for hit in hits:
            item = {
                "id": str(hit.get("id") or hit.get("pk") or hit.get("primary_key")),
                "distance": hit.get("distance"),
                "metadata": {k: v for k, v in hit.items() if k not in {"id", "pk", "primary_key", "distance", "vector"}},
                "document": None,
            }
            results.append(item)
        return results

    def delete(self, ids):  # type: ignore[override]
        self._client.delete(collection_name=self._collection_name, ids=ids)

    def count(self) -> int:  # type: ignore[override]
        try:
            info = self._client.get_collection_stats(collection_name=self._collection_name)
            return int(info.get("row_count", 0))
        except Exception:
            return 0

    def persist(self) -> None:  # type: ignore[override]
        return None


