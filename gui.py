import tkinter as tk
from functools import partial
import threading
import socket
from tkinter import messagebox
import random
import time

# --- CẤU HÌNH GIAO DIỆN & GAME ---
OX_ROWS = 15
OX_COLS = 20
GAME_PORT = 9999
DISCOVERY_PORT = 9998

# Bảng màu....
COLOR_BG_MAIN = "#2C3E50"
COLOR_SIDEBAR = "#34495E"
COLOR_BOARD = "#ECF0F1"
COLOR_X = "#E74C3C"
COLOR_O = "#3498DB"
COLOR_TEXT_LIGHT = "#ECF0F1"
COLOR_ACCENT = "#F1C40F"
COLOR_SUCCESS = "#2ECC71"
COLOR_WARNING = "#E67E22"


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Caro LAN - Auto Reconnect Fix")
        self.geometry("1100x700")
        self.configure(bg=COLOR_BG_MAIN)

        # Biến Game
        self.Buts = {}
        self.memory = []
        self.Threading_socket = Threading_socket(self)
        self.my_role = None
        self.timer = 30
        self.timer_running = False
        self.timer_thread_obj = None
        self.room_code = ""

        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        # --- SIDEBAR ---
        sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=250, padx=10, pady=10)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CARO LAN", font=("Helvetica", 20, "bold"),
                 bg=COLOR_SIDEBAR, fg=COLOR_ACCENT).pack(pady=(10, 20))

        tk.Label(sidebar, text="MÃ PHÒNG:", font=("Arial", 10, "bold"),
                 bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT).pack(anchor="w")

        self.entry_code = tk.Entry(sidebar, font=("Arial", 14), justify='center', bg="#FFF")
        self.entry_code.pack(fill=tk.X, pady=5)

        tk.Button(sidebar, text="VÀO PHÒNG", bg=COLOR_SUCCESS, fg="white", font=("Arial", 10, "bold"),
                  command=lambda: self.Threading_socket.find_room_by_code(self.entry_code.get())).pack(fill=tk.X,
                                                                                                       pady=5)

        tk.Button(sidebar, text="TẠO PHÒNG", bg=COLOR_WARNING, fg="white", font=("Arial", 10, "bold"),
                  command=self.createRoom).pack(fill=tk.X, pady=5)

        tk.Frame(sidebar, height=2, bg=COLOR_TEXT_LIGHT).pack(fill=tk.X, pady=20)

        self.lbl_role = tk.Label(sidebar, text="Vai trò: Chưa có", font=("Arial", 12),
                                 bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT)
        self.lbl_role.pack(pady=10)

        self.lbl_timer = tk.Label(sidebar, text="30s", font=("Helvetica", 40, "bold"),
                                  bg=COLOR_SIDEBAR, fg=COLOR_ACCENT)
        self.lbl_timer.pack(pady=10)

        self.lbl_status = tk.Label(sidebar, text="Hãy tạo hoặc vào phòng...", font=("Arial", 11, "italic"),
                                   bg=COLOR_SIDEBAR, fg="#BDC3C7", wraplength=230)
        self.lbl_status.pack(pady=10)

        tk.Button(sidebar, text="Đi lại (Undo)", bg="#95A5A6", fg="white",
                  command=partial(self.Undo, synchronized=True)).pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # --- BÀN CỜ ---
        board_frame = tk.Frame(self, bg=COLOR_BOARD, padx=10, pady=10)
        board_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        grid_container = tk.Frame(board_frame, bg=COLOR_BOARD)
        grid_container.place(relx=0.5, rely=0.5, anchor="center")

        for x in range(OX_ROWS):
            for y in range(OX_COLS):
                self.Buts[x, y] = tk.Button(grid_container, font=('Arial', 10, 'bold'),
                                            width=4, height=2, bg="white", relief="groove", borderwidth=1,
                                            command=partial(self.handleButton, x=x, y=y, sending=True))
                self.Buts[x, y].grid(row=x, column=y, padx=0, pady=0)

    # --- LOGIC ---
    def createRoom(self):
        self.Threading_socket.stop_services()
        self.clear_board_visuals()

        self.lbl_status.config(text="Đang khởi tạo...", fg=COLOR_WARNING)
        self.update()
        time.sleep(0.5)

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
        if self.Buts[x, y]['text'] != "": return

        if sending:
            if self.my_role is None or self.my_role == "WATCH": return
            if self.my_role.strip() != current_turn_char: return
            self.Threading_socket.sendData("{}|{}|{}|".format("hit", x, y))

        if self.memory.count([x, y]) == 0: self.memory.append([x, y])

        self.Buts[x, y]['text'] = current_turn_char
        self.Buts[x, y]['fg'] = COLOR_X if current_turn_char == "X" else COLOR_O
        self.Buts[x, y]['bg'] = "#FDF2E9"

        if self.checkWin(x, y, current_turn_char):
            self.timer_running = False
            winner_msg = f"Người chơi {current_turn_char} thắng!"
            self.lbl_status.config(text=winner_msg, fg="purple")
            self.after(200, lambda: self.show_end_game_dialog(winner_msg))
            return

        self.resetTimer()

    def show_end_game_dialog(self, msg):
        self.notification("Kết thúc", msg)
        if self.my_role in ["X", "O"]:
            self.ask_rematch()
        else:
            self.lbl_status.config(text="Đang chờ chủ phòng...", fg="orange")

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
        self.clear_board_visuals()
        self.lbl_status.config(text="Ván mới bắt đầu!", fg=COLOR_SUCCESS)
        self.resetTimer()

    def clear_board_visuals(self):
        for x in range(OX_ROWS):
            for y in range(OX_COLS):
                self.Buts[x, y]["text"] = ""
                self.Buts[x, y]["bg"] = "white"
        self.memory = []
        self.timer_running = False
        self.lbl_timer.config(text="--")

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

        status_text = ""
        if self.my_role == "WATCH":
            status_text = f"Đang chờ: {next_turn}"
            fg_color = "gray"
        elif next_turn == self.my_role:
            status_text = "LƯỢT CỦA BẠN!"
            fg_color = COLOR_SUCCESS
        else:
            status_text = "Lượt đối thủ..."
            fg_color = COLOR_X

        self.lbl_status.config(text=status_text, fg=fg_color)
        self.lbl_timer.config(text=str(self.timer))

        if not hasattr(self,
                       'timer_thread_obj') or self.timer_thread_obj is None or not self.timer_thread_obj.is_alive():
            self.timer_thread_obj = threading.Thread(target=self.countdown_worker, daemon=True)
            self.timer_thread_obj.start()

    def countdown_worker(self):
        while self.timer_running:
            time.sleep(1)
            if not self.timer_running: break
            self.timer -= 1
            try:
                self.lbl_timer.config(text=str(self.timer))
            except:
                break
            if self.timer <= 0:
                if (len(self.memory) % 2 == 0 and "X" == self.my_role) or (
                        len(self.memory) % 2 != 0 and "O" == self.my_role):
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
        if count >= 6: return True
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

    def on_close(self):
        self.Threading_socket.stop_services()
        self.destroy()


