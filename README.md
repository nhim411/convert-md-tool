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
