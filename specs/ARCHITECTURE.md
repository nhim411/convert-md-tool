# Kiến trúc Ứng dụng

## Sơ đồ Cấu trúc

```
┌─────────────────────────────────────────────────────────┐
│                     main.py                             │
│                  (Application Entry)                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │FileSelector │  │FolderOptions│  │OutputOptions │   │
│  └─────────────┘  └─────────────┘  └──────────────┘   │
│                                                         │
│  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │FormatFilter │  │        ProgressPanel            │  │
│  └─────────────┘  └─────────────────────────────────┘  │
│                                                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │              AIOptions Component                    │  │
│  │  (RAG Chunking, Image Extraction, AI Enrichment)  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                    converter.py                         │
│                  (Conversion Engine)                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  OCRService  │  │  LLMClient   │  │ RAGPipeline  │  │
│  │(markitdown-  │  │   (OpenAI-   │  │ (Chunking +  │  │
│  │    ocr)      │  │  Compatible) │  │  Metadata)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                    markitdown                           │
│                 (Microsoft Library)                     │
│            + markitdown-ocr plugin                     │
└─────────────────────────────────────────────────────────┘
```

## Cấu trúc Thư mục

```
markdown-converter/
├── app/
│   ├── main.py              # Entry point, main window
│   ├── converter.py         # Core conversion logic
│   ├── llm_client.py        # OpenAI-compatible LLM client (text + vision)
│   ├── ocr_service.py       # markitdown-ocr plugin wrapper
│   ├── rag_pipeline.py      # RAG chunking + metadata generation
│   ├── text_processor.py    # Japanese text cleaning
│   ├── excel_cleaner.py     # Excel data cleaning
│   ├── config_manager.py    # App config persistence
│   ├── requirements.txt     # Python dependencies
│   ├── locales/
│   │   ├── __init__.py
│   │   └── vi.py           # Vietnamese labels
│   └── components/
│       ├── __init__.py
│       ├── file_selector.py
│       ├── folder_options.py
│       ├── output_options.py
│       ├── format_filter.py
│       ├── progress_panel.py
│       └── ai_options.py    # AI/RAG configuration UI
├── specs/                   # Documentation
├── .github/
│   └── workflows/          # CI/CD workflows
├── build_mac.sh            # macOS build script
├── build_windows.bat       # Windows build script
├── README.md               # Project README
├── LICENSE                 # MIT License
└── .gitignore
```

## Mô tả Modules

### main.py
- Entry point của ứng dụng
- Khởi tạo CustomTkinter window
- Quản lý layout và theme
- Xử lý conversion workflow

### converter.py
- Wrapper cho markitdown + markitdown-ocr library
- Hỗ trợ single file và batch conversion
- Folder scanning (recursive/non-recursive)
- Progress callbacks
- Error handling
- Orchestrates: OCRService → LLMClient (AI enrichment) → RAGPipeline

### llm_client.py
- Unified OpenAI-compatible LLM client
- Supports any base_url (OpenAI, Azure, Ollama, LM Studio, vLLM, Groq)
- Methods: summarize(), describe_image(), chat(), fetch_models(), test_connection()

### ocr_service.py
- markitdown-ocr plugin wrapper
- Enables LLM Vision OCR for embedded images in PDF/DOCX/PPTX/XLSX
- Falls back to standard markitdown if OCR fails

### rag_pipeline.py
- Token-aware markdown chunking with overlap
- Rich metadata generation (chunk_id, token_count, header_path, prev/next_header)
- JSONL export for RAG ingestion
- YAML frontmatter generation

### components/
Các UI components độc lập:

| Component | Chức năng |
|-----------|-----------|
| `FileSelector` | Chọn file/folder với browse dialog |
| `FolderOptions` | Tùy chọn recursive và depth |
| `OutputOptions` | Cấu hình output directory |
| `FormatFilter` | Checkbox lọc định dạng file |
| `ProgressPanel` | Progress bar và log |
| `AIOptions` | RAG, AI enrichment, OpenAI-compatible config |

### locales/
- Chứa các labels cho giao diện
- Hiện tại hỗ trợ tiếng Việt (vi.py)
- Có thể mở rộng thêm ngôn ngữ khác

## Luồng Xử lý

```
1. User chọn source (file/folder)
         │
         ▼
2. User cấu hình options
   - Recursive?
   - Output path?
   - Formats to include?
         │
         ▼
3. Click "Bắt đầu Chuyển đổi"
         │
         ▼
4. Background thread bắt đầu
         │
         ▼
5. Scan files (nếu folder mode)
         │
         ▼
6. Loop: Convert từng file
   │
   ├──▶ Success: Log ✓
   │
   └──▶ Error: Log ✗, continue
         │
         ▼
7. Hiển thị tổng kết
```

## Threading Model

- UI chạy trên main thread
- Conversion chạy trên background thread
- Communication qua `after()` callbacks
- Có thể dừng conversion bằng stop flag
