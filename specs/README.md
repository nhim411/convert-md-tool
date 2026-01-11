# Markdown Converter - Tài liệu Dự án

## Tổng quan

**Markdown Converter** là ứng dụng desktop cross-platform để chuyển đổi các định dạng file (PDF, Word, Excel, PowerPoint, hình ảnh, âm thanh, v.v.) sang định dạng Markdown.

Ứng dụng sử dụng thư viện [markitdown](https://github.com/microsoft/markitdown) của Microsoft làm core conversion engine.

## Yêu cầu Thiết kế

### Chức năng chính

1. **Chọn nguồn chuyển đổi**
   - Hỗ trợ chọn file đơn hoặc thư mục
   - Khi chọn thư mục: tùy chọn bao gồm thư mục con (recursive)
   - Độ sâu recursive: 1 cấp hoặc tất cả các cấp

2. **Cài đặt đầu ra**
   - Mặc định: xuất file .md cùng vị trí với file nguồn
   - Tùy chọn: xuất ra thư mục khác

3. **Lọc định dạng file**
   - Checkbox cho từng loại định dạng
   - Nút "Chọn tất cả" / "Bỏ chọn tất cả"
   - Mặc định: tất cả định dạng được chọn

4. **Hiển thị tiến trình**
   - Progress bar tổng thể
   - Log chi tiết từng file (thành công/thất bại)
   - Có thể dừng giữa chừng

5. **Giao diện**
   - Dark/Light theme toggle
   - Giao diện tiếng Việt
   - Responsive, thân thiện người dùng

### Yêu cầu phi chức năng

- Cross-platform: Windows 10/11 và macOS
- Error handling: không crash khi gặp file lỗi
- Clean code, DRY principles
- Có thể build thành executable độc lập

## Định dạng File Hỗ trợ

| Định dạng | Extensions |
|-----------|------------|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| PowerPoint | `.pptx`, `.ppt` |
| Excel | `.xlsx`, `.xls` |
| Hình ảnh | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff` |
| Âm thanh | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| HTML | `.html`, `.htm` |
| Text/Data | `.csv`, `.json`, `.xml`, `.txt` |
| Archives | `.zip` |
| eBooks | `.epub` |
