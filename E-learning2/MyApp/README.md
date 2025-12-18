# UDP CLIENT-SERVER COMMUNICATION

## 📋 GIỚI THIỆU

Ứng dụng UDP Client-Server đơn giản với các tính năng:
- ✅ **Sequence Numbering** - Đánh số thứ tự gói tin
- ✅ **ACK Mechanism** - Xác nhận nhận gói tin  
- ✅ **Retransmission** - Truyền lại khi timeout (retry)
- ✅ **In-order Delivery** - Xử lý dữ liệu theo đúng thứ tự
- ✅ **Buffer Management** - Buffer các gói đến không đúng thứ tự
- ✅ **Menu Interface** - Chọn Client hoặc Server từ 1 chương trình

---

## 📁 CẤU TRÚC PROJECT

```
MyApp/
├── Program.cs        # Entry point với menu chọn Client/Server
├── UdpClient.cs      # Client - Gửi dữ liệu với retry
├── UdpServer.cs      # Server - Nhận dữ liệu và gửi ACK
├── MyApp.csproj      # Project configuration
└── README.md         # File này
```

---

## ⚙️ CẤU HÌNH

### UdpClient.cs:
```csharp
SERVER_IP = "127.0.0.1"    // Địa chỉ server
SERVER_PORT = 9000         // Cổng kết nối
PACKET_SIZE = 1400         // Kích thước mỗi gói
RETRY_MAX = 3              // Số lần retry tối đa
TIMEOUT_MS = 1000          // Timeout 1 giây
```

### UdpServer.cs:
```csharp
SERVER_IP = "127.0.0.1"    // Địa chỉ bind
SERVER_PORT = 9000         // Cổng lắng nghe
BUFFER_SIZE = 2048         // Buffer nhận
```

**Lưu ý:** Port mặc định là **9000** (có thể đổi trong cả 2 file)

---

## 🚀 CÁCH CHẠY

### Cách 1: Menu Interactive (Khuyên dùng)

**Terminal 1 - Server:**
```bash
dotnet run
```
→ Nhập `2` → Enter (chọn Server)

**Terminal 2 - Client:**
```bash
dotnet run
```
→ Nhập `1` → Enter (chọn Client)

### Cách 2: Chạy file exe trực tiếp

```bash
# Build trước
dotnet build

# Chạy
.\bin\Debug\net10.0\MyApp.exe
```

### Cách 3: Từ CMD

```cmd
cd C:\Users\Dell\MyApp
dotnet run
```

---

## 📊 PACKET STRUCTURE

```
┌─────────────────────────────────────────────┐
│           UDP PACKET FORMAT                 │
├─────────────┬───────────────────────────────┤
│  4 bytes    │  Sequence Number (int32)      │
├─────────────┴───────────────────────────────┤
│  N bytes    │  Payload Data (up to 1400B)   │
└─────────────────────────────────────────────┘

ACK Packet:
┌─────────────────────────────────────────────┐
│  4 bytes    │  ACK Number (int32)           │
└─────────────────────────────────────────────┘

FIN Packet (kết thúc):
┌─────────────────────────────────────────────┐
│  4 bytes    │  -1 (sequence = -1)           │
├─────────────┴───────────────────────────────┤
│  3 bytes    │  "END"                        │
└─────────────────────────────────────────────┘
```

---

## 🎯 WORKFLOW

### Client Side:
```
1. Chia dữ liệu thành các gói 1400 bytes
2. Với mỗi gói:
   - Tạo packet: [4 bytes seq] + [payload]
   - Gửi gói
   - Đợi ACK (timeout 1s)
   - Nếu timeout → Retry (tối đa 3 lần)
3. Gửi gói FIN (seq=-1) để kết thúc
4. Hiển thị thống kê
```

### Server Side:
```
1. Lắng nghe tại port 9000
2. Nhận gói: bytesReceived = ReceiveFrom(buffer)
3. Extract sequence number: seq = buffer[0..3]
4. Extract payload: payload = buffer[4..]
5. Lưu vào buffer: receivedPackets[seq] = payload
6. Gửi ACK: SendTo(ackBytes, clientEP)
7. Xử lý dữ liệu theo thứ tự:
   while receivedPackets.ContainsKey(expectedSeq):
       - Ghép vào dữ liệu hoàn chỉnh
       - expectedSeq++
8. Hiển thị thống kê
```

