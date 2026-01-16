"""
Caro LAN Game - Main Entry Point
File chính để chạy game với cấu trúc modular
"""

from ui.menu_screen import MenuScreen
from ui.main_window import CaroWindow


def start_game(mode):
    """Khởi động game với mode đã chọn"""
    if mode:
        # Xử lý mode AI với độ khó
        if mode.startswith("ai:"):
            difficulty = mode.split(":")[1]
            app = CaroWindow(initial_mode="ai", ai_difficulty=difficulty)
        elif mode == "pvp":
            app = CaroWindow(initial_mode="pvp")
        else:
            return

        app.mainloop()


if __name__ == "__main__":
    # Hiển thị menu trước
    menu = MenuScreen(on_mode_selected=start_game)
    menu.mainloop()


