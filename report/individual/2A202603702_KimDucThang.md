# Báo cáo cá nhân — Day 6: Data Ingestion Engineering

- **Họ và tên**: Kim Đức Thắng
- **MSSV**: 2A202603702
- **Lớp**: L3A
- **Chủ đề**: Kỹ thuật nạp dữ liệu (Data Ingestion Pipeline) và Đánh giá Benchmark cho RAG
- **Repo bài nộp**: `K5-L3A-DAY06-KimDucThang-2A202603702-DataIngestion`

---

## 1. Dữ liệu và pipeline

- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang**:
  - *Chủ đề*: Sổ tay sinh viên năm học 2025 - 2026 (Trường Đại học Tài nguyên và Môi trường Hà Nội).
  - *Nguồn và quyền sử dụng*: Tài liệu công khai hướng dẫn sinh viên, tải trực tiếp từ cổng thông tin nhà trường (`https://hunre.edu.vn/download/news/2025/12/01/134659_1.Sổ tay SV_2025.pdf`).
  - *Số trang*: File PDF gồm 61 trang vật lý.
  - *Quy tắc tính trang*: Loại bỏ trang 1 (bìa) và trang 2–5 (lời mở đầu + mục lục). Chỉ tính các trang từ trang 6 đến trang 61 có nội dung quy chế hữu ích với độ dài > 50 ký tự. Tổng số trang nội dung hợp lệ là **54 trang** (tổng cộng 87.650 ký tự), vượt xa yêu cầu tối thiểu ≥ 30 trang của đề bài. Toàn bộ thông tin được ghi chi tiết trong `data/manifest.json`.

- **Chuẩn hóa, lỗi và giới hạn**:
  - *Chuẩn hóa*: Sử dụng `unicodedata.normalize('NFC', text)` để đồng nhất bảng mã tiếng Việt dạng dựng sẵn, tránh xung đột giữa tổ hợp và dựng sẵn khi so khớp chuỗi. Làm sạch các ký tự khoảng trắng thừa nhưng bảo lưu cấu trúc xuống dòng đoạn văn.
  - *Lỗi & Giới hạn*: Một số trang PDF có khoảng trắng giữa các âm tiết tiếng Việt do layout in ấn (ví dụ: `đăng nh ập`, `ph ải làm`). Pipeline đã dùng giải thuật chuẩn hóa tolerant-spacing khi đối chiếu chuỗi bằng chứng để tránh false negative.

- **Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí**:
  - *Embedding model*: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (chạy local qua thư viện `fastembed` 0.9.1 trên nền ONNX Runtime).
  - *Số chiều (Dimensions)*: 384 chiều.
  - *Vector Store*: PostgreSQL 16.16 kết hợp extension `pgvector 0.8.7` chạy bằng Docker Compose local (cổng `127.0.0.1:55433`).
  - *Metric tìm kiếm*: Cosine Distance (`<=>`), điểm tương đồng cosine = $1.0 - \text{distance}$.
  - *Lệnh chạy pipeline*: `python -m src.run` (từ thư mục `starter/`).
  - *Chi phí (Cost)*: **0 USD** (chạy hoàn toàn local offline, không tiêu tốn token API).

- **Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn**:
  - *Metadata bắt buộc*: `document_id` (`so_tay_sinh_vien_2025`), `source` (`so_tay_sinh_vien_2025.pdf`), `page` (số trang vật lý gốc 1–61 để phục vụ truy vết).
  - *Trường lọc bổ sung (`section`)*: Phân loại văn bản thành 5 nhóm chuyên mục:
    1. `dao_tao`: Quy chế đào tạo tín chỉ, đăng ký môn học, thi cử, xét tốt nghiệp.
    2. `thu_vien`: Quy định thẻ thư viện, tra cứu tài liệu số/in, thời hạn mượn/trả sách.
    3. `quan_ly_sinh_vien`: Quy định khen thưởng, khung kỷ luật, đánh giá rèn luyện.
    4. `hoc_bong_chinh_sach`: Học bổng khuyến khích học tập, miễn giảm học phí, trợ cấp xã hội.
    5. `ky_tuc_xa`: Nội quy lưu trú ký túc xá.
  - *Lý do chọn*: Tài liệu trường học có cấu trúc phân ban rõ ràng. Việc gắn `section` giúp người dùng có thể giới hạn phạm vi tìm kiếm theo ngữ cảnh bài toán (ví dụ: đang hỏi về thủ tục thư viện thì chỉ quét trong khối `thu_vien`).

