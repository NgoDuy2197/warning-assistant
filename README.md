# Warning Assistant

Một ứng dụng thông báo nhẹ, mượt và hiện đại cho Windows.

## 🚀 Chức năng
- Tạo thông báo lặp lại, cố định giờ hoặc ngày cụ thể.
- 4 loại thông báo: Danger, Important, Warning, Info.
- Popup luôn hiển thị trên cùng (Always on top).
- Hỗ trợ Tiếng Việt, Tiếng Anh, Tiếng Trung.
- 2 Giao diện: Mặc định & Màu hồng dễ thương.
- Tự khởi động cùng Windows.
- Lưu trữ dữ liệu JSON.

## 🛠 Cài đặt và Sử dụng

### 1. Cài đặt Python
Đảm bảo bạn đã cài đặt **Python 3.8** trở lên trên máy tính.

### 2. Tải mã nguồn và cài đặt thư viện
Mở terminal (CMD hoặc PowerShell) tại thư mục dự án và chạy các lệnh sau:

```bash
# Cài đặt các thư viện cần thiết
pip install PyQt6 pyinstaller
```

### 3. Chạy ứng dụng từ mã nguồn
Để chạy ứng dụng trực tiếp bằng Python:

```bash
python main.py
```

## 🏗 Build file EXE
Để đóng gói ứng dụng thành một file `.exe` duy nhất, chạy lệnh sau:

```bash
pyinstaller --noconsole --onefile --windowed --name "Assistant" --add-data "i18n;i18n" main.py
```
pyinstaller --noconsole --onefile --windowed --name "Assistant" --icon "ui/images/logo.ico" --add-data "i18n;i18n" --add-data "ui/images;ui/images" main.py

*Lưu ý: Sau khi build, file .exe sẽ nằm trong thư mục `dist`. Hãy copy thư mục `i18n` vào cùng cấp với file .exe nếu bạn không dùng tham số `--add-data` đúng cách.*

## 📂 Cấu trúc dữ liệu (__user_data.txt)
Ví dụ nội dung file:

```json
{
    "notifications": [
        {
            "title": "Uống nước",
            "content": "Đến giờ uống nước rồi!",
            "type": "info",
            "freq": "repeat",
            "time": "",
            "repeat_min": 30,
            "active": true,
            "created_at": "2024-03-20T10:00:00"
        }
    ],
    "settings": {
        "theme": "pink",
        "language": "vi_VN",
        "autostart": true
    }
}
```


# TODO LIST
- [ ] Pick date đẹp hơn
- [ ] Nút điều chỉnh thời gian
- [v] Chỉnh global shortcut