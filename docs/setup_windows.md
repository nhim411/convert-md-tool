# Quản lý Đa phiên bản Python trên Windows

Để phát triển dự án này (yêu cầu Python 3.10 - 3.12) song song với các dự án khác, bạn có 2 giải pháp tối ưu nhất trên Windows:

---

## Cách 1: Sử dụng `py` Launcher (Có sẵn - Khuyên dùng)

Windows đi kèm với **Python Launcher** (`py.exe`) khi bạn cài đặt Python từ trang chủ python.org. Đây là cách đơn giản nhất không cần cài thêm tool.

### 1. Cài đặt nhiều phiên bản
Tải và cài đặt bình thường các bản Python bạn cần (ví dụ 3.10 và 3.12).

### 2. Chọn phiên bản khi tạo venv
Thay vì gõ `python`, hãy dùng `py` để chỉ định phiên bản:

```cmd
REM Kiểm tra các bản đã cài
py --list

REM Tạo venv với Python 3.10 cụ thể
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r app/requirements.txt
python app/main.py

REM Hoặc Python 3.11
py -3.11 -m venv venv
```

Sau khi `activate` venv, lệnh `python` sẽ tự động trỏ đúng vào phiên bản của venv đó.

---

## Cách 2: Sử dụng `pyenv-win` (Chuyên nghiệp)

Nếu bạn quen dùng `pyenv` trên macOS/Linux, hãy dùng `pyenv-win`. Công cụ này giúp đổi version Python dễ dàng ở cấp độ thư mục.

### 1. Cài đặt pyenv-win
Chạy PowerShell (Admin):
```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

### 2. Sử dụng
```cmd
# Cài đặt Python 3.10.11
pyenv install 3.10.11

# Set version cho dự án hiện tại (tạo file .python-version)
cd markdown-converter
pyenv local 3.10.11

# Kiểm tra version
python --version
# Output: Python 3.10.11
```

---

## So sánh

| Tiêu chí | `py` Launcher | `pyenv-win` |
|----------|---------------|-------------|
| **Cài đặt** | Có sẵn | Cần cài thêm |
| **Sử dụng** | `py -3.x` | Tự động theo folder |
| **Quản lý** | Thủ công tải installer | `pyenv install` tự động |
| **Phù hợp** | Dev mới, ít version | Dev chuyên nghiệp, nhiều dự án |

## Khuyến nghị cho dự án này

Sử dụng **Cách 1 (`py` Launcher)** vì đơn giản và Windows hỗ trợ native.

```cmd
# Trong thư mục dự án:
py -3.10 -m venv venv
venv\Scripts\activate
pip install -r app/requirements.txt
```
