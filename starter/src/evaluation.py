"""Evaluate retrieved evidence and preserve per-query traces."""
import unicodedata
from typing import Any


def clean_text_for_match(text: str) -> str:
    """Normalize text for robust whitespace/case-insensitive evidence matching."""
    norm = unicodedata.normalize("NFC", text or "")
    return " ".join(norm.split()).lower()


def is_chunk_hit(gold_page: int, evidence_quote: str, hit: dict[str, Any]) -> bool:
    """Xác định một chunk có phải là Hit hay không.

    Hit hợp lệ khi:
    1. Chunk thuộc đúng trang chứa bằng chứng (gold_page).
    2. Chunk chứa đoạn trích dẫn bằng chứng (evidence_quote).
    """
    if hit.get("page") != gold_page:
        return False

    hit_clean = clean_text_for_match(hit.get("text", ""))
    quote_clean = clean_text_for_match(evidence_quote)

    return quote_clean in hit_clean


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Check source/page and evidence match; keep hit@1 and hit@3 trace."""
    gold_page = question["gold_page"]
    evidence_quote = question["evidence_quote"]

    evaluated_hits: list[dict[str, Any]] = []
    has_hit_at_1 = False
    has_evidence_hit_at_3 = False

    for rank, h in enumerate(hits, start=1):
        hit_match = is_chunk_hit(gold_page, evidence_quote, h)
        if rank == 1 and hit_match:
            has_hit_at_1 = True
        if hit_match:
            has_evidence_hit_at_3 = True

        evaluated_hits.append({
            "rank": rank,
            "chunk_id": h.get("chunk_id"),
            "page": h.get("page"),
            "score": h.get("score"),
            "metadata": h.get("metadata"),
            "is_hit": hit_match,
            "text_preview": h.get("text", "")[:150]
        })

    return {
        "id": question["id"],
        "split": question.get("split", "dev"),
        "type": question.get("type", "truc_tiep"),
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "gold_page": gold_page,
        "evidence_quote": evidence_quote,
        "filter": question.get("filter"),
        "hit_at_1": has_hit_at_1,
        "evidence_hit_at_3": has_evidence_hit_at_3,
        "hits": evaluated_hits
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Hit@1 and Evidence Hit@3 by split (dev / test / all)."""
    summary = {}
    for split_key in ["dev", "test", "all"]:
        if split_key == "all":
            subset = traces
        else:
            subset = [t for t in traces if t.get("split") == split_key]

        total = len(subset)
        if total == 0:
            summary[split_key] = {
                "total": 0,
                "hit1_count": 0,
                "hit1_rate": 0.0,
                "hit3_count": 0,
                "hit3_rate": 0.0,
                "ratio_hit1": "0/0",
                "ratio_hit3": "0/0"
            }
            continue

        hit1 = sum(1 for t in subset if t["hit_at_1"])
        hit3 = sum(1 for t in subset if t["evidence_hit_at_3"])

        summary[split_key] = {
            "total": total,
            "hit1_count": hit1,
            "hit1_rate": round(hit1 / total, 4),
            "hit3_count": hit3,
            "hit3_rate": round(hit3 / total, 4),
            "ratio_hit1": f"{hit1}/{total}",
            "ratio_hit3": f"{hit3}/{total}"
        }

    return summary
