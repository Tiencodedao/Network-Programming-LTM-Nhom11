import asyncio
import socket
from datetime import datetime

# --- CẤU HÌNH SERVER ---
HOST = '127.0.0.1'
PORT = 9999  # Cổng hoạt động
BUFFER_SIZE = 65536  # Kích thước bộ đệm 64KB (Tối ưu hóa)


async def handle_client(reader, writer):
    """
    Hàm xử lý kết nối bất đồng bộ (Non-blocking)
    """
    addr = writer.get_extra_info('peername')
    print(f"[{datetime.now()}] ⚡ Kết nối mới từ: {addr}")

    # --- PHẦN TỐI ƯU HÓA TCP (QUAN TRỌNG) ---
    sock = writer.get_extra_info('socket')
    if sock:
        # 1. Tối ưu kích thước bộ đệm (Window Size) để truyền tải nhanh hơn
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)

        # 2. Tắt thuật toán Nagle (TCP_NODELAY) để giảm độ trễ cho gói tin nhỏ
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        print(f"   -> Đã cấu hình tối ưu TCP (Buffer: {BUFFER_SIZE}, NoDelay: True)")

    try:
        while True:
            # Đọc dữ liệu (await giúp không chặn các kết nối khác)
            data = await reader.read(1024)
            if not data:
                break

            message = data.decode('utf-8')
            print(f"    Nhận: {message}")

            # Gửi phản hồi
            response = f"Server Python (Async) đã nhận: {message}"
            writer.write(response.encode('utf-8'))
            await writer.drain()

    except ConnectionResetError:
        print(f"⚠️  Client {addr} ngắt kết nối đột ngột.")
    finally:
        print(f" Đóng kết nối: {addr}")
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"==================================================")
    print(f" PYTHON TCP SERVER ĐANG CHẠY TẠI {addrs}")
    print(f" Chế độ: Asyncio (Bất đồng bộ) + TCP Optimized")
    print(f"==================================================")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        # Chạy trên Windows cần Policy này để tránh lỗi EventLoop
        import sys

        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server đã dừng.")