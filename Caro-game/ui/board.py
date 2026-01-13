"""
BoardWidget - Component hiển thị bàn cờ
"""
import tkinter as tk
from functools import partial


class BoardWidget(tk.Frame):
    def __init__(self, parent, rows=15, cols=20, on_button_click=None):
        """
        Args:
            parent: Widget cha
            rows: Số hàng
            cols: Số cột
            on_button_click: Callback khi click button (x, y)
        """
        super().__init__(parent, bg="#ECF0F1", padx=10, pady=10)

        self.rows = rows
        self.cols = cols
        self.buttons = {}
        self.on_button_click = on_button_click

        self._create_board()

    def _create_board(self):
        """Tạo grid buttons"""
        # Container để center grid
        grid_container = tk.Frame(self, bg="#ECF0F1")
        grid_container.place(relx=0.5, rely=0.5, anchor="center")

        for x in range(self.rows):
            for y in range(self.cols):
                btn = tk.Button(
                    grid_container,
                    font=('Arial', 10, 'bold'),
                    width=4,
                    height=2,
                    bg="white",
                    relief="groove",
                    borderwidth=1,
                    command=partial(self._handle_click, x=x, y=y)
                )
                btn.grid(row=x, column=y, padx=0, pady=0)
                self.buttons[x, y] = btn

    def _handle_click(self, x, y):
        """Xử lý khi click button"""
        if self.on_button_click:
            self.on_button_click(x, y)

    def set_cell(self, x, y, text, color="#000", bg_color="#FDF2E9"):
        """
        Đặt giá trị cho ô

        Args:
            x, y: Tọa độ
            text: Text hiển thị (X hoặc O)
            color: Màu chữ
            bg_color: Màu nền
        """
        if (x, y) in self.buttons:
            self.buttons[x, y]['text'] = text
            self.buttons[x, y]['fg'] = color
            self.buttons[x, y]['bg'] = bg_color

    def clear_cell(self, x, y):
        """Xóa nội dung ô"""
        if (x, y) in self.buttons:
            self.buttons[x, y]['text'] = ""
            self.buttons[x, y]['bg'] = "white"

    def get_cell_text(self, x, y):
        """Lấy text của ô"""
        if (x, y) in self.buttons:
            return self.buttons[x, y]['text']
        return ""

    def reset(self):
        """Reset toàn bộ bàn cờ"""
        for x in range(self.rows):
            for y in range(self.cols):
                self.clear_cell(x, y)

    def highlight_cell(self, x, y, color="#FFFACD"):
        """Highlight một ô"""
        if (x, y) in self.buttons:
            self.buttons[x, y]['bg'] = color

    def disable_all(self):
        """Vô hiệu hóa tất cả buttons"""
        for btn in self.buttons.values():
            btn['state'] = 'disabled'

    def enable_all(self):
        """Kích hoạt tất cả buttons"""
        for btn in self.buttons.values():
            btn['state'] = 'normal'

