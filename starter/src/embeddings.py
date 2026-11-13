"""Real embedding provider adapter using fastembed (local multilingual model)."""
from typing import Protocol
from fastembed import TextEmbedding


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """Multilingual dense embedder running locally via ONNX Runtime (fast & 0-cost)."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name
        self.dimensions = 384
        # Khởi tạo mô hình embedding đa ngôn ngữ hỗ trợ tiếng Việt
        self._model = TextEmbedding(model_name=self.model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Tạo vector embedding cho danh sách các đoạn text."""
        if not texts:
            return []
        embeddings_generator = self._model.embed(texts)
        return [vector.tolist() for vector in embeddings_generator]

    def embed_query(self, question: str) -> list[float]:
        """Tạo vector embedding cho câu truy vấn."""
        embeddings_generator = self._model.embed([question])
        for vector in embeddings_generator:
            return vector.tolist()
        return [0.0] * self.dimensions
