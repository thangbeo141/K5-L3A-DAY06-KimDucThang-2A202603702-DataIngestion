"""Implement fixed-size (Strategy A) and structure/paragraph-aware chunking (Strategy B/C)."""
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Strategy A: Split text into fixed-size character windows with overlap.

    - Giữ nguyên số trang và nguồn.
    - Cắt cơ học theo độ dài ký tự cố định.
    """
    text = page.text
    if not text:
        return []

    chunks: list[Chunk] = []
    step = max(1, size - overlap)
    start = 0
    chunk_idx = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk_text = text[start:end].strip()

        if chunk_text:
            meta = dict(page.metadata)
            meta["chunk_strategy"] = "fixed_size"
            meta["chunk_index"] = chunk_idx

            chunks.append(
                Chunk(
                    chunk_id=f"{page.document_id}_p{page.page}_fix_{chunk_idx}",
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=chunk_text,
                    metadata=meta
                )
            )
            chunk_idx += 1

        if end == len(text):
            break
        start += step

    return chunks


def by_paragraph(page: DocumentPage, max_size: int = 800) -> list[Chunk]:
    """Strategy B & C: Structure-aware paragraph chunking.

    - Tách theo khối đoạn văn tự nhiên (dựa trên dấu xuống dòng đôi hoặc kết thúc ý).
    - Gom các đoạn nhỏ liền kề để đạt kích thước phù hợp (< max_size), không làm đứt giữa câu.
    - Giúp duy trì tính mạch lạc (chunk coherence) cao hơn rõ rệt so với fixed-size.
    """
    text = page.text
    if not text:
        return []

    # Tách đoạn văn dựa trên phân đoạn tự nhiên
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not raw_paragraphs:
        # Nếu trang không có \n\n, tách theo dòng
        raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks: list[Chunk] = []
    current_parts: list[str] = []
    current_len = 0
    chunk_idx = 0

    for para in raw_paragraphs:
        para_len = len(para)

        # Nếu đoạn văn đơn lẻ quá dài (vượt quá max_size), cắt đoạn đó
        if para_len > max_size:
            # Xả các đoạn đang gom trước đó nếu có
            if current_parts:
                combined_text = "\n\n".join(current_parts).strip()
                meta = dict(page.metadata)
                meta["chunk_strategy"] = "by_paragraph"
                meta["chunk_index"] = chunk_idx
                chunks.append(
                    Chunk(
                        chunk_id=f"{page.document_id}_p{page.page}_para_{chunk_idx}",
                        document_id=page.document_id,
                        source=page.source,
                        page=page.page,
                        text=combined_text,
                        metadata=meta
                    )
                )
                chunk_idx += 1
                current_parts = []
                current_len = 0

            # Cắt đoạn quá khổ theo câu hoặc khoảng 600 ký tự
            sub_start = 0
            while sub_start < para_len:
                sub_end = min(sub_start + max_size, para_len)
                sub_text = para[sub_start:sub_end].strip()
                if sub_text:
                    meta = dict(page.metadata)
                    meta["chunk_strategy"] = "by_paragraph"
                    meta["chunk_index"] = chunk_idx
                    chunks.append(
                        Chunk(
                            chunk_id=f"{page.document_id}_p{page.page}_para_{chunk_idx}",
                            document_id=page.document_id,
                            source=page.source,
                            page=page.page,
                            text=sub_text,
                            metadata=meta
                        )
                    )
                    chunk_idx += 1
                sub_start += max_size
            continue

        # Gom các đoạn văn lại nếu chưa quá max_size
        if current_len + para_len + 2 > max_size and current_parts:
            combined_text = "\n\n".join(current_parts).strip()
            meta = dict(page.metadata)
            meta["chunk_strategy"] = "by_paragraph"
            meta["chunk_index"] = chunk_idx
            chunks.append(
                Chunk(
                    chunk_id=f"{page.document_id}_p{page.page}_para_{chunk_idx}",
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=combined_text,
                    metadata=meta
                )
            )
            chunk_idx += 1
            current_parts = [para]
            current_len = para_len
        else:
            current_parts.append(para)
            current_len += para_len + 2

    # Đưa đoạn còn lại cuối cùng vào chunk
    if current_parts:
        combined_text = "\n\n".join(current_parts).strip()
        meta = dict(page.metadata)
        meta["chunk_strategy"] = "by_paragraph"
        meta["chunk_index"] = chunk_idx
        chunks.append(
            Chunk(
                chunk_id=f"{page.document_id}_p{page.page}_para_{chunk_idx}",
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=combined_text,
                metadata=meta
            )
        )

    return chunks
