"""
MenuScreen - Màn hình menu chính của game Cờ Caro
"""
import tkinter as tk
from tkinter import font as tkfont


class MenuScreen(tk.Tk):
    """
    Màn hình menu chính với 2 chế độ:
    1. Chơi với máy (AI)
    2. Chơi 2 người (LAN)
    """

    def __init__(self, on_mode_selected=None):
        super().__init__()
        self.title("Start")
        self.geometry("560x340")
        self.configure(bg='#F0F0F0')
        self.resizable(False, False)

        self.on_mode_selected = on_mode_selected

        self._create_widgets()

        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """Tạo các widget cho menu"""

        # Title - Game Caro
        title_font = tkfont.Font(family='Arial', size=32, weight='bold')
        title_label = tk.Label(
            self,
            text="Game Caro",
            font=title_font,
            bg='#F0F0F0',
            fg='black'
        )
        title_label.pack(pady=(50, 30))

        # Subtitle
        subtitle_label = tk.Label(
            self,
            text="Vui lòng chọn chế độ chơi",
            font=('Arial', 14),
            bg='#F0F0F0',
            fg='black'
        )
        subtitle_label.pack(pady=(0, 40))

        # Container for buttons
        button_frame = tk.Frame(self, bg='#F0F0F0')
        button_frame.pack(pady=20)

        # Button style
        button_font = ('Arial', 11)
        button_width = 15
        button_height = 2

        # Chơi với máy button
        btn_ai = tk.Button(
            button_frame,
            text="Chơi với máy",
            font=button_font,
            bg='white',
            fg='black',
            width=button_width,
            height=button_height,
            relief='raised',
            borderwidth=2,
            cursor='hand2',
            command=self._on_play_ai
        )
        btn_ai.grid(row=0, column=0, padx=20)

        # Chơi 2 người button
        btn_pvp = tk.Button(
            button_frame,
            text="Chơi 2 người",
            font=button_font,
            bg='white',
            fg='black',
            width=button_width,
            height=button_height,
            relief='raised',
            borderwidth=2,
            cursor='hand2',
            command=self._on_play_pvp
        )
        btn_pvp.grid(row=0, column=1, padx=20)

    def _on_play_ai(self):
        """Xử lý khi chọn chơi với máy"""
        self.withdraw()
        if callable(self.on_mode_selected):
            self.on_mode_selected("ai:medium")

    def _on_play_pvp(self):
        """Xử lý khi chọn chơi 2 người"""
        self.withdraw()
        if callable(self.on_mode_selected):
            self.on_mode_selected("pvp")


def show_menu(on_mode_selected=None):
    """
    Hiển thị màn hình menu và chờ người dùng chọn

    Args:
        on_mode_selected: Callback nhận mode đã chọn ("pvp", "ai")

    Returns:
        str: Mode đã chọn hoặc None
    """
    menu = MenuScreen(on_mode_selected=on_mode_selected)
    menu.mainloop()


if __name__ == "__main__":
    # Test menu
    def on_select(mode):
        print(f"Selected mode: {mode}")

    show_menu(on_select)

