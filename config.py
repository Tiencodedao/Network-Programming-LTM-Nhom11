"""
Cấu hình cho game Caro
"""

# Cấu hình bàn cờ
BOARD_ROWS = 15  # Số hàng
BOARD_COLS = 20  # Số cột
WIN_CONDITION = 5  # Số quân liên tiếp để thắng

# Cấu hình giao diện
BUTTON_FONT = ('arial', 15, 'bold')
BUTTON_HEIGHT = 1
BUTTON_WIDTH = 2
BUTTON_BORDER_WIDTH = 2

# Cấu hình mạng
DEFAULT_PORT = 8000
BUFFER_SIZE = 1024

# Ký hiệu người chơi
PLAYER_O = 'O'
PLAYER_X = 'X'

# Actions
ACTION_HIT = "hit"
ACTION_UNDO = "Undo"
ACTION_NEW_GAME = "new_game"

# Roles
ROLE_SERVER = "server"
ROLE_CLIENT = "client"

