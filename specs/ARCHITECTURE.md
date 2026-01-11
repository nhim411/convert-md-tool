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
├─────────────────────────────────────────────────────────┤
│                    converter.py                         │
│                  (Conversion Engine)                    │
├─────────────────────────────────────────────────────────┤
│                    markitdown                           │
│                 (Microsoft Library)                     │
└─────────────────────────────────────────────────────────┘
```

## Cấu trúc Thư mục

```
markdown-converter/
├── app/
│   ├── main.py              # Entry point, main window
│   ├── converter.py         # Core conversion logic
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
│       └── progress_panel.py
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
- Wrapper cho markitdown library
- Hỗ trợ single file và batch conversion
- Folder scanning (recursive/non-recursive)
- Progress callbacks
- Error handling

### components/
Các UI components độc lập:

| Component | Chức năng |
|-----------|-----------|
| `FileSelector` | Chọn file/folder với browse dialog |
| `FolderOptions` | Tùy chọn recursive và depth |
| `OutputOptions` | Cấu hình output directory |
| `FormatFilter` | Checkbox lọc định dạng file |
| `ProgressPanel` | Progress bar và log |

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
