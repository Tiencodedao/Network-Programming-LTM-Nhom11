"""
GameClient - Xử lý logic client TCP
"""
import socket
import threading


class GameClient:
    def __init__(self, on_data_received=None, on_connected=None, on_disconnected=None):
        """
        Args:
            on_data_received: Callback khi nhận data từ server
            on_connected: Callback khi kết nối thành công
            on_disconnected: Callback khi mất kết nối
        """
        self.conn = None
        self.on_data_received = on_data_received
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.is_connected = False

    def connect(self, server_ip, game_port=9999):
        """
        Kết nối đến server

        Args:
            server_ip: IP của server
            game_port: Port của server

        Returns:
            True nếu kết nối thành công, False nếu thất bại
        """
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((server_ip, game_port))
            self.is_connected = True

            # Callback
            if self.on_connected:
                self.on_connected()

            # Bắt đầu lắng nghe data từ server
            threading.Thread(target=self._listen_loop, daemon=True).start()

            return True

        except Exception as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            return False

    def _listen_loop(self):
        """Vòng lặp lắng nghe data từ server"""
        try:
            while self.is_connected:
                data = self.conn.recv(1024).decode()
                if not data:
                    break

                # Callback xử lý data
                if self.on_data_received:
                    self.on_data_received(data)

        except Exception as e:
            print(f"Listen error: {e}")
        finally:
            self._handle_disconnect()

    def _handle_disconnect(self):
        """Xử lý khi mất kết nối"""
        self.is_connected = False
        if self.on_disconnected:
            self.on_disconnected()

    def send(self, data):
        """
        Gửi data đến server

        Args:
            data: Dữ liệu cần gửi (string)

        Returns:
            True nếu gửi thành công, False nếu thất bại
        """
        if not self.is_connected or not self.conn:
            return False

        try:
            self.conn.sendall(data.encode() if isinstance(data, str) else data)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            self._handle_disconnect()
            return False

    def disconnect(self):
        """Ngắt kết nối"""
        self.is_connected = False
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None

