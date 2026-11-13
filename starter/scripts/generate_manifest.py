import json
import unicodedata
from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("day06/K5-L3A-DAY06-KimDucThang-2A202603702-DataIngestion/data/so_tay_sinh_vien_2025.pdf")
reader = PdfReader(pdf_path)
total_pages = len(reader.pages)

pages_data = []

# Analyze sections based on headings
current_section = "tong_quan"

for idx, page in enumerate(reader.pages, start=1):
    raw_text = page.extract_text() or ""
    norm_text = unicodedata.normalize("NFC", raw_text).strip()
    char_count = len(norm_text)
    
    # Identify cover and table of contents
    if idx == 1:
        category = "cover"
        is_content = False
        section = "bia"
    elif 2 <= idx <= 5:
        category = "toc"
        is_content = False
        section = "muc_luc"
    else:
        # Determine section based on content keywords
        upper_text = norm_text.upper()
        if "QUY CHẾ ĐÀO TẠO" in upper_text or "HỌC PHẦN" in upper_text or "TÍN CHỈ" in upper_text:
            current_section = "dao_tao"
        elif "THƯ VIỆN" in upper_text or "MƯỢN" in upper_text and "TRẢ TÀI LIỆU" in upper_text:
            current_section = "thu_vien"
        elif "KHEN THƯỞNG" in upper_text or "KỶ LUẬT" in upper_text or "RÈN LUYỆN" in upper_text:
            current_section = "quan_ly_sinh_vien"
        elif "HỌC BỔNG" in upper_text or "CHÍNH SÁCH" in upper_text or "HỌC PHÍ" in upper_text:
            current_section = "hoc_bong_chinh_sach"
        elif "KÝ TÚC XÁ" in upper_text or "NỘI TRÚ" in upper_text:
            current_section = "ky_tuc_xa"
            
        category = "content"
        is_content = char_count > 50
        section = current_section

    pages_data.append({
        "page_number": idx,
        "char_count": char_count,
        "category": category,
        "is_content_page": is_content,
        "section": section,
        "preview": norm_text[:120].replace("\n", " ") if norm_text else ""
    })

content_pages = [p for p in pages_data if p["is_content_page"]]
total_content_chars = sum(p["char_count"] for p in content_pages)

manifest = {
    "source_id": "so_tay_sinh_vien_2025",
    "title": "Sổ tay Sinh viên Năm học 2025 - 2026",
    "institution": "Trường Đại học Tài nguyên và Môi trường Hà Nội",
    "source_path_or_url": "https://hunre.edu.vn/download/news/2025/12/01/134659_1.Sổ tay SV_2025.pdf",
    "license_or_permission": "Tài liệu công khai lưu hành nội bộ và hướng dẫn sinh viên theo quy định của nhà trường",
    "accessed_at": "2026-11-13",
    "format": "PDF",
    "version": "2025-2026",
    "total_physical_pages": total_pages,
    "content_pages_count": len(content_pages),
    "total_content_characters": total_content_chars,
    "page_counting_rule": "Loại bỏ trang bìa (trang 1) và mục lục/lời mở đầu (trang 2-5). Chỉ tính các trang từ 6 đến 61 có nội dung quy chế, hướng dẫn thực tế với số ký tự > 50.",
    "filter_metadata_fields": {
        "section": "Chuyên mục nội dung (dao_tao, thu_vien, quan_ly_sinh_vien, hoc_bong_chinh_sach, ky_tuc_xa)"
    },
    "pages": pages_data
}

manifest_path = Path("day06/K5-L3A-DAY06-KimDucThang-2A202603702-DataIngestion/data/manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Manifest written successfully to {manifest_path}")
print(f"Total pages: {total_pages}, Valid Content pages: {len(content_pages)}, Total chars: {total_content_chars}")

