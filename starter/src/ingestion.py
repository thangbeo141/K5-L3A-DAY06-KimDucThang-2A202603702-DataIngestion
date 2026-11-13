"""Read and normalize source data; retain traceability from page back to source."""
import unicodedata
from pathlib import Path
from pypdf import PdfReader
from .models import DocumentPage


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC) and clean whitespace without losing paragraph structure."""
    if not text:
        return ""
    # Chuẩn hóa Unicode tiếng Việt dạng dựng sẵn NFC
    text = unicodedata.normalize("NFC", text)
    # Chuẩn hóa ký tự khoảng trắng lạ nhưng giữ phân đoạn dòng
    lines = [line.strip() for line in text.split("\n")]
    # Gom các dòng lại nhưng bảo lưu đoạn văn
    cleaned = "\n".join(lines)
    return cleaned.strip()


def detect_section(text: str, current_section: str) -> str:
    """Xác định chuyên mục (section) dựa trên từ khóa trong nội dung trang."""
    upper = text.upper()
    if any(k in upper for k in ["QUY CHẾ ĐÀO TẠO", "HỌC PHẦN", "TÍN CHỈ", "XÉT TỐT NGHIỆP", "CẢNH BÁO HỌC TẬP"]):
        return "dao_tao"
    elif any(k in upper for k in ["THƯ VIỆN", "MƯỢN", "TRẢ TÀI LIỆU", "BỘ SƯU TẬP"]):
        return "thu_vien"
    elif any(k in upper for k in ["KHEN THƯỞNG", "KỶ LUẬT", "RÈN LUYỆN", "CẢNH CÁO", "KHIỂN TRÁCH", "ĐÌNH CHỈ"]):
        return "quan_ly_sinh_vien"
    elif any(k in upper for k in ["HỌC BỔNG", "TRỢ CẤP", "MIỄN GIẢM HỌC PHÍ", "CHÍNH SÁCH"]):
        return "hoc_bong_chinh_sach"
    elif any(k in upper for k in ["KÝ TÚC XÁ", "NỘI TRÚ", "LƯU TRÚ"]):
        return "ky_tuc_xa"
    return current_section


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract each physical page; keep its page number, source, and section metadata.

    Bỏ qua trang bìa (trang 1) và mục lục (trang 2-5) theo quy định trong manifest.
    """
    reader = PdfReader(str(path))
    pages: list[DocumentPage] = []
    current_section = "dao_tao"

    for idx, raw_page in enumerate(reader.pages, start=1):
        # Bỏ qua bìa và mục lục
        if idx == 1 or 2 <= idx <= 5:
            continue

        raw_text = raw_page.extract_text() or ""
        text = normalize_text(raw_text)

        # Bỏ qua trang quá ít nội dung (< 50 ký tự)
        if len(text) < 50:
            continue

        current_section = detect_section(text, current_section)

        pages.append(
            DocumentPage(
                document_id=document_id,
                source=source,
                page=idx,  # Lưu đúng số trang vật lý của PDF để đối chiếu bằng chứng
                text=text,
                metadata={
                    "section": current_section,
                    "char_count": len(text)
                }
            )
        )

    return pages
