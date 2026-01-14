"""
GameState - Quản lý trạng thái bàn cờ và logic game
"""


class GameState:
    def __init__(self, rows=15, cols=20, win_condition=5):
        self.rows = rows
        self.cols = cols
        self.win_condition = win_condition
        self.memory = []  # Lưu lịch sử các nước đi [x, y]
        self.board = {}  # Trạng thái bàn cờ

    def reset(self):
        """Reset bàn cờ về trạng thái ban đầu"""
        self.memory = []
        self.board = {}

    def add_move(self, x, y):
        """Thêm nước đi mới"""
        if self.memory.count([x, y]) == 0:
            self.memory.append([x, y])
            return True
        return False

    def undo_last_move(self):
        """Hoàn tác nước đi cuối cùng"""
        if len(self.memory) > 0:
            last = self.memory.pop()
            return last
        return None

    def get_current_turn(self):
        """Trả về lượt hiện tại ('X' hoặc 'O')"""
        return "X" if len(self.memory) % 2 == 0 else "O"

    def check_win(self, x, y, player_symbol):
        """
        Kiểm tra điều kiện thắng tại vị trí (x, y)

        Args:
            x, y: tọa độ vừa đánh
            player_symbol: 'X' hoặc 'O'

        Returns:
            True nếu thắng, False nếu không
        """
        directions = [
            (0, 1),   # Ngang
            (1, 0),   # Dọc
            (1, 1),   # Chéo chính
            (1, -1)   # Chéo phụ
        ]

        for dx, dy in directions:
            count = 1  # Đếm ô hiện tại

            # Đếm về phía dương
            i, j = x + dx, y + dy
            while 0 <= i < self.rows and 0 <= j < self.cols and self.board.get((i, j)) == player_symbol:
                count += 1
                i += dx
                j += dy

            # Đếm về phía âm
            i, j = x - dx, y - dy
            while 0 <= i < self.rows and 0 <= j < self.cols and self.board.get((i, j)) == player_symbol:
                count += 1
                i -= dx
                j -= dy

            if count >= self.win_condition:
                return True

        return False

    def update_board(self, x, y, symbol):
        """Cập nhật trạng thái bàn cờ"""
        self.board[(x, y)] = symbol

    def clear_cell(self, x, y):
        """Xóa ô trên bàn cờ"""
        if (x, y) in self.board:
            del self.board[(x, y)]

