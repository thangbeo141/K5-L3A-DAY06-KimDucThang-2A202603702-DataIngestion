"""Orchestrate the Day 06 Data Ingestion & Benchmark pipeline."""
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

from .ingestion import load_pdf
from .chunking import fixed_size, by_paragraph
from .embeddings import MyEmbedder
from .store import PgVectorStore
from .evaluation import evaluate_query, summarize


def main() -> None:
    root_dir = Path(__file__).resolve().parents[2]
    starter_dir = Path(__file__).resolve().parents[1]

    # 1. Load configuration
    load_dotenv(starter_dir / ".env")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        sys.exit("DATABASE_URL missing: hãy đảm bảo file starter/.env tồn tại.")

    pdf_path = root_dir / "data" / "so_tay_sinh_vien_2025.pdf"
    benchmark_path = root_dir / "benchmark" / "questions.json"
    results_dir = root_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        sys.exit(f"Không tìm thấy file tài liệu tại: {pdf_path}")
    if not benchmark_path.exists():
        sys.exit(f"Không tìm thấy file benchmark tại: {benchmark_path}")

    # 2. Ingestion & Validation
    print("=" * 60)
    print("1. INGESTION: Đang đọc và chuẩn hóa tài liệu PDF...")
    pages = load_pdf(pdf_path, document_id="so_tay_sinh_vien_2025", source="so_tay_sinh_vien_2025.pdf")
    print(f"-> Đã đọc {len(pages)} trang nội dung hữu ích (Yêu cầu tối thiểu: >= 30 trang).")
    if len(pages) < 30:
        sys.exit("LỖI: Số trang nội dung chưa đạt yêu cầu tối thiểu 30 trang.")

    with open(benchmark_path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    print(f"-> Đã nạp {len(questions)} câu hỏi benchmark ({sum(1 for q in questions if q['split'] == 'dev')} dev, {sum(1 for q in questions if q['split'] == 'test')} test).")

    # 3. Khởi tạo Embedder và Vector Store
    print("\n" * 1 + "=" * 60)
    print("2. HẠ TẦNG: Khởi tạo Embedder và kết nối PostgreSQL + pgvector...")
    embedder = MyEmbedder()
    store = PgVectorStore(database_url=db_url, dimensions=embedder.dimensions)
    store.create_schema()
    print("-> Schema database đã sẵn sàng.")

    # 4. Chuẩn bị 3 chiến lược
    strategies = ["strategy_a", "strategy_b", "strategy_c"]
    all_summaries = {}
    metrics_log = []

    # Strategy A: Fixed-size chunking (500 ký tự, overlap 50)
    print("\n" * 1 + "=" * 60)
    print("3. THỰC HIỆN CHIẾN LƯỢC A: Fixed-size Chunking (size=500, overlap=50, No Filter)")
    t0 = time.time()
    chunks_a = []
    for p in pages:
        chunks_a.extend(fixed_size(p, size=500, overlap=50))
    print(f"-> Strategy A tạo ra {len(chunks_a)} chunks.")
    
    # Vectorizing chunks A
    texts_a = [c.text for c in chunks_a]
    vectors_a = embedder.embed_documents(texts_a)
    store.upsert("strategy_a", chunks_a, vectors_a)
    time_a = round(time.time() - t0, 2)
    print(f"-> Đã nạp xong Strategy A vào pgvector trong {time_a}s.")

    # Strategy B & C: Paragraph-based chunking (max_size=800)
    print("\n" * 1 + "=" * 60)
    print("4. THỰC HIỆN CHIẾN LƯỢC B & C: Structure/Paragraph Chunking (max_size=800)")
    t0 = time.time()
    chunks_b = []
    for p in pages:
        chunks_b.extend(by_paragraph(p, max_size=800))
    print(f"-> Strategy B & C tạo ra {len(chunks_b)} chunks.")

    texts_b = [c.text for c in chunks_b]
    vectors_b = embedder.embed_documents(texts_b)
    store.upsert("strategy_b", chunks_b, vectors_b)
    # Strategy C dùng chung cấu trúc vector của B để so sánh cô lập vai trò của metadata filter
    store.upsert("strategy_c", chunks_b, vectors_b)
    time_b = round(time.time() - t0, 2)
    print(f"-> Đã nạp xong Strategy B & C vào pgvector trong {time_b}s.")

    # 5. Chạy Benchmark cho từng chiến lược
    print("\n" * 1 + "=" * 60)
    print("5. RETRIEVAL & BENCHMARKING: Chạy truy xuất top-3 cho 20 câu hỏi...")

    for strat in strategies:
        print(f"\n--- Đang đánh giá {strat.upper()} ---")
        traces = []
        for q in questions:
            q_vec = embedder.embed_query(q["question"])
            
            # Cấu hình C: áp dụng filter metadata nếu câu hỏi có yêu cầu filter
            # Cấu hình A và B: hoàn toàn không dùng filter
            active_filter = q.get("filter") if strat == "strategy_c" else None

            hits = store.search(strategy=strat, query_vector=q_vec, top_k=3, filters=active_filter)
            trace = evaluate_query(q, hits)
            traces.append(trace)

        # Lưu trace chi tiết
        trace_file = results_dir / f"traces_{strat}.json"
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(traces, f, ensure_ascii=False, indent=2)

        summary = summarize(traces)
        all_summaries[strat] = summary
        print(f"[{strat.upper()}] DEV:  Hit@1 = {summary['dev']['ratio_hit1']} ({summary['dev']['hit1_rate']*100:.1f}%), Evidence Hit@3 = {summary['dev']['ratio_hit3']} ({summary['dev']['hit3_rate']*100:.1f}%)")
        print(f"[{strat.upper()}] TEST: Hit@1 = {summary['test']['ratio_hit1']} ({summary['test']['hit1_rate']*100:.1f}%), Evidence Hit@3 = {summary['test']['ratio_hit3']} ({summary['test']['hit3_rate']*100:.1f}%)")

    # Lưu file tổng hợp
    summary_path = results_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, ensure_ascii=False, indent=2)

    print("\n" * 1 + "=" * 60)
    print("BẢNG TỔNG HỢP KẾT QUẢ BENCHMARK (DAY 06):")
    print("| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk Count | Thời gian (s) |")
    print("|---|---|---|---|---|---|")
    counts = {"strategy_a": len(chunks_a), "strategy_b": len(chunks_b), "strategy_c": len(chunks_b)}
    times = {"strategy_a": time_a, "strategy_b": time_b, "strategy_c": time_b}

    for strat in strategies:
        for split in ["dev", "test"]:
            s = all_summaries[strat][split]
            print(f"| {strat.upper():<10} | {split:<5} | {s['ratio_hit1']:<11} | {s['ratio_hit3']:<20} | {counts[strat]:<11} | {times[strat]:<13} |")
    print("=" * 60)
    print("Hoàn tất pipeline thành công!")


if __name__ == "__main__":
    main()
