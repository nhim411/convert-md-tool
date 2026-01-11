# Giải pháp xử lý ảnh khi convert sang Markdown

## Vấn đề

Khi convert tài liệu (PDF, Word, PowerPoint) chứa ảnh sang Markdown:
- Nội dung text được chuyển đổi thành công
- **Ảnh bị mất** vì Markdown chỉ là text thuần

→ AI agent đọc file .md sẽ không biết nội dung ảnh

---

## Các giải pháp

### 1. Trích xuất ảnh + Mô tả bằng AI (Khuyến nghị ✅)

**Mô tả:**
- Trích xuất ảnh từ tài liệu ra thư mục riêng
- Sử dụng AI Vision (GPT-4o, Gemini) để mô tả nội dung ảnh
- Chèn mô tả vào file Markdown

**Ví dụ output:**
```markdown
## Hình 1: Biểu đồ doanh thu

![Biểu đồ doanh thu Q4 2024](./images/chart_001.png)

> **Mô tả AI:** Biểu đồ cột thể hiện doanh thu 4 quý năm 2024.
> Q1: 150M, Q2: 180M, Q3: 210M, Q4: 250M.
> Xu hướng tăng trưởng ổn định ~20% mỗi quý.
```

**Ưu điểm:**
- AI agent có thể đọc được nội dung ảnh
- Giữ được file ảnh gốc để reference
- Linh hoạt tùy chọn mức độ chi tiết mô tả

**Nhược điểm:**
- Cần API key AI (GPT-4o, Gemini)
- Tốn thời gian và chi phí API
- Độ chính xác phụ thuộc model

---

### 2. Trích xuất ảnh + Reference path

**Mô tả:**
- Trích xuất ảnh vào thư mục `images/`
- Markdown reference bằng relative path

**Ví dụ output:**
```markdown
![](./images/page_1_image_001.png)
![](./images/page_2_chart_001.png)
```

**Cấu trúc thư mục:**
```
document.md
images/
├── page_1_image_001.png
├── page_2_chart_001.png
└── ...
```

**Ưu điểm:**
- Đơn giản, không cần AI
- Giữ nguyên ảnh gốc
- AI có thể đọc path để biết có ảnh

**Nhược điểm:**
- AI không biết nội dung ảnh
- Cần giữ folder images cùng md file

---

### 3. Embed Base64 trực tiếp

**Mô tả:**
- Convert ảnh sang Base64
- Embed trực tiếp vào Markdown

**Ví dụ:**
```markdown
![Chart](data:image/png;base64,iVBORw0KGgoAAAANSUhEU...)
```

**Ưu điểm:**
- File MD tự chứa hoàn toàn (portable)
- Không cần thư mục ảnh riêng

**Nhược điểm:**
- File size rất lớn
- AI vẫn không đọc được nội dung ảnh
- Không phải tất cả viewer hỗ trợ

---

### 4. OCR cho ảnh chứa text

**Mô tả:**
- Nhận diện ảnh chứa text (screenshot, scan)
- Dùng OCR để extract text
- Thêm text vào markdown

**Ví dụ:**
```markdown
![Screenshot](./images/screenshot_001.png)

> **Text trong ảnh:**
> User Name: admin
> Status: Active
> Last Login: 2024-01-10
```

**Ưu điểm:**
- Recover text từ ảnh scan/screenshot
- AI có thể đọc được nội dung

**Nhược điểm:**
- Chỉ hữu ích với ảnh chứa text
- Không áp dụng cho biểu đồ, hình minh họa

---

## Đề xuất Implementation

### Giải pháp tối ưu: Kết hợp (1) + (2) + (4)

```
┌─────────────────────────────────────────────┐
│           Convert Document                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│        Trích xuất ảnh → images/             │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│   Phân loại ảnh:                            │
│   - Ảnh có text → OCR                       │
│   - Biểu đồ/Chart → AI Vision describe      │
│   - Hình minh họa → AI Vision describe      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│   Markdown output:                          │
│   - Reference ảnh gốc                       │
│   - Kèm mô tả/OCR text                      │
└─────────────────────────────────────────────┘
```

### Options cho user

| Option | Description | Use Case |
|--------|-------------|----------|
| `--extract-images` | Chỉ trích xuất ảnh, không mô tả | Nhanh, không cần API |
| `--describe-images` | Trích xuất + AI mô tả | Đầy đủ nhất, cần API |
| `--ocr-only` | Chỉ OCR ảnh chứa text | Cho tài liệu scan |
| `--no-images` | Bỏ qua ảnh hoàn toàn | Nhẹ nhất |

---

## Thay đổi cần thiết

### 1. Thêm dependencies
```
# Image extraction
pdf2image          # PDF images
python-pptx        # (đã có) PPTX images
python-docx        # (đã có) DOCX images
Pillow            # (đã có) Image processing

# OCR
pytesseract       # Local OCR
# hoặc sử dụng Azure/Google Vision API

# AI Vision (optional)
openai            # GPT-4o Vision
google-generativeai  # Gemini Vision
```

### 2. Thêm config
```python
IMAGE_OPTIONS = {
    'extract': True,          # Trích xuất ảnh
    'describe': False,        # AI mô tả (cần API key)
    'ocr': False,            # OCR text trong ảnh
    'output_dir': 'images',  # Thư mục output ảnh
    'ai_provider': 'openai', # 'openai' hoặc 'gemini'
}
```

### 3. UI mới
- Checkbox: "Trích xuất ảnh từ tài liệu"
- Checkbox: "Mô tả ảnh bằng AI" (yêu cầu API key)
- Checkbox: "OCR ảnh chứa text"
- Input: API Key (nếu cần)

---

## Kết luận

Để AI agent có thể "đọc" được ảnh trong tài liệu:

| Mục tiêu | Giải pháp |
|----------|-----------|
| Tốc độ nhanh, không cần AI | Extract + reference path |
| AI hiểu được nội dung ảnh | Extract + AI Vision describe |
| Tài liệu scan có text | Extract + OCR |
| Đầy đủ nhất | Kết hợp cả 3 |

**Khuyến nghị:** Implement giải pháp kết hợp với options cho user lựa chọn tùy nhu cầu.