class Threading_socket():
    def __init__(self, gui):
        self.conn = None
        self.server_sock = None
        self.discovery_sock = None
        self.client_list = []
        self.client_roles = {}
        self.gui = gui
        self.name = ""
        self.running = True
        self.rematch_votes = {"server": False, "client": False}

    def stop_services(self):
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except:
                pass
        if self.discovery_sock:
            try:
                self.discovery_sock.close()
            except:
                pass
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        for c in self.client_list:
            try:
                c.close()
            except:
                pass
        self.client_list = []
        self.client_roles = {}
        self.rematch_votes = {"server": False, "client": False}

    def find_room_by_code(self, room_code):
        if len(room_code) == 0: messagebox.showwarning("Lỗi", "Vui lòng nhập mã phòng!"); return
        self.stop_services()
        self.gui.clear_board_visuals()
        self.running = True
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
                self.gui.after(0, lambda: self.gui.lbl_status.config(text=f"Tìm thấy! Kết nối {server_ip}",
                                                                     fg=COLOR_SUCCESS))
                self.clientAction(server_ip)
            else:
                self.gui.after(0, lambda: self.gui.notification("Lỗi", "Phản hồi lạ!"))
        except socket.timeout:
            self.gui.after(0, lambda: self.gui.notification("Thất bại", "Không tìm thấy phòng!"))
            self.gui.after(0, lambda: self.gui.lbl_status.config(text="Không tìm thấy phòng.", fg="red"))
        except:
            self.gui.after(0, lambda: self.gui.notification("Lỗi", "Lỗi mạng LAN"))
        finally:
            udp_sock.close()

    def udp_discovery_server(self, my_room_code):
        retries = 5
        while retries > 0 and self.running:
            try:
                self.discovery_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.discovery_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.discovery_sock.bind(('0.0.0.0', DISCOVERY_PORT))
                break
            except OSError:
                retries -= 1
                time.sleep(0.5)

        if not self.discovery_sock: return
        while self.running:
            try:
                data, addr = self.discovery_sock.recvfrom(1024)
                msg = data.decode()
                if msg.startswith("FIND|") and msg.split("|")[1] == my_room_code:
                    my_ip = self.get_local_ip()
                    self.discovery_sock.sendto(f"FOUND|{my_ip}".encode(), addr)
            except:
                break

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80)); IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def clientAction(self, inputIP):
        self.stop_services()
        self.name = "client"
        self.running = True
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((inputIP, GAME_PORT))
            threading.Thread(target=self.client_listener, daemon=True).start()
        except:
            self.gui.after(0, lambda: self.gui.notification("Lỗi", "Không kết nối được TCP!"))

    def client_listener(self):
        while self.running:
            try:
                data = self.conn.recv(1024).decode()
                if not data: break

                if "RESET_GAME|" in data:
                    self.gui.after(0, self.gui.reset_board_ui)
                    data = data.replace("RESET_GAME|", "")

                if "OPP_READY|" in data:
                    self.gui.after(0, lambda: self.gui.lbl_status.config(text="Đối thủ đã sẵn sàng!", fg=COLOR_SUCCESS))
                    data = data.replace("OPP_READY|", "")

                if not data: continue

                if "ROLE|" in data:
                    parts = data.split("|")
                    try:
                        role_index = parts.index("ROLE")
                        role = parts[role_index + 1]
                        self.gui.my_role = role
                        self.gui.after(0, lambda r=role: self.gui.lbl_role.config(text=f"Vai trò: {r}"))
                        self.gui.after(0, self.gui.resetTimer)
                    except:
                        pass
                else:
                    self.gui.after(0, lambda d=data: self.process_data(d))
            except:
                break

    def serverAction(self):
        self.name = "server"
        self.running = True
        bound_success = False
        retries = 10
        while retries > 0 and self.running:
            try:
                self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_sock.bind(("0.0.0.0", GAME_PORT))
                self.server_sock.listen(5)
                bound_success = True
                break
            except OSError:
                if self.server_sock:
                    try:
                        self.server_sock.close()
                    except:
                        pass
                time.sleep(0.5)
                retries -= 1

        if not bound_success:
            self.gui.after(0, lambda: self.gui.lbl_status.config(text="Lỗi: Cổng bận!", fg="red"))
            return

        try:
            while self.running:
                try:
                    conn, addr = self.server_sock.accept()
                except OSError:
                    break

                self.client_list.append(conn)

                # --- AUTO RECONNECT LOGIC (FIX LỖI WATCH) ---
                # Kiểm tra nếu đã có X, thì đá X cũ đi, cho người mới làm X
                old_x_conn = None
                for c, r in self.client_roles.items():
                    if r == "X":
                        old_x_conn = c
                        break

                if old_x_conn:
                    # Chuyển X cũ thành Watcher
                    self.client_roles[old_x_conn] = "WATCH"
                    try:
                        old_x_conn.sendall("ROLE|WATCH|".encode())
                    except:
                        pass

                # Gán người mới làm X
                self.client_roles[conn] = "X"
                conn.sendall("ROLE|X|".encode())

                # Reset game để đồng bộ lại từ đầu
                self.rematch_votes = {"server": False, "client": False}
                self.server_reset_game()

                threading.Thread(target=self.server_handler, args=(conn,), daemon=True).start()
        except:
            pass

    def server_handler(self, conn):
        try:
            while self.running:
                data = conn.recv(1024).decode()
                if not data: break

                if "REMATCH|YES" in data:
                    self.rematch_votes["client"] = True
                    self.gui.after(0,
                                   lambda: self.gui.lbl_status.config(text="Đối thủ muốn chơi lại!", fg=COLOR_SUCCESS))
                    self.check_rematch()
                elif "REMATCH|NO" in data:
                    self.client_roles[conn] = "WATCH"
                    conn.sendall("ROLE|WATCH|".encode())
                    self.find_new_player()
                    self.gui.after(0, lambda: self.gui.lbl_status.config(text="Đối thủ làm khán giả.", fg="gray"))
                else:
                    self.gui.after(0, lambda d=data: self.process_data(d))
                    self.broadcast(data, sender_conn=conn)
        except:
            pass
        finally:
            if conn in self.client_list: self.client_list.remove(conn)
            if conn in self.client_roles: del self.client_roles[conn]
            try:
                conn.close()
            except:
                pass

    def check_rematch(self):
        if self.rematch_votes["server"] and self.rematch_votes["client"]:
            time.sleep(0.5)
            self.server_reset_game()
            self.rematch_votes = {"server": False, "client": False}
        elif self.rematch_votes["server"]:
            self.broadcast("OPP_READY|")

    def find_new_player(self):
        # Tìm người thay thế X
        has_X = any(r == "X" for r in self.client_roles.values())
        if not has_X:
            for c, r in self.client_roles.items():
                if r == "WATCH":
                    self.client_roles[c] = "X"
                    try:
                        c.sendall("ROLE|X|".encode())
                    except:
                        pass
                    time.sleep(0.1)
                    self.server_reset_game()
                    break

    def server_reset_game(self):
        self.broadcast("RESET_GAME|")
        # Gửi lại vai trò để đảm bảo đồng bộ
        for conn, role in self.client_roles.items():
            if role == "X":
                try:
                    conn.sendall("ROLE|X|".encode())
                except:
                    pass
        self.gui.after(0, self.gui.reset_board_ui)

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
                self.rematch_votes["server"] = True
                self.check_rematch()
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