import tkinter as tk
from functools import partial
import threading
import socket
from tkinter import messagebox
import random
import time

# --- CẤU HÌNH GIAO DIỆN & GAME ---
OX_ROWS = 15  # Số dòng
OX_COLS = 20  # Số cột
GAME_PORT = 9999
DISCOVERY_PORT = 9998

# Bảng màu (Theme hiện đại)
COLOR_BG_MAIN = "#2C3E50"  # Màu nền chính (Xám đậm)
COLOR_SIDEBAR = "#34495E"  # Màu thanh bên
COLOR_BOARD = "#ECF0F1"  # Màu nền bàn cờ
COLOR_BTN_DEFAULT = "#BDC3C7"  # Màu nút chưa đánh
COLOR_X = "#E74C3C"  # Màu đỏ cho X
COLOR_O = "#3498DB"  # Màu xanh cho O
COLOR_TEXT_LIGHT = "#ECF0F1"  # Màu chữ sáng
COLOR_ACCENT = "#F1C40F"  # Màu nhấn (Vàng)


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Caro LAN Ultimate - Giao Diện Mới")
        self.geometry("1100x700")
        self.configure(bg=COLOR_BG_MAIN)

        # Biến Game
        self.Buts = {}
        self.memory = []
        self.Threading_socket = Threading_socket(self)
        self.my_role = None  # "O", "X", "WATCH"
        self.timer = 30
        self.timer_running = False
        self.room_code = ""

        # Khởi tạo giao diện
        self.setup_ui()

    def setup_ui(self):
        # --- 1. SIDEBAR (Bên trái) ---
        sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=250, padx=10, pady=10)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)  # Giữ kích thước cố định

        # Tiêu đề
        lbl_title = tk.Label(sidebar, text="CARO LAN", font=("Helvetica", 20, "bold"),
                             bg=COLOR_SIDEBAR, fg=COLOR_ACCENT)
        lbl_title.pack(pady=(10, 20))

        # Khu vực kết nối
        lbl_room = tk.Label(sidebar, text="MÃ PHÒNG:", font=("Arial", 10, "bold"),
                            bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT)
        lbl_room.pack(anchor="w")

        self.entry_code = tk.Entry(sidebar, font=("Arial", 14), justify='center', bg="#FFF")
        self.entry_code.pack(fill=tk.X, pady=5)

        btn_join = tk.Button(sidebar, text="VÀO PHÒNG", bg="#2ECC71", fg="white", font=("Arial", 10, "bold"),
                             command=lambda: self.Threading_socket.find_room_by_code(self.entry_code.get()))
        btn_join.pack(fill=tk.X, pady=5)

        btn_create = tk.Button(sidebar, text="TẠO PHÒNG", bg="#E67E22", fg="white", font=("Arial", 10, "bold"),
                               command=self.createRoom)
        btn_create.pack(fill=tk.X, pady=5)

        tk.Frame(sidebar, height=2, bg=COLOR_TEXT_LIGHT).pack(fill=tk.X, pady=20)  # Đường kẻ ngang

        # Thông tin người chơi
        self.lbl_role = tk.Label(sidebar, text="Vai trò: Chưa có", font=("Arial", 12),
                                 bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT)
        self.lbl_role.pack(pady=10)

        # Đồng hồ đếm ngược
        self.lbl_timer = tk.Label(sidebar, text="30s", font=("Helvetica", 40, "bold"),
                                  bg=COLOR_SIDEBAR, fg=COLOR_ACCENT)
        self.lbl_timer.pack(pady=10)

        # Trạng thái game
        self.lbl_status = tk.Label(sidebar, text="Hãy tạo hoặc vào phòng...", font=("Arial", 11, "italic"),
                                   bg=COLOR_SIDEBAR, fg="#BDC3C7", wraplength=230)
        self.lbl_status.pack(pady=10)

        # Nút chức năng ingame
        btn_undo = tk.Button(sidebar, text="Đi lại (Undo)", bg="#95A5A6", fg="white",
                             command=partial(self.Undo, synchronized=True))
        btn_undo.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # --- 2. MAIN BOARD (Bên phải) ---
        board_frame = tk.Frame(self, bg=COLOR_BOARD, padx=10, pady=10)
        board_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Center the grid inside the board frame
        grid_container = tk.Frame(board_frame, bg=COLOR_BOARD)
        grid_container.place(relx=0.5, rely=0.5, anchor="center")

        for x in range(OX_ROWS):
            for y in range(OX_COLS):
                # Tạo nút phẳng, đẹp hơn
                self.Buts[x, y] = tk.Button(grid_container, font=('Arial', 10, 'bold'),
                                            width=4, height=2,
                                            bg="white", relief="groove", borderwidth=1,
                                            command=partial(self.handleButton, x=x, y=y, sending=True))
                self.Buts[x, y].grid(row=x, column=y, padx=0, pady=0)

    # --- LOGIC CŨ (Đã kết nối với UI mới) ---
    def createRoom(self):
        self.my_role = "O"
        self.room_code = str(random.randint(100000, 999999))
        self.entry_code.delete(0, tk.END)
        self.entry_code.insert(0, self.room_code)

        self.lbl_status.config(text=f"Đang chờ người chơi...", fg=COLOR_ACCENT)
        self.lbl_role.config(text="Vai trò: Server (O)")

        threading.Thread(target=self.Threading_socket.serverAction, daemon=True).start()
        threading.Thread(target=self.Threading_socket.udp_discovery_server, args=(self.room_code,), daemon=True).start()

    def handleButton(self, x, y, sending=True):
        current_turn_char = "X" if len(self.memory) % 2 == 0 else "O"

        if self.Buts[x, y]['text'] == "":
            if sending:
                if self.my_role is None or self.my_role == "WATCH" or self.my_role != current_turn_char:
                    return

            if self.memory.count([x, y]) == 0:
                self.memory.append([x, y])

            # Cập nhật giao diện nút
            self.Buts[x, y]['text'] = current_turn_char
            self.Buts[x, y]['fg'] = COLOR_X if current_turn_char == "X" else COLOR_O
            # Highlight nước vừa đánh (tùy chọn)
            self.Buts[x, y]['bg'] = "#FDF2E9"

            if sending:
                self.Threading_socket.sendData("{}|{}|{}|".format("hit", x, y))

            if self.checkWin(x, y, current_turn_char):
                self.timer_running = False
                winner_msg = f"Người chơi {current_turn_char} thắng!"
                self.lbl_status.config(text=winner_msg, fg="purple")
                self.notification("Kết thúc", winner_msg)

                if self.my_role in ["X", "O"]:
                    self.ask_rematch()
                else:
                    self.lbl_status.config(text="Đang chờ chủ phòng...", fg="orange")
                return

            self.resetTimer()

    def ask_rematch(self):
        ans = messagebox.askyesno("Ván mới?", "Bạn có muốn tiếp tục chơi không?\n(No = Làm khán giả)")
        if ans:
            self.lbl_status.config(text="Đã chọn Tiếp tục. Đang chờ...", fg="blue")
            self.Threading_socket.sendData("REMATCH|YES|")
        else:
            self.my_role = "WATCH"
            self.lbl_status.config(text="Chế độ Khán Giả.", fg="gray")
            self.lbl_role.config(text="Vai trò: Khán Giả")
            self.Threading_socket.sendData("REMATCH|NO|")

    def reset_board_ui(self):
        for x in range(OX_ROWS):
            for y in range(OX_COLS):
                self.Buts[x, y]["text"] = ""
                self.Buts[x, y]["bg"] = "white"  # Reset màu nền
        self.memory = []
        self.timer_running = False
        self.lbl_status.config(text="Ván mới bắt đầu!", fg="#2ECC71")
        self.resetTimer()

    def handleSkipTurn(self):
        current_turn_char = "X" if len(self.memory) % 2 == 0 else "O"
        if current_turn_char == self.my_role:
            self.Threading_socket.sendData("{}|".format("SKIP"))
            self.notification("Hết giờ", "Bạn đã mất lượt!")
            self.forceSkipLogic()

    def forceSkipLogic(self):
        self.memory.append([-1, -1])
        self.resetTimer()

    def resetTimer(self):
        self.timer = 30
        self.timer_running = True
        next_turn = "X" if len(self.memory) % 2 == 0 else "O"

        # Logic hiển thị trạng thái
        if self.my_role == "WATCH":
            status_text = f"Đang chờ: {next_turn}"
            self.lbl_status.config(fg="gray")
        elif next_turn == self.my_role:
            status_text = "LƯỢT CỦA BẠN!"
            self.lbl_status.config(fg="#2ECC71")  # Màu xanh lá
        else:
            status_text = "Lượt đối thủ..."
            self.lbl_status.config(fg="#E74C3C")  # Màu đỏ

        self.lbl_status.config(text=status_text)
        self.lbl_timer.config(text=str(self.timer))

        if not hasattr(self, 'timer_thread_obj') or not self.timer_thread_obj.is_alive():
            self.timer_thread_obj = threading.Thread(target=self.countdown_worker, daemon=True)
            self.timer_thread_obj.start()

    def countdown_worker(self):
        while self.timer_running:
            time.sleep(1)
            if not self.timer_running: break
            self.timer -= 1

            # Cập nhật UI an toàn từ luồng khác
            self.after(0, lambda: self.lbl_timer.config(text=str(self.timer)))

            if self.timer <= 0:
                next_turn = "X" if len(self.memory) % 2 == 0 else "O"
                if next_turn == self.my_role:
                    self.after(0, self.handleSkipTurn)
                self.timer = 30

    def notification(self, title, msg):
        messagebox.showinfo(str(title), str(msg))

    def checkWin(self, x, y, XO):
        count = 0;
        i, j = x, y
        while (j < OX_ROWS and self.Buts[i, j]["text"] == XO): count += 1; j += 1
        j = y
        while (j >= 0 and self.Buts[i, j]["text"] == XO): count += 1; j -= 1
        if count >= 6: return True  # Sửa lại điều kiện thắng (thường là 5, code cũ để 6)

        count = 0;
        i, j = x, y
        while (i < OX_COLS and self.Buts[i, j]["text"] == XO): count += 1; i += 1
        i = x
        while (i >= 0 and self.Buts[i, j]["text"] == XO): count += 1; i -= 1
        if count >= 6: return True

        count = 0;
        i, j = x, y
        while (i >= 0 and j < OX_ROWS and self.Buts[i, j]["text"] == XO): count += 1; i -= 1; j += 1
        i, j = x, y
        while (i <= OX_COLS and j >= 0 and self.Buts[i, j]["text"] == XO): count += 1; i += 1; j -= 1
        if count >= 6: return True

        count = 0;
        i, j = x, y
        while (i < OX_ROWS and j < OX_COLS and self.Buts[i, j]["text"] == XO): count += 1; i += 1; j += 1
        i, j = x, y
        while (i >= 0 and j >= 0 and self.Buts[i, j]["text"] == XO): count += 1; i -= 1; j -= 1
        if count >= 6: return True
        return False

    def Undo(self, synchronized):
        if self.my_role == "WATCH" and synchronized: return
        if len(self.memory) > 0:
            last = self.memory[-1]
            if last != [-1, -1]:
                self.Buts[last[0], last[1]]['text'] = ""
                self.Buts[last[0], last[1]]['bg'] = "white"
            self.memory.pop()
            if synchronized: self.Threading_socket.sendData("{}|".format("Undo"))
            self.resetTimer()


