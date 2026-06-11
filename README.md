# Markdown Converter

Ứng dụng desktop chuyển đổi các định dạng file sang Markdown.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## 🤖 Tính năng AI (tùy chọn)

- **markitdown-ocr**: Trích xuất text từ ảnh trong tài liệu bằng LLM Vision
- **OpenAI-Compatible**: Hỗ trợ Azure OpenAI, Ollama, LM Studio, vLLM, Groq...
- **RAG Pipeline**: Smart chunking theo header, metadata phong phú, JSONL export
- **AI Summarization**: Tự động tạo tóm tắt và keywords cho document
- **Excel Cleaning**: Forward-fill data cleaning cho Excel files

### Yêu cầu AI

Cần có API key từ OpenAI-compatible provider để sử dụng tính năng AI. Không bắt buộc - ứng dụng vẫn hoạt động normal nếu không có API key.

## ✨ Tính năng

- 📄 Hỗ trợ nhiều định dạng: PDF, Word, PowerPoint, Excel, hình ảnh, âm thanh, HTML, CSV/JSON/XML, ZIP, EPub
- 📁 Chuyển đổi file đơn hoặc cả thư mục
- 🔄 Hỗ trợ chuyển đổi thư mục con (recursive)
- 🎯 Lọc định dạng file cần chuyển đổi
- 📤 Xuất ra vị trí tùy chỉnh hoặc tại chỗ
- ⚠️ **Mới:** Tùy chọn giữ nguyên hoặc ghi đè file cũ
- 🌙 Dark/Light theme
- 🇻🇳 Giao diện tiếng Việt
- 💻 **Mới:** Giao diện dòng lệnh (CLI) cho tự động hóa & xử lý hàng loạt

## � Yêu cầu Hệ thống

Để chạy từ mã nguồn hoặc đóng gói ứng dụng, bạn cần:

- **Python**: Phiên bản **3.10** đến **3.12** (Khuyên dùng 3.11 để tương thích tốt nhất)
- **Hệ điều hành**: Windows 10/11 hoặc macOS 10.15+

## �📥 Cài đặt & Chạy từ Source

### 1. Chuẩn bị môi trường

Đảm bảo bạn đã cài đặt Python và Git. Kiểm tra bằng dòng lệnh:
```bash
python --version  # Nên là Python 3.10+
git --version
```

### 2. Clone và Cài đặt

#### Windows
```cmd
git clone https://github.com/yourusername/markdown-converter.git
cd markdown-converter

# Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate

# Cài đặt thư viện
pip install -r app/requirements.txt

# Chạy ứng dụng
python app/main.py
```

#### macOS
```bash
git clone https://github.com/yourusername/markdown-converter.git
cd markdown-converter

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt thư viện
pip install -r app/requirements.txt

# Chạy ứng dụng
python app/main.py
```

## 💻 Sử dụng Command Line (CLI)

Ngoài giao diện đồ họa, ứng dụng còn có CLI để chuyển đổi không cần mở GUI — phù hợp cho tự động hóa, script và xử lý hàng loạt.

Có hai cách gọi CLI tương đương nhau:

```bash
python app/cli.py <input> [tùy chọn]
# hoặc (main.py tự nhận diện: có tham số -> CLI, không tham số -> mở GUI)
python app/main.py <input> [tùy chọn]
```

### Ví dụ nhanh

```bash
# Chuyển đổi một file (xuất .md cùng thư mục với file gốc)
python app/cli.py document.pdf

# Chuyển đổi cả thư mục, quét thư mục con, xuất ra ./out
python app/cli.py ./docs --recursive -o ./out

# Chỉ chuyển đổi PDF và Word trong thư mục
python app/cli.py ./docs --formats pdf,word

# Ghi đè file .md đã tồn tại
python app/cli.py report.xlsx --overwrite

# Xuất kết quả dạng JSON (dùng cho script)
python app/cli.py document.pdf --json

# Bật tính năng AI (OCR + tóm tắt). Nên đặt API key qua biến môi trường
export MD_API_KEY="sk-..."        # Windows: set MD_API_KEY=sk-...
python app/cli.py scan.pdf --ocr --summary --extract-images
```

### Các tùy chọn

