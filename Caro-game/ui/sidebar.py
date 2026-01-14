"""
SidebarWidget - Component thanh bên
"""
import tkinter as tk
from ui.chat_widget import ChatWidget


class SidebarWidget(tk.Frame):
    def __init__(self, parent, on_join_room=None, on_create_room=None, on_undo=None, on_chat_send=None):
        """
        Args:
            parent: Widget cha
            on_join_room: Callback khi vào phòng (room_code)
            on_create_room: Callback khi tạo phòng
            on_undo: Callback khi undo
            on_chat_send: Callback khi gửi tin nhắn chat (text)
        """
        super().__init__(parent, bg="#34495E", width=250, padx=10, pady=10)
        self.pack_propagate(False)

        self.on_join_room = on_join_room
        self.on_create_room = on_create_room
        self.on_undo = on_undo
        self.on_chat_send = on_chat_send

        self.chat_widget = None  # Sẽ được tạo trong _create_widgets

        self._create_widgets()

    def _create_widgets(self):
        """Tạo các widget trong sidebar"""
        # Tiêu đề
        lbl_title = tk.Label(
            self,
            text="CARO LAN",
            font=("Helvetica", 20, "bold"),
            bg="#34495E",
            fg="#F1C40F"
        )
        lbl_title.pack(pady=(10, 20))

        # Khu vực kết nối
        lbl_room = tk.Label(
            self,
            text="MÃ PHÒNG:",
            font=("Arial", 10, "bold"),
            bg="#34495E",
            fg="#ECF0F1"
        )
        lbl_room.pack(anchor="w")

        self.entry_code = tk.Entry(self, font=("Arial", 14), justify='center', bg="#FFF")
        self.entry_code.pack(fill=tk.X, pady=5)

        btn_join = tk.Button(
            self,
            text="VÀO PHÒNG",
            bg="#2ECC71",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self._handle_join_room
        )
        btn_join.pack(fill=tk.X, pady=5)

        btn_create = tk.Button(
            self,
            text="TẠO PHÒNG",
            bg="#E67E22",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self._handle_create_room
        )
        btn_create.pack(fill=tk.X, pady=5)

        # Đường kẻ ngang
        tk.Frame(self, height=2, bg="#ECF0F1").pack(fill=tk.X, pady=20)

        # Thông tin người chơi
        self.lbl_role = tk.Label(
            self,
            text="Vai trò: Chưa có",
            font=("Arial", 12),
            bg="#34495E",
            fg="#ECF0F1"
        )
        self.lbl_role.pack(pady=10)

        # Đồng hồ đếm ngược
        self.lbl_timer = tk.Label(
            self,
            text="30s",
            font=("Helvetica", 40, "bold"),
            bg="#34495E",
            fg="#F1C40F"
        )
        self.lbl_timer.pack(pady=10)

        # Trạng thái game
        self.lbl_status = tk.Label(
            self,
            text="Hãy tạo hoặc vào phòng...",
            font=("Arial", 11, "italic"),
            bg="#34495E",
            fg="#BDC3C7",
            wraplength=230
        )
        self.lbl_status.pack(pady=10)

        # Nút chức năng
        btn_undo = tk.Button(
            self,
            text="Đi lại (Undo)",
            bg="#95A5A6",
            fg="white",
            command=self._handle_undo
        )
        btn_undo.pack(fill=tk.X, pady=(0, 10))

        # Chat box
        chat_frame = tk.LabelFrame(
            self,
            text="💬 Chat",
            font=("Arial", 10, "bold"),
            bg="#34495E",
            fg="#ECF0F1",
            padx=5,
            pady=5
        )
        chat_frame.pack(fill='both', expand=True, pady=(5, 0))

        self.chat_widget = ChatWidget(
            chat_frame,
            on_send=self._handle_chat_send
        )
        self.chat_widget.pack(fill='both', expand=True)

    def _handle_join_room(self):
        """Xử lý nút vào phòng"""
        if self.on_join_room:
            room_code = self.entry_code.get()
            self.on_join_room(room_code)

    def _handle_create_room(self):
        """Xử lý nút tạo phòng"""
        if self.on_create_room:
            self.on_create_room()

    def _handle_undo(self):
        """Xử lý nút undo"""
        if self.on_undo:
            self.on_undo()

    def _handle_chat_send(self, text):
        """Xử lý gửi tin nhắn chat"""
        if self.on_chat_send:
            self.on_chat_send(text)

    def add_chat_message(self, sender, message):
        """Thêm tin nhắn vào chat box"""
        if self.chat_widget:
            self.chat_widget.add_message(sender, message)

    def set_room_code(self, room_code):
        """Đặt mã phòng"""
        self.entry_code.delete(0, tk.END)
        self.entry_code.insert(0, room_code)

    def set_role(self, role_text):
        """Cập nhật vai trò"""
        self.lbl_role.config(text=f"Vai trò: {role_text}")

    def set_timer(self, seconds):
        """Cập nhật đồng hồ"""
        self.lbl_timer.config(text=f"{seconds}s")

    def set_status(self, text, color="#ECF0F1"):
        """Cập nhật trạng thái"""
        self.lbl_status.config(text=text, fg=color)

