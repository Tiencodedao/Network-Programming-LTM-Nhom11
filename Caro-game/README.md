# Caro LAN Game - Modular Structure

## 📁 Cấu trúc dự án

```
Caro-game/
├── main.py                 # File chính để chạy game
├── config.py              # Cấu hình (đã có sẵn)
├── gui.py                 # File cũ (backup, không dùng nữa)
│
├── models/                # Logic game và dữ liệu
│   ├── __init__.py
│   ├── game_state.py     # Quản lý bàn cờ, memory, win logic
│   └── player.py         # Thông tin người chơi
│
├── network/              # Xử lý mạng
│   ├── __init__.py
│   ├── discovery.py     # UDP broadcast tìm phòng
│   ├── server.py        # TCP server logic
│   └── client.py        # TCP client logic
│
├── ui/                   # Giao diện người dùng
│   ├── __init__.py
│   ├── main_window.py   # Cửa sổ chính
│   ├── board.py         # Component bàn cờ
│   └── sidebar.py       # Component thanh bên
│
└── utils/               # Các tiện ích
    ├── __init__.py
    ├── timer.py        # Thread-safe countdown
    └── validator.py    # Validate input
```

## 🚀 Cách chạy

### Chạy với cấu trúc mới:
```bash
python main.py
```

### Chạy file cũ (backup):
```bash
python gui.py
```

## ✨ Ưu điểm của cấu trúc mới

1. **Tách biệt concerns**: UI, logic game, network riêng biệt
2. **Dễ maintain**: Mỗi file 50-150 dòng thay vì 500+ dòng
3. **Dễ test**: Có thể test từng module độc lập
4. **Dễ mở rộng**: Thêm tính năng không ảnh hưởng module khác
5. **Dễ làm việc nhóm**: Mỗi người phụ trách 1 module

## 📝 Các class chính

### Models
- `GameState`: Quản lý trạng thái bàn cờ, memory, kiểm tra thắng
- `Player`: Thông tin người chơi (role, timer)

### Network
- `DiscoveryService`: Tìm kiếm phòng qua UDP broadcast
- `GameServer`: Xử lý logic server TCP
- `GameClient`: Xử lý logic client TCP

### UI
- `CaroWindow`: Cửa sổ chính tích hợp tất cả
- `BoardWidget`: Component hiển thị bàn cờ
- `SidebarWidget`: Component thanh bên (buttons, timer, status)

### Utils
- `CountdownTimer`: Timer thread-safe với callback
- `InputValidator`: Validate input (room code, IP, port)

## 🔧 Tính năng đã cải thiện

1. ✅ Sửa lỗi logic kiểm tra thắng (không đếm trùng điểm xuất phát)
2. ✅ Tách class thành modules rõ ràng
3. ✅ Thread-safe với các shared state
4. ✅ Cleanup resources (socket, thread)
5. ✅ Callbacks rõ ràng giữa các layer
6. ✅ Code dễ đọc và maintain hơn

## 📚 Hướng dẫn phát triển tiếp

### Thêm tính năng mới:
1. **Thêm UI component**: Tạo file trong `ui/`
2. **Thêm game logic**: Sửa trong `models/`
3. **Thêm network feature**: Sửa trong `network/`
4. **Thêm utility**: Tạo file trong `utils/`

### Ví dụ: Thêm chat feature
```
network/chat.py        # Logic chat
ui/chat_widget.py      # UI chat box
```

## ⚠️ Lưu ý

- File `gui.py` được giữ lại như backup
- Chạy `main.py` để sử dụng cấu trúc mới
- Tất cả tính năng game đều hoạt động như cũ

