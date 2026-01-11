# Tech Stack

## Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.10+ | Primary development language |
| Conversion Engine | markitdown | 0.1.4+ | Microsoft's file-to-Markdown converter |
| GUI Framework | CustomTkinter | 5.2.0+ | Modern cross-platform GUI |
| Image Processing | Pillow | 10.0.0+ | Image handling support |
| Packaging | PyInstaller | 6.0+ | Create standalone executables |

## Why These Choices?

### Python
- Cross-platform compatibility
- Rich ecosystem for file processing
- Easy integration with markitdown library

### CustomTkinter
- Modern, beautiful widgets out-of-the-box
- Native dark/light mode support
- Pure Python, no external dependencies
- Consistent look across Windows/macOS
- Based on stable Tkinter foundation

### markitdown
- Official Microsoft library
- Supports wide range of formats
- Active development and maintenance
- Good documentation

### PyInstaller
- Creates single executable or folder
- Works on Windows and macOS
- No runtime dependencies for end user
- Well-documented and mature

## Dependencies

### Production
```
markitdown[all]>=0.1.0
customtkinter>=5.2.0
Pillow>=10.0.0
```

### Development
```
pyinstaller>=6.0
```

## System Requirements

### Development
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Runtime (Packaged App)
- Windows 10/11 (64-bit)
- macOS 10.15 Catalina or newer (Intel or Apple Silicon)
