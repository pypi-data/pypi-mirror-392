from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..core.base import BaseVectorStore


class PgVectorVectorStore(BaseVectorStore):
    def __init__(
        self,
        *,
        host: str,
        port: int = 5432,
        dbname: str,
        user: str,
        password: str,
        table_name: str,
        dim: int = 1536,
        metric: str = "cosine",  # cosine | l2 | ip
        sslmode: str = "require",
        create_index: bool = True,
        index_lists: int = 100,
        probes: int = 10,
        **config: Any,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            table_name=table_name,
            dim=dim,
            metric=metric,
            create_index=create_index,
            index_lists=index_lists,
            probes=probes,
            **config,
        )
        try:
            import psycopg  # type: ignore
            from pgvector.psycopg import register_vector, Vector  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise ImportError(
                "psycopg and pgvector are required. Install with `pip install llmpy[pg]`."
            ) from exc

        self._psycopg = psycopg
        self._Vector = Vector
        self._conn = psycopg.connect(
            host=host, port=port, dbname=dbname, user=user, password=password, sslmode=sslmode
        )
        self._conn.autocommit = True
        if not dbname:
            raise ValueError("dbname is required and must be non-empty.")
        if not table_name:
            raise ValueError("table_name is required and must be non-empty.")
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError("dim must be a positive integer.")

        self._table = table_name
        self._dim = dim
        self._metric = metric
        self._probes = probes

        with self._conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self._table} (
                    id TEXT PRIMARY KEY,
                    embedding VECTOR({self._dim}) NOT NULL,
                    metadata JSONB,
                    document TEXT
                )
                """
            )
            if create_index:
                ops = {
                    "l2": "vector_l2_ops",
                    "ip": "vector_ip_ops",
                    "cosine": "vector_cosine_ops",
                }.get(self._metric, "vector_cosine_ops")
                cur.execute(
                    f"CREATE INDEX IF NOT EXISTS {self._table}_idx ON {self._table} USING ivfflat (embedding {ops}) WITH (lists = {index_lists})"
                )
        # register vector type after extension is ensured
        register_vector(self._conn)

    def _distance_sql(self) -> str:
        # Operators: <-> L2, <#> inner product, <=> cosine distance
        if self._metric == "l2":
            return "<->"
        if self._metric == "ip":
            return "<#>"
        return "<=>"  # cosine

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

        rows: List[Tuple[Any, Any, Any, Any]] = []
        for i, emb in enumerate(embeddings):
            rows.append((ids[i], emb, metadatas[i], documents[i]))

        sql = (
            f"INSERT INTO {self._table} (id, embedding, metadata, document) VALUES (%s, %s, %s, %s) "
            f"ON CONFLICT (id) DO UPDATE SET embedding = excluded.embedding, metadata = excluded.metadata, document = excluded.document"
        )
        with self._conn.cursor() as cur:
            cur.executemany(sql, rows)
        return ids

    def similarity_search_by_vector(self, query_vector: List[float], *, k: int = 5) -> List[Dict[str, Any]]:
        op = self._distance_sql()
        results: List[Dict[str, Any]] = []
        with self._conn.cursor() as cur:
            # set probes separately to avoid multi-statement with parameters
            try:
                cur.execute(f"SET ivfflat.probes = {int(self._probes)}")
            except Exception:
                pass
            cur.execute(
                f"SELECT id, metadata, document, (embedding {op} %s) AS distance FROM {self._table} "
                f"ORDER BY embedding {op} %s LIMIT %s",
                (self._Vector(query_vector), self._Vector(query_vector), int(k)),
            )
            for rid, meta, doc, dist in cur.fetchall():
                results.append(
                    {
                        "id": rid,
                        "metadata": meta,
                        "document": doc,
                        "distance": float(dist) if dist is not None else None,
                    }
                )
        return results

    def delete(self, ids: Iterable[str]) -> None:  # type: ignore[override]
        with self._conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self._table} WHERE id = ANY(%s)", (list(ids),))

    def count(self) -> int:  # type: ignore[override]
        with self._conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self._table}")
            return int(cur.fetchone()[0])

    def persist(self) -> None:  # type: ignore[override]
        return None


