"""
Caro LAN Game - Main Entry Point
File chính để chạy game với cấu trúc modular
"""

from ui.main_window import CaroWindow


if __name__ == "__main__":
    app = CaroWindow()
    app.mainloop()