class Threading_socket():
    def __init__(self, gui):
        self.conn = None
        self.client_list = []
        self.client_roles = {}
        self.gui = gui
        self.name = ""
        self.rematch_count = 0

    # --- DISCOVERY & CONNECTION (Giữ nguyên logic) ---
    def find_room_by_code(self, room_code):
        if len(room_code) == 0:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mã phòng!")
            return
        self.gui.lbl_status.config(text=f"Đang tìm phòng {room_code}...", fg="orange")
        threading.Thread(target=self.perform_discovery, args=(room_code,), daemon=True).start()

    def perform_discovery(self, room_code):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.settimeout(3)
        try:
            message = f"FIND|{room_code}"
            udp_sock.sendto(message.encode(), ('<broadcast>', DISCOVERY_PORT))
            data, addr = udp_sock.recvfrom(1024)
            response = data.decode()
            if response.startswith("FOUND|"):
                server_ip = response.split("|")[1]
                self.gui.lbl_status.config(text=f"Tìm thấy! Kết nối {server_ip}", fg="#2ECC71")
                self.clientAction(server_ip)
            else:
                self.gui.notification("Lỗi", "Phản hồi lạ!")
        except socket.timeout:
            self.gui.notification("Thất bại", "Không tìm thấy phòng!")
            self.gui.lbl_status.config(text="Không tìm thấy phòng.", fg="red")
        except Exception as e:
            print(e)
            self.gui.notification("Lỗi", "Lỗi mạng LAN")
        finally:
            udp_sock.close()

    def udp_discovery_server(self, my_room_code):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('0.0.0.0', DISCOVERY_PORT))
        while True:
            try:
                data, addr = udp_sock.recvfrom(1024)
                msg = data.decode()
                if msg.startswith("FIND|") and msg.split("|")[1] == my_room_code:
                    my_ip = self.get_local_ip()
                    udp_sock.sendto(f"FOUND|{my_ip}".encode(), addr)
            except:
                pass

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def clientAction(self, inputIP):
        self.name = "client"
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((inputIP, GAME_PORT))
            threading.Thread(target=self.client_listener, daemon=True).start()
        except:
            self.gui.notification("Lỗi", "Không kết nối được TCP!")

    def client_listener(self):
        while True:
            try:
                data = self.conn.recv(1024).decode()
                if not data: break
                if data.startswith("ROLE|"):
                    role = data.split("|")[1]
                    self.gui.my_role = role
                    self.gui.lbl_role.config(text=f"Vai trò: {role}")
                    self.gui.resetTimer()
                elif data == "RESET_GAME|":
                    self.gui.reset_board_ui()
                else:
                    self.process_data(data)
            except:
                break

    def serverAction(self):
        self.name = "server"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", GAME_PORT))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            self.client_list.append(conn)
            current_x_exists = any(r == "X" for r in self.client_roles.values())
            if not current_x_exists:
                role = "X"
                self.client_roles[conn] = "X"
                self.gui.resetTimer()
            else:
                role = "WATCH"
                self.client_roles[conn] = "WATCH"
            conn.sendall(f"ROLE|{role}".encode())
            threading.Thread(target=self.server_handler, args=(conn,), daemon=True).start()

    def server_handler(self, conn):
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data: break
                if "REMATCH|YES" in data:
                    self.rematch_count += 1
                elif "REMATCH|NO" in data:
                    self.client_roles[conn] = "WATCH"
                    conn.sendall("ROLE|WATCH".encode())
                    self.find_new_player()
                self.process_data(data)
                self.broadcast(data, sender_conn=conn)
        except:
            pass
        finally:
            if conn in self.client_list: self.client_list.remove(conn)
            if conn in self.client_roles: del self.client_roles[conn]
            conn.close()

    def find_new_player(self):
        has_X = any(r == "X" for r in self.client_roles.values())
        if not has_X:
            for c, r in self.client_roles.items():
                if r == "WATCH":
                    self.client_roles[c] = "X"
                    c.sendall("ROLE|X".encode())
                    self.server_reset_game()
                    break

    def server_reset_game(self):
        self.broadcast("RESET_GAME|")
        self.gui.reset_board_ui()
        self.rematch_count = 0

    def broadcast(self, data, sender_conn=None):
        for c in self.client_list:
            if c != sender_conn:
                try:
                    c.sendall(data.encode())
                except:
                    pass

    def process_data(self, data):
        if not data: return
        parts = data.split("|")
        if len(parts) > 2:
            if parts[1] == "hit": self.gui.handleButton(int(parts[2]), int(parts[3]), sending=False)
            if parts[1] == "Undo": self.gui.Undo(False)
            if parts[1] == "SKIP": self.gui.forceSkipLogic()

    def sendData(self, data):
        msg = "{}|".format(self.name) + data if "REMATCH" not in data else data
        if self.name == "server":
            if "REMATCH|YES" in data:
                self.server_reset_game()
                return
            if "REMATCH|NO" in data:
                self.gui.my_role = "WATCH"
                return
            self.broadcast(msg)
        else:
            if self.conn:
                try:
                    self.conn.sendall(msg.encode())
                except:
                    pass

if __name__ == "__main__":
    window = Window()
    window.mainloop()