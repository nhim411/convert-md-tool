# Hướng dẫn Release

## Tạo Release mới

### 1. Cập nhật version

Quy ước versioning: `vMAJOR.MINOR.PATCH` (ví dụ: v1.0.0, v1.1.0, v1.0.1)

### 2. Commit changes

```bash
git add .
git commit -m "Release v1.0.0"
```

### 3. Tạo tag

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
```

### 4. Push to GitHub

```bash
git push origin main
git push origin v1.0.0
```

### 5. GitHub Actions tự động build

Khi push tag có format `v*`:
- Build Windows executable
- Build macOS app bundle
- Tạo Release với 2 file ZIP

## Build thủ công (Local)

### macOS

```bash
chmod +x build_mac.sh
./build_mac.sh
# Output: dist/MarkdownConverter.app
```

### Windows

```cmd
build_windows.bat
# Output: dist\MarkdownConverter\MarkdownConverter.exe
```

## Cấu trúc Release

```
MarkdownConverter-windows.zip
├── MarkdownConverter/
│   ├── MarkdownConverter.exe
│   ├── _internal/
│   └── locales/

MarkdownConverter-macos.zip
├── MarkdownConverter.app/
│   └── Contents/
│       ├── MacOS/
│       ├── Resources/
│       └── Info.plist
```
