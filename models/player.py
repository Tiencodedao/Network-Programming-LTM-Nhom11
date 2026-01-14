"""
Player - Quản lý thông tin người chơi
"""


class Player:
    def __init__(self, role=None):
        """
        Args:
            role: "O" (Server), "X" (Client), "WATCH" (Khán giả)
        """
        self.role = role
        self.timer = 30
        self.is_my_turn = False

    def set_role(self, role):
        """Đặt vai trò cho người chơi"""
        self.role = role

    def reset_timer(self, time_limit=30):
        """Reset đồng hồ đếm ngược"""
        self.timer = time_limit

    def is_player(self):
        """Kiểm tra có phải là người chơi không (không phải khán giả)"""
        return self.role in ["O", "X"]

    def is_watcher(self):
        """Kiểm tra có phải là khán giả không"""
        return self.role == "WATCH"

    def can_move(self, current_turn):
        """Kiểm tra có thể đánh không"""
        return self.role == current_turn and self.is_player()

