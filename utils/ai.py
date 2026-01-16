"""
AI Module - Trí tuệ nhân tạo cho game Cờ Caro
"""
import random
import time


class CaroAI:
    """
    AI cho game Cờ Caro
    Sử dụng thuật toán Minimax với Alpha-Beta pruning (có thể đơn giản hóa)
    """

    def __init__(self, symbol='O', difficulty='medium'):
        """
        Args:
            symbol: Ký hiệu của AI ('O' hoặc 'X')
            difficulty: Độ khó ('easy', 'medium', 'hard')
        """
        self.symbol = symbol
        self.opponent_symbol = 'X' if symbol == 'O' else 'O'
        self.difficulty = difficulty

    def get_move(self, board, rows, cols, win_condition=5):
        """
        Tính toán nước đi tốt nhất cho AI
        
        Args:
            board: Ma trận bàn cờ (2D list)
            rows: Số hàng
            cols: Số cột
            win_condition: Số quân liên tiếp để thắng
            
        Returns:
            tuple: (row, col) vị trí đánh
        """
        if self.difficulty == 'easy':
            return self._get_random_move(board, rows, cols)
        elif self.difficulty == 'medium':
            return self._get_smart_move(board, rows, cols, win_condition)
        else:  # hard
            return self._get_best_move(board, rows, cols, win_condition)

    def _get_random_move(self, board, rows, cols):
        """Chọn nước đi ngẫu nhiên"""
        empty_cells = []
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == "":
                    empty_cells.append((r, c))
        
        if empty_cells:
            return random.choice(empty_cells)
        return None

    def _get_smart_move(self, board, rows, cols, win_condition):
        """
        Chọn nước đi thông minh:
        1. Kiểm tra xem có thể thắng ngay không
        2. Chặn đối thủ nếu họ sắp thắng
        3. Tạo các dãy nguy hiểm
        4. Random nếu không có nước đặc biệt
        """
        # 1. Kiểm tra thắng ngay
        winning_move = self._find_winning_move(board, rows, cols, win_condition, self.symbol)
        if winning_move:
            return winning_move

        # 2. Chặn đối thủ
        blocking_move = self._find_winning_move(board, rows, cols, win_condition, self.opponent_symbol)
        if blocking_move:
            return blocking_move

        # 3. Tạo dãy nguy hiểm (3 hoặc 4 quân)
        threat_move = self._find_threat_move(board, rows, cols, win_condition)
        if threat_move:
            return threat_move

        # 4. Đánh gần các quân đã có
        near_move = self._find_near_move(board, rows, cols)
        if near_move:
            return near_move

        # 5. Random
        return self._get_random_move(board, rows, cols)

    def _get_best_move(self, board, rows, cols, win_condition):
        """
        Sử dụng Minimax với alpha-beta pruning
        (Đơn giản hóa - chỉ tìm kiếm sâu 2-3 lớp)
        """
        # Tạm thời dùng smart move cho hard mode
        # Có thể cải thiện sau với minimax đầy đủ
        return self._get_smart_move(board, rows, cols, win_condition)

    def _find_winning_move(self, board, rows, cols, win_condition, symbol):
        """Tìm nước đi để thắng ngay (hoặc chặn đối thủ thắng)"""
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == "":
                    # Thử đánh vào ô này
                    board[r][c] = symbol
                    if self._check_win(board, r, c, symbol, win_condition):
                        board[r][c] = ""  # Hoàn tác
                        return (r, c)
                    board[r][c] = ""  # Hoàn tác
        return None

    def _find_threat_move(self, board, rows, cols, win_condition):
        """Tìm nước đi tạo ra dãy nguy hiểm (3-4 quân)"""
        best_score = -1
        best_move = None

        for r in range(rows):
            for c in range(cols):
                if board[r][c] == "":
                    board[r][c] = self.symbol
                    score = self._evaluate_position(board, r, c, self.symbol, win_condition)
                    board[r][c] = ""
                    
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)

        if best_score >= 3:  # Có ít nhất 3 quân liên tiếp
            return best_move
        return None

    def _find_near_move(self, board, rows, cols, distance=2):
        """Tìm ô trống gần các quân đã đánh"""
        candidates = []
        
        for r in range(rows):
            for c in range(cols):
                if board[r][c] != "":
                    # Tìm các ô trống xung quanh
                    for dr in range(-distance, distance + 1):
                        for dc in range(-distance, distance + 1):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < rows and 0 <= nc < cols and 
                                board[nr][nc] == "" and (nr, nc) not in candidates):
                                candidates.append((nr, nc))
        
        if candidates:
            return random.choice(candidates)
        return None

    def _check_win(self, board, row, col, symbol, win_condition):
        """Kiểm tra xem nước đi tại (row, col) có thắng không"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # Đếm về phía trước
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r += dr
                c += dc
            
            # Đếm về phía sau
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r -= dr
                c -= dc
            
            if count >= win_condition:
                return True
        
        return False

    def _evaluate_position(self, board, row, col, symbol, win_condition):
        """Đánh giá điểm số của một vị trí"""
        max_count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # Đếm về phía trước
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r += dr
                c += dc
            
            # Đếm về phía sau
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r -= dr
                c -= dc
            
            max_count = max(max_count, count)
        
        return max_count


def test_ai():
    """Test AI"""
    # Tạo bàn cờ 15x20
    board = [["" for _ in range(20)] for _ in range(15)]
    
    # Đặt một vài quân
    board[7][10] = 'X'
    board[7][11] = 'X'
    board[7][12] = 'X'
    board[7][13] = 'X'
    
    # AI phải chặn
    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 20, 5)
    print(f"AI suggests move: {move}")
    
    # Nên là (7, 9) hoặc (7, 14) để chặn


if __name__ == "__main__":
    test_ai()

