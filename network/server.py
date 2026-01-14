"""
GameServer - Xử lý logic server TCP
"""
import socket
import threading


class GameServer:
    def __init__(self, game_port=9999, on_data_received=None, on_client_connected=None):
        """
        Args:
            game_port: Port cho TCP server
            on_data_received: Callback khi nhận data từ client
            on_client_connected: Callback khi có client kết nối
        """
        self.game_port = game_port
        self.client_list = []
        self.client_roles = {}  # {conn: role}
        self.on_data_received = on_data_received
        self.on_client_connected = on_client_connected
        self.server_socket = None

    def start(self):
        """Khởi động server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", self.game_port))
        self.server_socket.listen(5)

        # Chạy vòng lặp accept
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        """Vòng lặp chấp nhận kết nối"""
        while True:
            try:
                conn, addr = self.server_socket.accept()
                self.client_list.append(conn)

                # Phân role cho client
                current_x_exists = any(r == "X" for r in self.client_roles.values())
                if not current_x_exists:
                    role = "X"
                    self.client_roles[conn] = "X"
                else:
                    role = "WATCH"
                    self.client_roles[conn] = "WATCH"

                # Gửi role cho client
                conn.sendall(f"ROLE|{role}".encode())

                # Callback
                if self.on_client_connected:
                    self.on_client_connected(conn, addr, role)

                # Xử lý client trong thread riêng
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()

            except Exception as e:
                print(f"Accept error: {e}")
                break

    def _handle_client(self, conn):
        """Xử lý data từ một client"""
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break

                # Xử lý REMATCH
                if "REMATCH|YES" in data:
                    pass  # Logic rematch sẽ xử lý ở tầng cao hơn
                elif "REMATCH|NO" in data:
                    self.client_roles[conn] = "WATCH"
                    conn.sendall("ROLE|WATCH".encode())

                # Callback xử lý data
                if self.on_data_received:
                    self.on_data_received(data, conn)

                # Broadcast cho các client khác
                self.broadcast(data, sender_conn=conn)

        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            self._remove_client(conn)

    def _remove_client(self, conn):
        """Xóa client khi disconnect"""
        if conn in self.client_list:
            self.client_list.remove(conn)
        if conn in self.client_roles:
            del self.client_roles[conn]
        try:
            conn.close()
        except:
            pass

    def broadcast(self, data, sender_conn=None):
        """
        Gửi data đến tất cả client (trừ sender)

        Args:
            data: Dữ liệu cần gửi
            sender_conn: Connection của người gửi (sẽ không nhận lại data)
        """
        for conn in self.client_list[:]:  # Copy list để tránh modify during iteration
            if conn != sender_conn:
                try:
                    conn.sendall(data.encode() if isinstance(data, str) else data)
                except:
                    self._remove_client(conn)

    def send_to_all(self, data):
        """Gửi data đến TẤT CẢ client"""
        self.broadcast(data, sender_conn=None)

    def find_new_player(self):
        """Tìm người chơi mới từ danh sách khán giả"""
        has_x = any(r == "X" for r in self.client_roles.values())
        if not has_x:
            for conn, role in self.client_roles.items():
                if role == "WATCH":
                    self.client_roles[conn] = "X"
                    try:
                        conn.sendall("ROLE|X".encode())
                    except:
                        pass
                    return conn
        return None

    def get_client_count(self):
        """Lấy số lượng client đang kết nối"""
        return len(self.client_list)

    def stop(self):
        """Dừng server"""
        for conn in self.client_list[:]:
            try:
                conn.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

