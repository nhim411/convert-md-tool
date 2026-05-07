# Xử lý Ảnh trong tài liệu - markitdown-ocr

## Cách tiếp cận mới: markitdown-ocr

### Giới thiệu

**markitdown-ocr** là plugin chính thức của Microsoft cho markitdown, sử dụng LLM Vision để:
- Trích xuất text từ ảnh embedded trong PDF/DOCX/PPTX/XLSX
- Mô tả nội dung ảnh bằng AI (GPT-4o, Claude, hoặc bất kỳ model nào hỗ trợ vision)
- Hỗ trợ **OpenAI-compatible API** - có thể dùng Azure OpenAI, Ollama, LM Studio, vLLM, Groq...

### Cách hoạt động

```python
from markitdown import MarkItDown
from openai import OpenAI

# OpenAI-compatible client - ví dụ dùng Azure, Ollama, hoặc OpenAI
client = OpenAI(
    base_url="https://api.openai.com/v1",  # hoặc Azure, Ollama, v.v.
    api_key="your-api-key"
)

md = MarkItDown(
    enable_plugins=True,
    llm_client=client,
    llm_model="gpt-4o-mini"
)

result = md.convert("document.pdf")
print(result.text_content)
```

### Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| OCR Vision | Trích xuất text từ ảnh trong tài liệu |
| AI Description | Tự động mô tả nội dung ảnh |
| OpenAI-Compatible | Hỗ trợ bất kỳ OpenAI-compatible endpoint nào |
| Fallback | Tự động fallback sang markitdown standard nếu OCR fail |

### Supported Formats

- PDF (embedded images)
- DOCX/DOC (embedded images)
- PPTX/PPT (embedded images)
- XLSX/XLS (embedded images)

### Configuration

```python
# User config in app
AIOptions:
  base_url: str = "https://api.openai.com/v1"  # OpenAI, Azure, Ollama, v.v.
  api_key: str = ""
  model: str = "gpt-4o-mini"  # vision-capable model
  extract_images: bool = False  # extract images to folder
```

---

## Các giải pháp trước đây (legacy)

### 1. Trích xuất ảnh + Mô tả bằng AI

**Mô tả:**
- Trích xuất ảnh từ tài liệu ra thư mục riêng
- Sử dụng AI Vision (GPT-4o) để mô tả nội dung ảnh
- Chèn mô tả vào file Markdown

### 2. Trích xuất ảnh + Reference path

**Mô tả:**
- Trích xuất ảnh vào thư mục `images/`
- Markdown reference bằng relative path

### 3. Embed Base64 trực tiếp

**Mô tả:**
- Convert ảnh sang Base64
- Embed trực tiếp vào Markdown

### 4. OCR cho ảnh chứa text

**Mô tả:**
- Nhận diện ảnh chứa text (screenshot, scan)
- Dùng OCR để extract text

---

## Đề xuất Implementation

### Giải pháp tối ưu: markitdown-ocr + RAG metadata

```
┌─────────────────────────────────────────────┐
│           Convert Document                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│        markitdown-ocr Plugin                │
│   (LLM Vision OCR for embedded images)      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│   Markdown output with OCR text:            │
│   - OCR text from images                    │
│   - AI descriptions (if enabled)             │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│   RAG Pipeline (optional):                  │
│   - Smart chunking by headers               │
│   - Rich metadata (chunk_id, token_count)   │
│   - JSONL export for RAG ingestion          │
└─────────────────────────────────────────────┘
```

### Options cho user

| Option | Description | Use Case |
|--------|-------------|----------|
| `extract_images` | Trích xuất ảnh ra folder riêng | Reference sau này |
| `chunk_enabled` | RAG smart chunking + JSONL export | Build RAG knowledge base |
| `summary_enabled` | AI summarize + keywords | Quick document overview |
| `excel_clean_enabled` | Clean Excel forward-fill | Excel data processing |

### API Configuration

```
--- OpenAI-Compatible Configuration ---
  Base URL: [https://api.openai.com/v1 _______________] (hoặc Azure, Ollama, v.v.)
  API Key:  [••••••••________________________]
  Model:    [gpt-4o-mini ▼]  [🔄 Refresh]
  Status:   ✅ Connected
```

---

## Dependencies

```
# Core
markitdown>=0.1.0
markitdown-ocr>=0.1.0    # NEW: Official Microsoft LLM Vision OCR plugin

# AI (optional)
openai>=1.0.0            # OpenAI SDK - hỗ trợ OpenAI-compatible

# For building
pyinstaller
```

---

## Kết luận

**markitdown-ocr** thay thế hoàn toàn các giải pháp xử lý ảnh legacy:
- OCR Vision tích hợp sẵn trong markitdown
- OpenAI-compatible - không giới hạn provider
- Fallback tự động nếu OCR fail
- Kết hợp RAG pipeline cho document intelligence
