"""
CaroWindow - Cửa sổ chính của game
"""
import tkinter as tk
from tkinter import messagebox
import threading
import random
import time

from models.game_state import GameState
from models.player import Player
from network.discovery import DiscoveryService
from network.server import GameServer
from network.client import GameClient
from ui.board import BoardWidget
from ui.sidebar import SidebarWidget


# Màu sắc
COLOR_BG_MAIN = "#2C3E50"
COLOR_X = "#E74C3C"
COLOR_O = "#3498DB"

GAME_PORT = 9999
DISCOVERY_PORT = 9998
OX_ROWS = 15
OX_COLS = 20


class CaroWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Caro LAN Ultimate - Modular Structure")
        self.geometry("1100x700")
        self.configure(bg=COLOR_BG_MAIN)

        # Models
        self.game_state = GameState(rows=OX_ROWS, cols=OX_COLS, win_condition=5)
        self.player = Player()

        # Network
        self.discovery_service = DiscoveryService(DISCOVERY_PORT)
        self.game_server = None
        self.game_client = None

        # Timer
        self.timer_running = False
        self.timer_thread_obj = None
        self.room_code = ""

        # UI Components
        self.sidebar = None
        self.board = None
        self._setup_ui()

    def _setup_ui(self):
        """Khởi tạo giao diện"""
        # Sidebar (bên trái)
        self.sidebar = SidebarWidget(
            self,
            on_join_room=self.handle_join_room,
            on_create_room=self.handle_create_room,
            on_undo=self.handle_undo,
            on_chat_send=self.handle_chat_send
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Board (bên phải)
        self.board = BoardWidget(
            self,
            rows=OX_ROWS,
            cols=OX_COLS,
            on_button_click=self.handle_button_click
        )
        self.board.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # ========== NETWORK HANDLERS ==========
    def handle_create_room(self):
        """Xử lý tạo phòng"""
        self.player.set_role("O")
        self.room_code = str(random.randint(100000, 999999))
        self.sidebar.set_room_code(self.room_code)
        self.sidebar.set_status(f"Đang chờ người chơi...", "#F1C40F")
        self.sidebar.set_role("Server (O)")

        # Khởi động server
        self.game_server = GameServer(
            game_port=GAME_PORT,
            on_data_received=self.on_server_data_received,
            on_client_connected=self.on_client_connected
        )
        self.game_server.start()

        # Khởi động discovery server
        threading.Thread(
            target=self.discovery_service.start_discovery_server,
            args=(self.room_code,),
            daemon=True
        ).start()

    def handle_join_room(self, room_code):
        """Xử lý vào phòng"""
        if not room_code:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mã phòng!")
            return

        self.sidebar.set_status(f"Đang tìm phòng {room_code}...", "orange")

        # Tìm phòng trong thread riêng
        def search_thread():
            server_ip = self.discovery_service.find_room(room_code)
            if server_ip:
                self.after(0, lambda: self.connect_to_server(server_ip))
            else:
                self.after(0, lambda: messagebox.showerror("Thất bại", "Không tìm thấy phòng!"))
                self.after(0, lambda: self.sidebar.set_status("Không tìm thấy phòng.", "red"))

        threading.Thread(target=search_thread, daemon=True).start()

    def connect_to_server(self, server_ip):
        """Kết nối đến server"""
        self.sidebar.set_status(f"Đang kết nối {server_ip}...", "#2ECC71")

        self.game_client = GameClient(
            on_data_received=self.on_client_data_received,
            on_connected=self.on_connected_to_server,
            on_disconnected=self.on_disconnected_from_server
        )

        if self.game_client.connect(server_ip, GAME_PORT):
            self.sidebar.set_status("Đã kết nối!", "#2ECC71")
        else:
            messagebox.showerror("Lỗi", "Không kết nối được!")
            self.sidebar.set_status("Kết nối thất bại.", "red")

    def on_client_connected(self, conn, addr, role):
        """Callback khi có client kết nối (server)"""
        print(f"Client {addr} connected with role {role}")
        if role == "X":
            self.after(0, lambda: self.reset_timer())

    def on_connected_to_server(self):
        """Callback khi kết nối thành công (client)"""
        print("Connected to server")

    def on_disconnected_from_server(self):
        """Callback khi mất kết nối (client)"""
        self.after(0, lambda: messagebox.showwarning("Mất kết nối", "Đã mất kết nối với server!"))

    def on_server_data_received(self, data, sender_conn):
        """Callback khi server nhận data từ client"""
        self.after(0, lambda: self.process_received_data(data))

    def on_client_data_received(self, data):
        """Callback khi client nhận data từ server"""
        if data.startswith("ROLE|"):
            role = data.split("|")[1]
            self.player.set_role(role)
            self.after(0, lambda: self.sidebar.set_role(role))
            if role in ["O", "X"]:
                self.after(0, lambda: self.reset_timer())
        elif data == "RESET_GAME|":
            self.after(0, lambda: self.reset_board_ui())
        else:
            self.after(0, lambda: self.process_received_data(data))

    def process_received_data(self, data):
        """Xử lý data nhận được"""
        parts = data.split("|")
        if len(parts) < 2:
            return

        action = parts[1]

        if action == "hit" and len(parts) >= 4:
            x, y = int(parts[2]), int(parts[3])
            self.handle_button_click(x, y, sending=False)
        elif action == "Undo":
            self.handle_undo(synchronized=False)
        elif action == "SKIP":
            self.force_skip_logic()
        elif action == "CHAT" and len(parts) >= 4:
            sender = parts[2]
            message = parts[3]
            self.after(0, lambda: self.sidebar.add_chat_message(sender, message))

    # ========== GAME LOGIC ==========
    def handle_button_click(self, x, y, sending=True):
        """Xử lý khi click vào ô"""
        current_turn = self.game_state.get_current_turn()

        # Kiểm tra quyền đánh
        if self.board.get_cell_text(x, y) != "":
            return

        if sending:
            if not self.player.can_move(current_turn):
                return

        # Thêm nước đi
        if not self.game_state.add_move(x, y):
            return

        # Cập nhật board model
        self.game_state.update_board(x, y, current_turn)

        # Cập nhật UI
        color = COLOR_X if current_turn == "X" else COLOR_O
        self.board.set_cell(x, y, current_turn, color)

        # Gửi qua mạng
        if sending:
            self.send_data(f"hit|{x}|{y}")

        # Kiểm tra thắng
        if self.game_state.check_win(x, y, current_turn):
            self.timer_running = False
            winner_msg = f"Người chơi {current_turn} thắng!"
            self.sidebar.set_status(winner_msg, "purple")
            messagebox.showinfo("Kết thúc", winner_msg)

            if self.player.is_player():
                self.ask_rematch()
            return

        # Reset timer
        self.reset_timer()

    def handle_undo(self, synchronized=True):
        """Xử lý đi lại"""
        if self.player.is_watcher() and synchronized:
            return

        last_move = self.game_state.undo_last_move()
        if last_move:
            x, y = last_move
            if x != -1 and y != -1:
                self.board.clear_cell(x, y)
                self.game_state.clear_cell(x, y)

            if synchronized:
                self.send_data("Undo")

            self.reset_timer()

    def ask_rematch(self):
        """Hỏi chơi tiếp"""
        ans = messagebox.askyesno("Ván mới?", "Bạn có muốn tiếp tục chơi không?\n(No = Làm khán giả)")
        if ans:
            self.sidebar.set_status("Đã chọn Tiếp tục. Đang chờ...", "blue")
            self.send_data("REMATCH|YES")
            if self.game_server:
                self.reset_board_ui()
        else:
            self.player.set_role("WATCH")
            self.sidebar.set_status("Chế độ Khán Giả.", "gray")
            self.sidebar.set_role("Khán Giả")
            self.send_data("REMATCH|NO")

    def reset_board_ui(self):
        """Reset giao diện bàn cờ"""
        self.board.reset()
        self.game_state.reset()
        self.timer_running = False
        self.sidebar.set_status("Ván mới bắt đầu!", "#2ECC71")
        self.reset_timer()

    def force_skip_logic(self):
        """Bỏ lượt"""
        self.game_state.add_move(-1, -1)
        self.reset_timer()

    # ========== TIMER ==========
    def reset_timer(self):
        """Reset đồng hồ đếm ngược"""
        self.player.reset_timer(30)
        self.timer_running = True
        next_turn = self.game_state.get_current_turn()

        # Cập nhật status
        if self.player.is_watcher():
            self.sidebar.set_status(f"Đang chờ: {next_turn}", "gray")
        elif next_turn == self.player.role:
            self.sidebar.set_status("LƯỢT CỦA BẠN!", "#2ECC71")
        else:
            self.sidebar.set_status("Lượt đối thủ...", "#E74C3C")

        self.sidebar.set_timer(self.player.timer)

        if not self.timer_thread_obj or not self.timer_thread_obj.is_alive():
            self.timer_thread_obj = threading.Thread(target=self.countdown_worker, daemon=True)
            self.timer_thread_obj.start()

    def countdown_worker(self):
        """Worker thread cho countdown"""
        while self.timer_running:
            time.sleep(1)
            if not self.timer_running:
                break

            self.player.timer -= 1
            self.after(0, lambda: self.sidebar.set_timer(self.player.timer))

            if self.player.timer <= 0:
                next_turn = self.game_state.get_current_turn()
                if next_turn == self.player.role:
                    self.after(0, self.handle_skip_turn)
                self.player.timer = 30

    def handle_skip_turn(self):
        """Xử lý hết giờ"""
        current_turn = self.game_state.get_current_turn()
        if current_turn == self.player.role:
            self.send_data("SKIP")
            messagebox.showinfo("Hết giờ", "Bạn đã mất lượt!")
            self.force_skip_logic()

    # ========== CHAT HANDLERS ==========
    def handle_chat_send(self, text):
        """Xử lý gửi tin nhắn chat"""
        if not text.strip():
            return

        # Xác định tên người gửi
        sender_name = "Bạn"
        if self.game_server:
            sender_name = "Host"
        elif self.game_client:
            sender_name = "Guest"

        # Gửi qua mạng
        self.send_data(f"CHAT|{sender_name}|{text}")

    # ========== NETWORK SEND ==========
    def send_data(self, action):
        """Gửi data qua mạng"""
        if self.game_server:
            # Server mode
            if "REMATCH" in action:
                if "YES" in action:
                    self.reset_board_ui()
                elif "NO" in action:
                    self.player.set_role("WATCH")
                return
            self.game_server.broadcast(f"server|{action}|", sender_conn=None)
        elif self.game_client:
            # Client mode
            msg = f"client|{action}|" if "REMATCH" not in action else action
            self.game_client.send(msg)