---

## 2. Cấu hình và benchmark

- **Mô tả 3 chiến lược A / B / C**:
  - **Strategy A (Fixed-size Chunking)**: Chia text thành các cửa sổ ký tự cố định có kích thước `size = 500` ký tự, độ gối đầu `overlap = 50` ký tự. Lưu đầy đủ metadata nguồn và số trang. Không áp dụng filter khi tìm kiếm.
  - **Strategy B (Paragraph/Structure Chunking)**: Chia text theo các khối đoạn văn tự nhiên (`\n\n`), gom các đoạn nhỏ liền kề tối đa `max_size = 800` ký tự để giữ trọn vẹn ngữ cảnh của ý/câu văn, không làm đứt giữa câu. Không áp dụng filter khi tìm kiếm.
  - **Strategy C (Paragraph Chunking + Metadata Filter)**: Sử dụng chính xác tập chunk và vector của Strategy B (đảm bảo so sánh kiểm soát cô lập duy nhất 1 biến số). Khi người dùng/câu hỏi có điều kiện lọc metadata (ví dụ `filter: {"section": "thu_vien"}`), câu truy vấn sẽ bổ sung điều kiện SQL `WHERE metadata->>'section' = 'thu_vien'`. Đối với câu hỏi không có filter, hệ thống tìm kiếm toàn cục như Strategy B.

- **Bộ câu hỏi Benchmark (≥20 câu: 15 dev / 5 test)**:
  - Gồm đúng **20 câu hỏi**, tách cố định thành **15 câu Dev** (`q01`–`q15`) và **5 câu Test** (`q16`–`q20`).
  - Gồm đủ 4 nhóm câu hỏi: Trực tiếp (Direct), Diễn đạt lại (Paraphrased), Điều kiện/Ngoại lệ (Conditional), và Lọc Metadata (Filtered).
  - Có **5 câu có yêu cầu filter metadata** (3 câu dev: `q06`, `q07`, `q13`; 2 câu test: `q16`, `q20`), vượt tiêu chuẩn tối thiểu.
  - Toàn bộ 20 câu hỏi đã được script `verify_benchmark.py` kiểm chứng tự động khớp 100% với đoạn trích văn bản (`evidence_quote`) và số trang gốc (`gold_page`) trước khi tiến hành chạy benchmark.

- **Tiêu chí chọn chiến lược chốt trước khi xem tập Test**:
  - Ưu tiên 1: Tối đa hóa **Evidence Hit@3** (đảm bảo thông tin trả lời nằm trong top 3 để LLM không bị ảo giác).
  - Ưu tiên 2: **Tính mạch lạc của chunk (Chunk Coherence)** và **Chất lượng bằng chứng (Grounding Quality)** (đoạn trích phải tròn câu, đủ ngữ cảnh, không bị ngắt cụt).
  - Ưu tiên 3: Tối ưu tài nguyên (số lượng chunk và thời gian nạp).

---

## 3. Kết quả thực nghiệm

### Bảng 1: Hiệu năng Truy xuất và Tài nguyên
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian nạp (s) | Chi phí ($) |
|---|---|---|---|---|---|---|
| **STRATEGY A** | Dev | 7/15 (46.7%) | 9/15 (60.0%) | 207 | 7.92s | 0.00 |
| **STRATEGY A** | Test | 3/5 (60.0%) | 4/5 (80.0%) | 207 | 7.92s | 0.00 |
| **STRATEGY B** | Dev | 9/15 (60.0%) | 9/15 (60.0%) | 180 | 5.91s | 0.00 |
| **STRATEGY B** | Test | 3/5 (60.0%) | 3/5 (60.0%) | 180 | 5.91s | 0.00 |
| **STRATEGY C** | Dev | 9/15 (60.0%) | 9/15 (60.0%) | 180 | 5.91s | 0.00 |
| **STRATEGY C** | Test | 2/5 (40.0%) | 2/5 (40.0%) | 180 | 5.91s | 0.00 |