---

## 📈 OUTPUT MẪU

### Terminal 1 - Server:
```
=================================
   UDP CLIENT-SERVER DEMO
=================================

Chọn chế độ:
  [1] Client
  [2] Server

Nhập lựa chọn (1 hoặc 2): 2

=== UDP SERVER ===
Đang lắng nghe tại: 127.0.0.1:9000

[  0] Nhận 1404B ✓
[  1] Nhận 1404B ✓
[  2] Nhận 1404B ✓
[  3] Nhận 1404B ✓
...
[ 19] Nhận 1382B ✓
[ -1] Nhận    7B - Gói kết thúc

=== THỐNG KÊ ===
Tổng gói nhận: 20
Ngoài thứ tự: 0
Trùng lặp: 0
Còn trong buffer: 0
Tổng dữ liệu: 27978 bytes

Preview (100 ký tự đầu):
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA Lorem ipsum dolor sit amet BBBBBBBBBBBBBBBBBBB...

--- Nhấn Enter để thoát ---
```

### Terminal 2 - Client:
```
=================================
   UDP CLIENT-SERVER DEMO
=================================

Chọn chế độ:
  [1] Client
  [2] Server

Nhập lựa chọn (1 hoặc 2): 1

=== UDP CLIENT ===
Gửi đến: 127.0.0.1:9000

Tổng dữ liệu: 27978 bytes
Chia thành: 20 gói

[  0] Gửi 1404B ✓ OK
[  1] Gửi 1404B ✓ OK
[  2] Gửi 1404B ✓ OK
[  3] Gửi 1404B ✓ OK
...
[ 19] Gửi 1382B ✓ OK

=== THỐNG KÊ ===
Gói gửi thành công: 20
Số lần retry: 0
Tỷ lệ retry: 0.00%

--- Nhấn Enter để thoát ---
```

---

## 🔍 CHI TIẾT CODE

### Program.cs - Entry Point
```csharp
// Menu chọn Client hoặc Server
// Đơn giản, dễ sử dụng
// Không cần parameter phức tạp
```

### UdpClient.cs - Gửi dữ liệu
- Class: `UdpClientApp`
- Method chính: `SendData(string message)`
- Xử lý retry tự động
- Hiển thị progress với icons ✓ và ✗

### UdpServer.cs - Nhận dữ liệu
- Class: `UdpServerApp`
- Method chính: `Start()`
- Xử lý gói ngoài thứ tự
- Phát hiện gói trùng lặp
- Ghép dữ liệu theo thứ tự

---

## ⚡ TÙY CHỈNH

### Đổi Port:
Sửa trong **CẢ 2 file** `UdpClient.cs` và `UdpServer.cs`:
```csharp
private const int SERVER_PORT = 8080;  // Port mới
```

### Tăng Timeout:
Trong `UdpClient.cs`:
```csharp
private const int TIMEOUT_MS = 2000;  // 2 giây
```

### Thay đổi kích thước gói:
```csharp
private const int PACKET_SIZE = 512;  // Gói nhỏ hơn
```

### Tăng số lần retry:
```csharp
private const int RETRY_MAX = 5;  // Retry tối đa 5 lần
```

### Test với Remote Server:
Trong `UdpClient.cs`:
```csharp
private const string SERVER_IP = "192.168.1.100";  // IP máy server
```

---

## 🛠️ BUILD & DEBUG

### Build project:
```bash
dotnet build
```

### Clean và rebuild:
```bash
dotnet clean
dotnet build
```

### Chạy với configuration cụ thể:
```bash
dotnet run --configuration Release
```

### Kiểm tra process đang chạy:
```powershell
Get-Process MyApp
```

### Dừng tất cả process MyApp:
```powershell
Stop-Process -Name "MyApp" -Force
```

---

## ❓ TROUBLESHOOTING

### Lỗi: "Port already in use"
**Nguyên nhân:** Server đã chạy hoặc port bị chiếm

