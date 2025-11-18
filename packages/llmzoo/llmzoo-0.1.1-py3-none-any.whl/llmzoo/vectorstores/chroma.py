from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.base import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    def __init__(
        self,
        *,
        collection_name: str,
        persist_path: Optional[str] = None,
        **config: Any,
    ) -> None:
        if not collection_name:
            raise ValueError("collection_name is required and must be non-empty for Chroma.")
        super().__init__(collection_name=collection_name, persist_path=persist_path, **config)
        try:
            import chromadb  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            raise ImportError("chromadb is required. Install with `pip install llmpy[chroma]`." ) from exc
        if persist_path:
            self._client = chromadb.PersistentClient(path=persist_path)
        else:
            self._client = chromadb.Client()
        self._collection = self._client.get_or_create_collection(name=collection_name)

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
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )
        return ids

    def similarity_search_by_vector(self, query_vector: List[float], *, k: int = 5) -> List[Dict[str, Any]]:
        res = self._collection.query(query_embeddings=[query_vector], n_results=k)
        results: List[Dict[str, Any]] = []
        for i in range(len(res.get("ids", [[]])[0])):
            item = {
                "id": res["ids"][0][i],
                "distance": None,  # Chroma returns distances under different keys/version; omit here
                "metadata": (res.get("metadatas", [[None]])[0][i] if res.get("metadatas") else None),
                "document": (res.get("documents", [[None]])[0][i] if res.get("documents") else None),
            }
            results.append(item)
        return results

    def delete(self, ids):  # type: ignore[override]
        self._collection.delete(ids=ids)

    def count(self) -> int:  # type: ignore[override]
        try:
            return self._collection.count()
        except Exception:
            return 0

    def persist(self) -> None:  # type: ignore[override]
        # PersistentClient persists automatically; for in-memory client, nothing to do
        return None