### Bảng 2: Đánh giá Thủ công 5 Khía cạnh
| Strategy | Coherence TB /2 (n=10) | Metadata Đủ & Đúng (n=15) | Filter Tuân thủ (n/N) | Grounding TB /2 (n=5 test) |
|---|---|---|---|---|
| **STRATEGY A** | 0.8 / 2.0 | 14/15 (93.3%) | N/A (không dùng filter) | 1.4 / 2.0 |
| **STRATEGY B** | **2.0 / 2.0** | 14/15 (93.3%) | N/A (không dùng filter) | 0.8 / 2.0 |
| **STRATEGY C** | **2.0 / 2.0** | 14/15 (93.3%) | **2/2 (100% tuân thủ)** | 0.8 / 2.0 |

- **Đường dẫn artifact & trace**:
  - Traces chi tiết: `results/traces_strategy_A.json`, `results/traces_strategy_B.json`, `results/traces_strategy_C.json`.
  - File tổng hợp chỉ số: `results/summary.json`.
  - Mẫu chấm thủ công và lý giải chi tiết: `results/manual_audit.json`.
  - Nhật ký thí nghiệm: `artifacts/experiment_log.csv`.
  - *Cách chọn mẫu audit*: Chọn 10 vị trí nội dung quan trọng trải dài từ trang 8 đến trang 42 đại diện cho 5 chuyên mục; chọn toàn bộ 5 câu test để chấm Grounding Quality (thang 0–2).

---

## 4. Phân tích và kết luận

### So sánh Strategy A vs Strategy B (Ảnh hưởng của phương pháp Chunking):
- **Tính mạch lạc (Chunk Coherence)**: Strategy B vượt trội hoàn toàn (2.0/2 so với 0.8/2 của Strategy A). Strategy A do cắt cứng theo 500 ký tự nên thường xuyên cắt đứt đôi câu văn (ví dụ tại trang 21, câu `và ph ải làm thủ tục...` bị ngắt lìa; tại trang 9, bảng tiết học bị chia cắt giữa chừng). Ngược lại, Strategy B gom trọn từng đoạn văn, giữ nguyên ý nghĩa độc lập của mệnh đề.
- **Độ chính xác Top-1 (Hit@1)**: Trên tập Dev, Strategy B nâng Hit@1 từ 46.7% (Strategy A) lên **60.0%**. Việc giữ ngữ cảnh trọn vẹn giúp vector embedding đại diện chính xác hơn cho toàn bộ nội dung đoạn văn, giúp câu truy vấn bám sát chunk chuẩn xác hơn.
- **Tài nguyên**: Strategy B giảm số lượng chunk từ 207 xuống còn 180 chunks (giảm 13%), giúp thời gian embedding và nạp database giảm từ 7.92s xuống 5.91s (tiết kiệm 25% thời gian).

### So sánh Strategy B vs Strategy C (Ảnh hưởng của Metadata Filtering):
- **Ưu điểm**: Khi có metadata filter chính xác (ví dụ câu `q16` về thư viện), Strategy C loại bỏ 100% các đoạn nhiễu ở các khoa/chuyên mục khác, chỉ trả về đúng các tài liệu thuộc `thu_vien`. Tỷ lệ tuân thủ filter đạt tuyệt đối 100% (2/2 câu có filter trong test).
- **Phân tích trade-off và thất bại tại câu `q20`**:
  - *Câu hỏi q20*: "Thủ tục xin xác nhận đăng ký làm thẻ vé tháng xe buýt cho sinh viên thuộc lĩnh vực công tác nào?" (Gold page: 42, thuộc mục Công tác sinh viên).
  - *Ở Strategy B (không filter)*: Truy xuất thành công Top-1 chính xác vào trang 42 với độ tương đồng rất cao (Score: 0.7199), đạt Hit@1 và Hit@3.
  - *Ở Strategy C (có filter `section: quan_ly_sinh_vien`)*: Lại thất bại (Hit@1 = False, Hit@3 = False).
  - *Nguyên nhân thất bại (Ví dụ lỗi 1)*: Do ở bước Ingestion tự động, trang 42 nằm liền sau một số trang thư viện và không có từ khóa nhận diện mới ở đầu trang, hàm gán nhãn đã kế thừa nhãn `thu_vien` cho trang 42. Khi Strategy C áp đặt bộ lọc cứng `WHERE section = 'quan_ly_sinh_vien'`, nó đã vô tình **triệt tiêu hoàn toàn chunk đúng**.
  - *Bài học xương máu*: Metadata Filter là "con dao hai lưỡi". Nếu chất lượng gán nhãn metadata ở khâu Ingestion không đạt độ chính xác 100%, việc dùng Hard Filtering sẽ gây ra lỗi loại trừ âm tính giả (False Negative), làm hệ thống hoạt động kém hơn cả Dense Search thuần túy!

