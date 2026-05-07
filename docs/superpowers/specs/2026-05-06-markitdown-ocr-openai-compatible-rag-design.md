# Design: Tích hợp markitdown-ocr + OpenAI-Compatible + RAG Improvements

**Date:** 2026-05-06
**Author:** Claude
**Status:** Draft

---

## 1. Tổng quan

Project convert-md-tool mở rộng với 3 cải tiến chính:

1. **markitdown-ocr plugin** – LLM Vision OCR cho ảnh trong tài liệu
2. **OpenAI-compatible provider** – hỗ trợ mọi OpenAI-compatible endpoint
3. **Enhanced RAG pipeline** – chunking thông minh + metadata phong phú

## 2. User Choices

| Question | Choice |
|----------|--------|
| LLM Provider | OpenAI-compatible only |
| RAG Features | Pipeline cơ bản + Metadata |
| Refactor Scope | Refactor vừa phải |
| OCR Strategy | Thay hoàn toàn bằng markitdown-ocr |

## 3. Kiến trúc Module

```
app/
├── main.py                    # Giữ nguyên
├── converter.py               # Thu hẹp: orchestration + service calls
├── config_manager.py          # base_url, api_key, model (bỏ gemini_*)
├── llm_client.py              # NEW: unified OpenAI-compatible client
├── ocr_service.py             # NEW: markitdown-ocr wrapper
├── rag_pipeline.py            # NEW: chunking + metadata
├── text_processor.py          # Giữ nguyên
├── excel_cleaner.py           # Giữ nguyên
├── image_handler.py           # DELETE (thay bằng ocr_service)
├── ai_helper.py               # DELETE (hợp nhất vào llm_client)
└── components/
    └── ai_options.py          # Cập nhật UI
```

## 4. Chi tiết Module

### 4.1 LLMClient (llm_client.py)

```python
class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def summarize(self, text: str) -> dict:
        """Gọi LLM với prompt summarize, trả về dict summary + keywords."""

    def describe_image(self, image_bytes: bytes, prompt: str) -> str:
        """Gọi Vision API để mô tả ảnh."""

    def chat(self, messages: list) -> str:
        """Generic chat completion."""

    @staticmethod
    def fetch_models(base_url: str, api_key: str) -> list[str]:
        """GET /models từ base_url, trả về list model names."""
```

### 4.2 OCRService (ocr_service.py)

```python
class OCRService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def convert_with_ocr(self, file_path: str) -> str:
        md = MarkItDown(
            enable_plugins=True,
            llm_client=self.llm_client.client,
            llm_model=self.llm_client.model,
        )
        return md.convert(file_path).text_content
```

markitdown-ocr plugin tự động extract ảnh + gọi LLM Vision + chèn OCR text vào markdown.

### 4.3 RAGPipeline (rag_pipeline.py)

```python
@dataclass
class Chunk:
    chunk_id: str
    source_file: str
    chunk_index: int
    header: str
    header_path: str
    content: str
    level: int
    token_count: int
    char_count: int
    prev_header: str
    next_header: str
    tags: list[str]

class RAGPipeline:
    def chunk(self, markdown: str, source_file: str,
              overlap: int = 50, max_tokens: int = 512) -> list[Chunk]: ...

    def generate_metadata(self, markdown: str, source_file: str,
                          ai_summary: str | None = None) -> dict: ...

    def save_jsonl(self, chunks: list[Chunk], output_path: str) -> None: ...
```

### 4.4 Converter (converter.py) – Refactored

```python
class MarkdownConverter:
    def __init__(self):
        self.llm_client = None
        self.ocr_service = None
        self.rag_pipeline = RAGPipeline()

    def _get_services(self):
        if self.ocr_service is None:
            cfg = self.config
            self.llm_client = LLMClient(cfg.base_url, cfg.api_key, cfg.model)
            self.ocr_service = OCRService(self.llm_client)
        return self.ocr_service

    def convert_file(self, source_path: Path, options: AIOptions) -> ConversionResult:
        ocr = self._get_services()
        markdown = ocr.convert_with_ocr(str(source_path))

        if options.excel_clean_enabled:
            markdown = self._preprocess_excel(source_path, markdown)

        markdown = self._optimize_text(markdown)

        if options.summary_enabled and self.llm_client:
            summary = self.llm_client.summarize(markdown[:8000])
            markdown = self._add_frontmatter(markdown, summary)

        if options.chunk_enabled:
            chunks = self.rag_pipeline.chunk(markdown, str(source_path))
            jsonl_path = output_path.with_suffix('.jsonl')
            self.rag_pipeline.save_jsonl(chunks, jsonl_path)

        output_path.write_text(markdown, encoding='utf-8')
```

## 5. Config Changes

```python
# Before
ai_provider: str = "openai"
openai_api_key: str = ""
gemini_api_key: str = ""
openai_model: str = "gpt-4o-mini"
gemini_model: str = "gemini-1.5-flash"

# After
base_url: str = "https://api.openai.com/v1"
api_key: str = ""
model: str = "gpt-4o-mini"
```

## 6. UI Changes

```
--- OpenAI-Compatible Configuration ---
  Base URL: [https://api.openai.com/v1 _______________]
  API Key:  [••••••••________________________]
  Model:    [gpt-4o-mini ▼]  [🔄 Refresh]

  [Test Connection]

--- Features ---
[RAG & Chunking]
[X] Smart Chunking (Header-based)
[X] Clean Excel Data

[Images]
[X] Extract & OCR images (markitdown-ocr)

[AI Enrichment]
[X] Summarize & Generate Keywords
```

## 7. YAML Frontmatter (Enhanced)

```yaml
---
source_file: report.pdf
converted_at: 2026-05-06T10:30:00
total_chunks: 12
total_tokens: 4821
ai_summary: |
  Báo cáo tài chính Q4 2024 với doanh thu tăng 20%.
ai_keywords:
  - quarterly-report
  - financial
document_type: financial-report
language: vi
---
```

## 8. JSONL Output Format

```json
{"chunk_id":"a1b2c3d4","source_file":"report.pdf","chunk_index":0,"header":"# Introduction","header_path":"# Introduction","content":"...","level":1,"token_count":142,"char_count":890,"prev_header":"","next_header":"## Background","tags":["intro"]}
```

## 9. Dependencies

```diff
+ markitdown-ocr>=0.1.0
```

## 10. Migration

Existing users with `gemini_api_key` set: show one-time migration dialog pre-filling `base_url` with `https://api.openai.com/v1`.

## 11. Error Handling

| Scenario | Behavior |
|----------|----------|
| markitdown-ocr LLM error | Log warning, continue with standard conversion |
| Invalid base_url | Show error in UI before conversion starts |
| API key invalid | Show connection test failure, allow retry |
| Large PDF (300 DPI) | Show per-page progress |
| Ollama offline | Fallback: "Ollama không khả dụng. Kiểm tra base URL." |

## 12. Test Coverage

| Module | Tests |
|--------|-------|
| LLMClient | test_summarize, test_describe_image, test_fetch_models |
| OCRService | test_convert_pdf_with_images, test_fallback_on_error |
| RAGPipeline | test_chunk_by_header, test_token_count, test_jsonl_output |
| Converter | test_orchestration_flow |
