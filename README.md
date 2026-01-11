# Markdown Converter

Ứng dụng desktop chuyển đổi các định dạng file sang Markdown.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Tính năng

- 📄 Hỗ trợ nhiều định dạng: PDF, Word, PowerPoint, Excel, hình ảnh, âm thanh, HTML, CSV/JSON/XML, ZIP, EPub
- 📁 Chuyển đổi file đơn hoặc cả thư mục
- 🔄 Hỗ trợ chuyển đổi thư mục con (recursive)
- 🎯 Lọc định dạng file cần chuyển đổi
- 📤 Xuất ra vị trí tùy chỉnh
- 🌙 Dark/Light theme
- 🇻🇳 Giao diện tiếng Việt

## 📥 Cài đặt

### Tải bản build sẵn

Tải file cài đặt từ [Releases](../../releases):
- **Windows**: `MarkdownConverter-windows.zip`
- **macOS**: `MarkdownConverter-macos.zip`

### Chạy từ source

```bash
# Clone repository
git clone https://github.com/yourusername/markdown-converter.git
cd markdown-converter

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r app/requirements.txt

# Chạy ứng dụng
python app/main.py
```

## 🔨 Build

### macOS
```bash
chmod +x build_mac.sh
./build_mac.sh
```

### Windows
```cmd
build_windows.bat
```

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
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [PyInstaller](https://pyinstaller.org/) - Application packaging

## 📄 License

MIT License - xem file [LICENSE](LICENSE)
