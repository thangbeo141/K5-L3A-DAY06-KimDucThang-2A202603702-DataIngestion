import json
import unicodedata
from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("day06/K5-L3A-DAY06-KimDucThang-2A202603702-DataIngestion/data/so_tay_sinh_vien_2025.pdf")
reader = PdfReader(pdf_path)

def get_page_text(page_num):
    text = reader.pages[page_num - 1].extract_text() or ""
    return unicodedata.normalize("NFC", text)

# Let's verify and build questions
questions = [
    # --- DEV SET (15 questions: q01 - q15) ---
    {
        "id": "q01",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Tiết 1 buổi sáng bắt đầu và kết thúc vào khung giờ nào?",
        "expected_answer": "Bắt đầu từ 7h00 và kết thúc vào 7h50",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 9,
        "evidence_quote": "Tiết 1 7h00 : 7h50",
        "filter": None
    },
    {
        "id": "q02",
        "split": "dev",
        "type": "dieu_kien",
        "question": "Sinh viên phải tham dự tối thiểu bao nhiêu phần trăm số giờ học của từng bài thực hành để được tổng kết học phần?",
        "expected_answer": "Tối thiểu 70% số giờ học của từng bài",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 10,
        "evidence_quote": "Đối với các học phần thực hành: Sinh viên tham dự đủ 70% số giờ học c ủa từng bài",
        "filter": None
    },
    {
        "id": "q03",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Điểm tổng kết môn Giáo dục quốc phòng và an ninh được làm tròn tới mấy chữ số thập phân và có quy đổi sang điểm chữ không?",
        "expected_answer": "Làm tròn đến hai chữ số thập phân và không tính kết quả học tập theo điểm chữ",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 14,
        "evidence_quote": "làm tròn đến hai chữ số thập phân; không tính k ết quả học tập môn học GDQP-AN theo điểm chữ",
        "filter": None
    },
    {
        "id": "q04",
        "split": "dev",
        "type": "dieu_kien",
        "question": "Để đủ điều kiện xét tốt nghiệp, điểm trung bình tích lũy của toàn khóa học tối thiểu phải đạt bao nhiêu?",
        "expected_answer": "Từ 2,00 trở lên",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 16,
        "evidence_quote": "Điểm trung bình tích lũy của toàn khóa học đạt từ 2,00 trở lên.",
        "filter": None
    },
    {
        "id": "q05",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Sinh viên tham gia thực hiện đề tài nghiên cứu khoa học có được làm chủ nhiệm đề tài cùng cấp nào khác không?",
        "expected_answer": "Không được là chủ nhiệm của đề tài nghiên cứu khoa học cùng cấp nào khác",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 18,
        "evidence_quote": "Không là chủ nhiệm của đề tài nghiên cứu khoa học cùng cấp nào khác.",
        "filter": None
    },
    {
        "id": "q06",
        "split": "dev",
        "type": "filter_metadata",
        "question": "Nếu độc giả chỉ muốn tra cứu tài liệu số trên phần mềm thư viện thì cần chọn thẻ nào?",
        "expected_answer": "Chọn thẻ 'Bộ sưu tập số'",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 20,
        "evidence_quote": "Nếu chỉ muốn tìm tài liệu số thì chọn thẻ “Bộ sưu tập số”.",
        "filter": {"section": "thu_vien"}
    },
    {
        "id": "q07",
        "split": "dev",
        "type": "filter_metadata",
        "question": "Trong thư viện, sinh viên có thể đọc toàn bộ file tài liệu nội sinh trên máy tính tại phòng nào?",
        "expected_answer": "Tại Phòng Đọc Sinh viên",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 22,
        "evidence_quote": "Tại Thư viện trường, Bạn đọc có thể đọc toàn bộ file tài liệu nội sinh trên máy tính của Thư viện tại Phòng Đọc Sinh viên.",
        "filter": {"section": "thu_vien"}
    },
    {
        "id": "q08",
        "split": "dev",
        "type": "dieu_kien",
        "question": "Điều kiện về điểm thi và điểm tổng kết các học phần lần thứ nhất để được xét học bổng khuyến khích học tập là gì?",
        "expected_answer": "Không có điểm dưới 4.0 theo thang điểm 10, học phần GDTC đạt từ 4.0 và GDQP-AN đạt từ 5.0 trở lên",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 28,
        "evidence_quote": "Không có điểm thi và đi ểm tổng kết học phần tính điểm lần thứ nhất các học phần trong năm xét dưới 4.0 theo thang điểm 10",
        "filter": None
    },
    {
        "id": "q09",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Hình thức kỷ luật Cảnh cáo được áp dụng đối với người học trong những trường hợp nào?",
        "expected_answer": "Áp dụng đối với người học đã bị khiển trách mà tái phạm hoặc vi phạm mức độ nhẹ có tính chất thường xuyên hoặc mới vi phạm lần đầu nhưng mức độ tương đối nghiêm trọng",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 30,
        "evidence_quote": "Cảnh cáo: áp dụng đối với người học đã bị khiển trách mà tái phạm hoặc vi phạm ở mức độ nhẹ nhưng hành vi vi phạm có tính chất thường xuyên",
        "filter": None
    },
    {
        "id": "q10",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Khi đăng nhập hệ thống thông tin sinh viên lần đầu, cấu trúc mật khẩu mặc định của sinh viên được quy định như thế nào?",
        "expected_answer": "Là ngày tháng năm sinh định dạng ddmmyyyy",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 46,
        "evidence_quote": "Ví dụ sinh viên có mã là: 11223355 và sinh ngày 31/12/2003 thì khi đó tên đăng nh ập sẽ là: 11223355 và mật khẩu là: 31122003",
        "filter": None
    },
    {
        "id": "q11",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Tiết 6 của buổi chiều bắt đầu từ mấy giờ và kết thúc lúc mấy giờ?",
        "expected_answer": "Từ 12h30 đến 13h20",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 9,
        "evidence_quote": "Tiết 6 12h30 : 13h20",
        "filter": None
    },
    {
        "id": "q12",
        "split": "dev",
        "type": "dieu_kien",
        "question": "Sinh viên có được xét học bổng khuyến khích học tập không nếu trong năm xét bị kỷ luật mức khiển trách?",
        "expected_answer": "Không được xét (quy định: Không bị kỷ luật từ mức khiển trách trở lên trong năm xét)",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 28,
        "evidence_quote": "Không bị kỷ luật từ mức khiển trách trở lên trong năm xét.",
        "filter": None
    },
    {
        "id": "q13",
        "split": "dev",
        "type": "filter_metadata",
        "question": "Trong trường hợp nào thì bạn đọc tại thư viện không được gia hạn thêm tài liệu mượn về nhà?",
        "expected_answer": "Nếu tài liệu đó trong kho đã hết",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 21,
        "evidence_quote": "Nếu tài liệu đó trong kho đã h ết, Bạn đọc sẽ không được gia hạn thêm và ph ải làm thủ tục trả tài liệu.",
        "filter": {"section": "thu_vien"}
    },
    {
        "id": "q14",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Mã ngành đào tạo của ngành Bất động sản tại trường là gì?",
        "expected_answer": "7340116",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 8,
        "evidence_quote": "1 Bất động sản 7340116",
        "filter": None
    },
    {
        "id": "q15",
        "split": "dev",
        "type": "dieu_kien",
        "question": "Điều kiện về tình trạng kỷ luật tại thời điểm xét tốt nghiệp là gì?",
        "expected_answer": "Không bị truy cứu trách nhiệm hình sự hoặc không đang trong thời gian bị kỷ luật ở mức đình chỉ học tập",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 16,
        "evidence_quote": "Tại thời điểm xét tốt nghiệp không bị truy cứu trách nhiệm hình sự hoặc không đang trong thời gian bị kỷ luật ở mức đình chỉ học tập.",
        "filter": None
    },

    # --- TEST SET (5 questions: q16 - q20) ---
    {
        "id": "q16",
        "split": "test",
        "type": "filter_metadata",
        "question": "Nếu chỉ muốn tìm tài liệu in trên cổng thông tin thư viện thì bạn đọc chọn thẻ nào?",
        "expected_answer": "Chọn thẻ 'Bộ sưu tập tài liệu in'",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 20,
        "evidence_quote": "Nếu chỉ muốn tìm tài liệu in thì chọn thẻ “Bộ sưu tập tài liệu in”.",
        "filter": {"section": "thu_vien"}
    },
    {
        "id": "q17",
        "split": "test",
        "type": "truc_tiep",
        "question": "Tiết học thứ 11 của buổi tối bắt đầu lúc mấy giờ và kết thúc lúc mấy giờ?",
        "expected_answer": "Bắt đầu từ 17h30 đến 18h20",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 9,
        "evidence_quote": "Tiết 11 17h30 : 18h20",
        "filter": None
    },
    {
        "id": "q18",
        "split": "test",
        "type": "dieu_kien",
        "question": "Trường hợp sinh viên không tham dự đủ 70% số giờ học của từng bài thực hành thì bị xử lý ra sao?",
        "expected_answer": "Nhận điểm F là điểm học phần và phải đăng ký học lại học phần đó hoặc đổi sang học phần khác",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 10,
        "evidence_quote": "nhận điểm F là điểm học phần và phải đăng ký học lại học phần đó hoặc học đổi sang học phần khác",
        "filter": None
    },
    {
        "id": "q19",
        "split": "test",
        "type": "dien_dat_lai",
        "question": "Hình thức kỷ luật đình chỉ học tập có thời hạn áp dụng cho sinh viên trong trường hợp nào?",
        "expected_answer": "Áp dụng đối với người học đang trong thời gian bị cảnh cáo mà vẫn vi phạm kỷ luật hoặc vi phạm nghiêm trọng",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 30,
        "evidence_quote": "Đình chỉ học tập có thời hạn: áp dụng đối với những người học đang trong thời gian bị cảnh cáo mà v ẫn vi ph ạm kỷ luật hoặc vi ph ạm nghiêm tr ọng",
        "filter": None
    },
    {
        "id": "q20",
        "split": "test",
        "type": "filter_metadata",
        "question": "Thủ tục xin xác nhận đăng ký làm thẻ vé tháng xe buýt cho sinh viên thuộc lĩnh vực công tác nào?",
        "expected_answer": "Lĩnh vực công tác sinh viên",
        "gold_source_id": "so_tay_sinh_vien_2025",
        "gold_page": 42,
        "evidence_quote": "I LĨNH VỰC CÔNG TÁC SINH VIÊN\n1 Xác nhận Đăng ký làm thẻ vé tháng xe buýt",
        "filter": {"section": "quan_ly_sinh_vien"}
    }
]

# Verify all evidence quotes exist in their respective gold pages
all_valid = True
for q in questions:
    page_text = get_page_text(q["gold_page"])
    # clean both for space tolerance
    clean_page = " ".join(page_text.split())
    clean_quote = " ".join(q["evidence_quote"].split())
    if clean_quote not in clean_page:
        print(f"FAILED verification for {q['id']} on page {q['gold_page']}!")
        print(f"  Quote: {repr(clean_quote)}")
        all_valid = False
    else:
        print(f"Verified {q['id']} (Page {q['gold_page']}, {q['split']}) -> OK")

if all_valid:
    out_dir = Path("day06/K5-L3A-DAY06-KimDucThang-2A202603702-DataIngestion/benchmark")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "questions.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\nALL 20 QUESTIONS VERIFIED! Saved to {out_path}")
else:
    print("\nSome quotes failed verification, please check!")