### Ví dụ lỗi thứ 2 (Lỗi Semantic Mismatch ở câu `q19`):
- *Câu hỏi q19*: "Hình thức kỷ luật đình chỉ học tập có thời hạn áp dụng cho sinh viên trong trường hợp nào?" (Gold page: 30).
- *Kết quả*: Cả 3 cấu hình A, B, C đều trượt top-3 ở câu này.
- *Nguyên nhân*: Trang 30 chứa định nghĩa điều khoản kỷ luật với văn phong quy phạm pháp luật khô khan (`Đình chỉ học tập có thời hạn: áp dụng đối với những người học đang trong thời gian bị cảnh cáo...`). Trong khi đó, mô hình embedding đa ngữ lại ưu tiên tìm về các trang có từ khóa "rèn luyện", "kỷ luật", "học bổng" ở các trang 24, 26, 28 vì mật độ lặp lại các từ này cao hơn. Đây là hạn chế kinh điển của Dense Retrieval khi xử lý các câu hỏi diễn đạt lại mang tính pháp lý.

### Chiến lược được lựa chọn & Điều kiện áp dụng:
- **Chiến lược được chọn**: **Strategy B (Paragraph-based Chunking, Soft/Hybrid Metadata)**.
- **Lý do**: Strategy B đạt sự cân bằng tối ưu giữa độ chính xác truy xuất (Hit@1 60%), tính mạch lạc tuyệt đối (Coherence 2.0/2), giảm tải 13% dung lượng lưu trữ vector và không có rủi ro bị "bộ lọc cứng" chặn nhầm dữ liệu.
- **Điều kiện áp dụng**: Dùng Paragraph-based chunking cho mọi tài liệu có cấu trúc văn bản/quy chế. Nếu muốn dùng Metadata, nên áp dụng dưới dạng **Soft Scoring / Re-ranking Boost** (tăng điểm ưu tiên cho metadata phù hợp) thay vì dùng Hard Filter (`WHERE`) trừ khi metadata được trích xuất hoàn toàn chuẩn xác từ hệ thống có cấu trúc.

### Hạn chế của nghiên cứu:
1. *Kích thước tập Test nhỏ (5 câu)*: Mỗi câu đúng/sai làm thay đổi tỷ lệ tới 20%, dễ gây sai lệch thống kê nếu kết luận vội vã.
2. *Gán nhãn metadata tự động*: Hàm `detect_section` theo keyword còn mang tính heuristic, dẫn tới hiện tượng trôi nhãn (label drift) ở các trang chuyển tiếp.

### Đề xuất cải tiến nếu mở rộng bài toán:
1. **Hybrid Retrieval (Dense + BM25)**: Kết hợp embedding dense với thuật toán tìm kiếm từ khóa BM25 để xử lý triệt để các câu hỏi thuật ngữ chính xác như `q19`.
2. **Metadata Enrichment bằng LLM**: Thay vì dùng heuristic keyword thô sơ, sử dụng LLM nhỏ để trích xuất cấu trúc JSON Schema chuẩn xác cho từng trang/đoạn văn trước khi nạp vào pgvector.
3. **Soft Filtering (Cross-Encoder / Re-ranking)**: Chuyển metadata thành trọng số phạt/thưởng trong hàm re-ranking thay vì loại bỏ cứng trong câu lệnh SQL.

