"""Store and search vectors using PostgreSQL + pgvector with metadata filtering."""
import json
from typing import Any
import psycopg
from .models import Chunk


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int = 384) -> None:
        self.database_url = database_url
        self.dimensions = dimensions

    def create_schema(self) -> None:
        """Create PostgreSQL table with pgvector column and JSONB metadata."""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS rag_chunks (
                        chunk_id TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        document_id TEXT NOT NULL,
                        source TEXT NOT NULL,
                        page INT NOT NULL,
                        text TEXT NOT NULL,
                        metadata JSONB NOT NULL,
                        embedding vector({self.dimensions}) NOT NULL,
                        PRIMARY KEY (chunk_id, strategy)
                    );
                    CREATE INDEX IF NOT EXISTS idx_rag_chunks_strat ON rag_chunks(strategy);
                """)
            conn.commit()

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Validate lengths/dimensions and write stable IDs without duplicates.

        Xóa các bản ghi cũ của strategy đó trước khi nạp để bảo đảm tính idempotent (không nhân đôi).
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"Số chunk ({len(chunks)}) không khớp số vector ({len(vectors)})")

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                # Xóa các chunk cũ của chiến lược tương ứng để tránh nhân bản
                cur.execute("DELETE FROM rag_chunks WHERE strategy = %s", (strategy,))

                insert_sql = """
                    INSERT INTO rag_chunks (chunk_id, strategy, document_id, source, page, text, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
                """
                records = [
                    (
                        c.chunk_id,
                        strategy,
                        c.document_id,
                        c.source,
                        c.page,
                        c.text,
                        json.dumps(c.metadata, ensure_ascii=False),
                        str(v)
                    )
                    for c, v in zip(chunks, vectors)
                ]
                cur.executemany(insert_sql, records)
            conn.commit()

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Filter permitted metadata in SQL, rank by cosine distance (<=>), return top-k.

        Cosine similarity = 1.0 - Cosine Distance.
        """
        query_vec_str = str(query_vector)
        params: list[Any] = [query_vec_str, strategy]
        filter_clause = ""

        if filters:
            for key, val in filters.items():
                filter_clause += " AND metadata->>%s = %s"
                params.extend([key, str(val)])

        params.extend([query_vec_str, top_k])

        sql = f"""
            SELECT chunk_id, document_id, source, page, text, metadata,
                   (1 - (embedding <=> %s::vector)) AS score
            FROM rag_chunks
            WHERE strategy = %s {filter_clause}
            ORDER BY embedding <=> %s::vector ASC
            LIMIT %s;
        """

        results: list[dict[str, Any]] = []
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
                for row in rows:
                    meta = row[5] if isinstance(row[5], dict) else json.loads(row[5])
                    results.append({
                        "chunk_id": row[0],
                        "document_id": row[1],
                        "source": row[2],
                        "page": row[3],
                        "text": row[4],
                        "metadata": meta,
                        "score": round(float(row[6]), 4)
                    })
        return results
