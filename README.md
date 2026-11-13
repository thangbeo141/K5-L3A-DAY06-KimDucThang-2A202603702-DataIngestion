# Day 06 · Data Ingestion Engineering

**Lab cá nhân** · **4 giờ** · **Dữ liệu tự chọn**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| Tối thiểu **30 trang nội dung** | Tối thiểu **3 cấu hình** | Tối thiểu **20 câu hỏi** |

---

## Thông tin bài nộp
- **Học viên**: Kim Đức Thắng - MSSV: 2A202603702 - Lớp: L3A
- **Corpus**: Sổ tay Sinh viên Năm học 2025 - 2026 (54 trang nội dung hữu ích, 87.650 ký tự)
- **Báo cáo chi tiết**: [report/individual/2A202603702_KimDucThang.md](report/individual/2A202603702_KimDucThang.md)
- **Nhật ký thí nghiệm**: [artifacts/experiment_log.csv](artifacts/experiment_log.csv)
- **Tập Benchmark**: [benchmark/questions.json](benchmark/questions.json) (15 dev, 5 test)
- **Manifest**: [data/manifest.json](data/manifest.json)
- **Kết quả & Trace**: [results/](results/)

---

## Hướng dẫn tái lập (Quickstart)

### 1. Khởi động Docker PostgreSQL + pgvector
```bash
cd starter
# Sao chép file cấu hình môi trường nếu chưa có
cp .env.example .env     # (Windows PowerShell: Copy-Item .env.example .env)
docker-compose -p day6_student_starter up -d --wait
python scripts/check_setup.py
```

### 2. Cài đặt thư viện Python
```bash
pip install -r requirements.txt
```

### 3. Chạy toàn bộ Pipeline và Benchmark
```bash
python -m src.run
```

Lệnh trên sẽ tự động:
1. Đọc và chuẩn hóa 54 trang PDF.
2. Sinh chunk và nhúng vector (384 chiều) cho 3 chiến lược: Strategy A (Fixed-size 500/50), Strategy B (Paragraph 800), Strategy C (Paragraph + Filter Metadata).
3. Nạp và lưu trữ vào pgvector.
4. Chạy truy xuất Top-3 cho toàn bộ 20 câu hỏi Benchmark (15 dev, 5 test).
5. Đánh giá Hit@1, Evidence Hit@3 và xuất trace ra thư mục `results/`.