| Tùy chọn | Mô tả |
|----------|-------|
| `input` | Đường dẫn tới file hoặc thư mục cần chuyển đổi (bắt buộc) |
| `-o`, `--output DIR` | Thư mục xuất (mặc định: cùng vị trí với file gốc) |
| `-r`, `--recursive` | Quét cả thư mục con (chỉ áp dụng cho thư mục) |
| `--max-depth N` | Giới hạn độ sâu khi quét đệ quy |
| `-f`, `--formats` | Lọc định dạng, phân tách bằng dấu phẩy: `pdf,word,powerpoint,excel,images,text` |
| `--overwrite` | Ghi đè file `.md` đã tồn tại (mặc định: bỏ qua) |
| `--json` | In kết quả dưới dạng JSON |
| `-q`, `--quiet` | Chỉ in lỗi và dòng tóm tắt cuối |
| `-h`, `--help` | Hiển thị toàn bộ trợ giúp |

**Tùy chọn AI** (cần API key):

| Tùy chọn | Mô tả |
|----------|-------|
| `--extract-images` | Trích xuất hình ảnh từ PDF/DOCX/PPTX |
| `--ocr` | Bật OCR mô tả ảnh bằng LLM Vision |
| `--chunk` | Tạo file `.jsonl` phân mảnh cho RAG |
| `--excel-clean` | Làm sạch file Excel (gỡ merge cell) trước khi chuyển đổi |
| `--summary` | Sinh tóm tắt + từ khóa bằng AI |
| `--api-key KEY` | API key (hoặc đặt biến môi trường `MD_API_KEY` — an toàn hơn) |
| `--base-url URL` | Base URL tương thích OpenAI (mặc định `https://api.openai.com/v1`) |
| `--model NAME` | Tên model (mặc định `gpt-4o-mini`) |

### Mã thoát (exit code)

| Mã | Ý nghĩa |
|----|---------|
| `0` | Tất cả file chuyển đổi thành công (hoặc được bỏ qua) |
| `1` | Có ít nhất một file lỗi |
| `2` | Lỗi tham số (không tìm thấy đường dẫn, định dạng không hợp lệ) |

> **Lưu ý khi dùng bản đóng gói:** file `.exe`/`.app` hiện được build ở chế độ windowed (không có console) nên sẽ không hiển thị output CLI. Để dùng CLI, hãy chạy `python app/cli.py ...` từ mã nguồn.

## hammer_and_wrench: Đóng gói (Build EXE/App)

### Windows (Tạo file .exe)

Dự án đã bao gồm script tự động build cho Windows.

1. Mở Command Prompt (cmd) hoặc PowerShell tại thư mục dự án.
2. Đảm bảo đã activate venv (`venv\Scripts\activate`).
3. Chạy lệnh:
```cmd
build_windows.bat
```
4. Sau khi hoàn tất, file chạy sẽ nằm tại: `dist\MarkdownConverter\MarkdownConverter.exe`

> **Lưu ý:** Script sẽ tự động cài đặt `pyinstaller` và thực hiện các bước tối ưu dung lượng.

### macOS (Tạo file .app)

```bash
chmod +x build_mac.sh
./build_mac.sh
```
File ứng dụng sẽ nằm trong thư mục `dist/`.

## 📖 Tài liệu

- [Yêu cầu thiết kế](specs/README.md)
- [Tech Stack](specs/TECH_STACK.md)
- [Kiến trúc](specs/ARCHITECTURE.md)

## 📋 Định dạng hỗ trợ

| Loại | Extensions |
|------|------------|
| Documents | `.pdf`, `.docx`, `.doc`, `.pptx`, `.ppt`, `.xlsx`, `.xls` |
| Media | `.jpg`, `.png`, `.gif`, `.mp3`, `.wav` |
| Web | `.html`, `.htm` |
| Data | `.csv`, `.json`, `.xml`, `.txt` |
| Other | `.zip`, `.epub` |

## 🛠️ Công nghệ

- [markitdown](https://github.com/microsoft/markitdown) - Microsoft's conversion library
- [markitdown-ocr](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-ocr) - LLM Vision OCR plugin
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [PyInstaller](https://pyinstaller.org/) - Application packaging
- [OpenAI SDK](https://github.com/openai/openai-python) - OpenAI-compatible API client

## 📄 License

MIT License - xem file [LICENSE](LICENSE)