**Giải pháp:**
```bash
# Cách 1: Đổi port
private const int SERVER_PORT = 9001;

# Cách 2: Dừng process cũ
Stop-Process -Name "MyApp" -Force
```

### Lỗi: "The process cannot access the file because it is being used by another process"
**Nguyên nhân:** Process MyApp.exe đang chạy

**Giải pháp:**
```powershell
# Dừng process
Stop-Process -Name "MyApp" -Force

# Hoặc dừng theo PID
Stop-Process -Id <PID> -Force
```

### Lỗi: Client timeout liên tục
**Nguyên nhân:** Server chưa chạy hoặc firewall block

**Giải pháp:**
```bash
1. Chạy Server TRƯỚC, Client SAU
2. Tắt Firewall tạm thời
3. Tăng TIMEOUT_MS lên 2000
```

### Lỗi: Gói tin mất nhiều
**Nguyên nhân:** Mạng chậm, buffer overflow

**Giải pháp:**
```csharp
// Tăng delay giữa các gói
Thread.Sleep(100);  // Thay vì 50
```

### Output hiển thị ký tự lỗi (encoding)
**Nguyên nhân:** Console encoding

**Giải pháp:**
```bash
# Trong PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 📝 TESTING SCENARIOS

### Test 1: Kết nối bình thường
1. Chạy Server → Chọn `2`
2. Chạy Client → Chọn `1`
3. Kết quả: 20/20 gói thành công, 0% retry

### Test 2: Client chạy trước Server
1. Chạy Client → Chọn `1`
2. Kết quả: Timeout, Failed
3. Chạy Server → Chọn `2`
4. Chạy lại Client → OK

### Test 3: Đổi port
1. Đổi `SERVER_PORT = 8080` trong cả 2 file
2. Build lại: `dotnet build`
3. Chạy như bình thường

### Test 4: Network delay simulation
1. Tăng `Thread.Sleep(100)` trong Client
2. Quan sát thời gian gửi tăng

---

## 🎓 KIẾN THỨC MỞ RỘNG

### UDP vs TCP
| Đặc điểm | UDP | TCP |
|----------|-----|-----|
| Kết nối | Không kết nối | Có kết nối |
| Độ tin cậy | Không đảm bảo | Đảm bảo |
| Thứ tự gói | Không đảm bảo | Đảm bảo |
| Tốc độ | Nhanh | Chậm hơn |
| Overhead | Thấp | Cao |

### Tại sao dùng UDP?
- ✅ Tốc độ cao
- ✅ Phù hợp real-time (game, video streaming)
- ✅ Broadcast/Multicast
- ⚠️ Cần tự implement reliability

### Byte Order (Endianness)
```csharp
// Little Endian (Windows): 0x12345678 → 78 56 34 12
// Big Endian (Network): 0x12345678 → 12 34 56 78

// C# mặc định là Little Endian
// Không cần convert vì cả Client và Server đều C# trên Windows
```

---

## 📚 TÀI LIỆU THAM KHẢO

1. **UDP Protocol**: RFC 768
2. **C# Socket**: https://docs.microsoft.com/dotnet/api/system.net.sockets.socket
3. **BitConverter**: https://docs.microsoft.com/dotnet/api/system.bitconverter
4. **.NET Documentation**: https://docs.microsoft.com/dotnet/

---

## 🎯 KẾT LUẬN

**Đơn giản, dễ sử dụng, dễ mở rộng!**

```bash
# Chỉ cần 1 lệnh
dotnet run

# Chọn Server (2) hoặc Client (1)
# Xong!
```

### Ưu điểm:
- ✅ Code đơn giản, dễ đọc
- ✅ Menu interactive thân thiện
- ✅ Xử lý lỗi tốt
- ✅ Thống kê chi tiết
- ✅ Dễ debug và mở rộng

### Học được gì:
- 🎓 UDP Socket programming
- 🎓 Network packet structure
- 🎓 Retry mechanism
- 🎓 In-order delivery
- 🎓 C# networking fundamentals

---

**Made with ❤️ for learning UDP networking in C#** 🚀
