"""
AI Module - Trí tuệ nhân tạo cho game Cờ Caro
"""
import random
import time


class CaroAI:
    """
    AI cho game Cờ Caro
    Sử dụng thuật toán Minimax với Alpha-Beta pruning và đánh giá pattern thông minh
    """

    # Điểm số cho các pattern khác nhau
    PATTERNS = {
        'five': 100000,      # 5 quân liên tiếp - thắng
        'open_four': 10000,  # 4 quân 2 đầu trống: _XXXX_
        'four': 5000,        # 4 quân 1 đầu bị chặn: XXXX_ hoặc _XXXX
        'open_three': 1000,  # 3 quân 2 đầu trống: _XXX_
        'three': 500,        # 3 quân 1 đầu bị chặn
        'open_two': 100,     # 2 quân 2 đầu trống: _XX_
        'two': 50,           # 2 quân
        'one': 10            # 1 quân
    }

    def __init__(self, symbol='O', difficulty='medium'):
        """
        Args:
            symbol: Ký hiệu của AI ('O' hoặc 'X')
            difficulty: Độ khó ('easy', 'medium', 'hard')
        """
        self.symbol = symbol
        self.opponent_symbol = 'X' if symbol == 'O' else 'O'
        self.difficulty = difficulty
        self.max_depth = {'easy': 1, 'medium': 2, 'hard': 3}[difficulty]

    def get_move(self, board, rows, cols, win_condition=5):
        """
        Tính toán nước đi tốt nhất cho AI
        
        Args:
            board: Ma trận bàn cờ (2D list hoặc dict)
            rows: Số hàng
            cols: Số cột
            win_condition: Số quân liên tiếp để thắng
            
        Returns:
            tuple: (row, col) vị trí đánh
        """
        if self.difficulty == 'easy':
            # Easy mode: 70% random, 30% smart
            if random.random() < 0.7:
                return self._get_random_move(board, rows, cols)
            else:
                return self._get_smart_move(board, rows, cols, win_condition)
        elif self.difficulty == 'medium':
            return self._get_smart_move(board, rows, cols, win_condition)
        else:  # hard
            return self._get_best_move(board, rows, cols, win_condition)

    def _get_cell(self, board, r, c):
        """Helper function to get cell value from board (supports both dict and 2D array)"""
        if isinstance(board, dict):
            return board.get((r, c), "")
        else:
            return board[r][c]

    def _set_cell(self, board, r, c, value):
        """Helper function to set cell value (supports both dict and 2D array)"""
        if isinstance(board, dict):
            if value == "":
                if (r, c) in board:
                    del board[(r, c)]
            else:
                board[(r, c)] = value
        else:
            board[r][c] = value

    def _get_random_move(self, board, rows, cols):
        """Chọn nước đi ngẫu nhiên"""
        empty_cells = []
        for r in range(rows):
            for c in range(cols):
                if self._get_cell(board, r, c) == "":
                    empty_cells.append((r, c))
        
        if empty_cells:
            return random.choice(empty_cells)
        return None

    def _get_smart_move(self, board, rows, cols, win_condition):
        """
        Chọn nước đi thông minh với đánh giá điểm số:
        1. Kiểm tra xem có thể thắng ngay không
        2. Chặn đối thủ nếu họ sắp thắng
        3. Tạo các dãy nguy hiểm
        4. Chọn vị trí tốt nhất dựa trên điểm số
        """
        # 1. Kiểm tra thắng ngay
        winning_move = self._find_winning_move(board, rows, cols, win_condition, self.symbol)
        if winning_move:
            return winning_move

        # 2. Chặn đối thủ nếu có 4 quân liên tiếp
        blocking_move = self._find_winning_move(board, rows, cols, win_condition, self.opponent_symbol)
        if blocking_move:
            return blocking_move

        # 3. Đánh giá tất cả các nước đi có thể
        scored_moves = []
        candidates = self._get_candidate_moves(board, rows, cols)

        for r, c in candidates:
            # Tính điểm tấn công (khi AI đánh)
            self._set_cell(board, r, c, self.symbol)
            attack_score = self._evaluate_board_position(board, r, c, self.symbol, win_condition, rows, cols)
            self._set_cell(board, r, c, "")

            # Tính điểm phòng thủ (khi đối thủ đánh)
            self._set_cell(board, r, c, self.opponent_symbol)
            defense_score = self._evaluate_board_position(board, r, c, self.opponent_symbol, win_condition, rows, cols)
            self._set_cell(board, r, c, "")

            # Tổng điểm = tấn công + phòng thủ (phòng thủ quan trọng hơn một chút)
            total_score = attack_score + defense_score * 1.1

            # Thêm một chút random để khó đoán (±10%)
            randomness = random.uniform(0.9, 1.1)
            total_score *= randomness

            scored_moves.append((total_score, r, c))

        if not scored_moves:
            return self._get_random_move(board, rows, cols)

        # Sắp xếp theo điểm số
        scored_moves.sort(reverse=True)

        # Chọn ngẫu nhiên trong top 3 nước đi tốt nhất để khó đoán hơn
        top_moves = scored_moves[:min(3, len(scored_moves))]
        weights = [move[0] for move in top_moves]

        # Weighted random choice
        if sum(weights) > 0:
            chosen = random.choices(top_moves, weights=weights, k=1)[0]
            return (chosen[1], chosen[2])
        else:
            return (top_moves[0][1], top_moves[0][2])

    def _get_best_move(self, board, rows, cols, win_condition):
        """
        Sử dụng Minimax với alpha-beta pruning cho hard mode
        """
        # Kiểm tra thắng ngay hoặc chặn
        winning_move = self._find_winning_move(board, rows, cols, win_condition, self.symbol)
        if winning_move:
            return winning_move

        blocking_move = self._find_winning_move(board, rows, cols, win_condition, self.opponent_symbol)
        if blocking_move:
            return blocking_move

        # Sử dụng minimax cho các trường hợp khác
        candidates = self._get_candidate_moves(board, rows, cols)

        if not candidates:
            return self._get_random_move(board, rows, cols)

        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        # Giới hạn số nước đi cần xem xét (tối đa 15 nước)
        if len(candidates) > 15:
            # Đánh giá sơ bộ và lấy top 15
            scored = []
            for r, c in candidates:
                self._set_cell(board, r, c, self.symbol)
                score = self._evaluate_board_position(board, r, c, self.symbol, win_condition, rows, cols)
                self._set_cell(board, r, c, "")
                scored.append((score, r, c))
            scored.sort(reverse=True)
            candidates = [(r, c) for _, r, c in scored[:15]]

        for r, c in candidates:
            self._set_cell(board, r, c, self.symbol)
            score = self._minimax(board, rows, cols, win_condition, 0, False, alpha, beta)
            self._set_cell(board, r, c, "")

            if score > best_score:
                best_score = score
                best_move = (r, c)

            alpha = max(alpha, score)

        return best_move if best_move else candidates[0]

    def _find_winning_move(self, board, rows, cols, win_condition, symbol):
        """Tìm nước đi để thắng ngay (hoặc chặn đối thủ thắng)"""
        for r in range(rows):
            for c in range(cols):
                if self._get_cell(board, r, c) == "":
                    # Thử đánh vào ô này
                    self._set_cell(board, r, c, symbol)
                    if self._check_win(board, r, c, symbol, win_condition, rows, cols):
                        self._set_cell(board, r, c, "")  # Hoàn tác
                        return (r, c)
                    self._set_cell(board, r, c, "")  # Hoàn tác
        return None

    def _find_threat_move(self, board, rows, cols, win_condition):
        """Tìm nước đi tạo ra dãy nguy hiểm (3-4 quân) - Deprecated, dùng _get_smart_move thay thế"""
        return None

    def _get_candidate_moves(self, board, rows, cols, distance=2):
        """Lấy danh sách các ô trống gần các quân đã đánh"""
        candidates = set()
        has_pieces = False

        for r in range(rows):
            for c in range(cols):
                if self._get_cell(board, r, c) != "":
                    has_pieces = True
                    # Tìm các ô trống xung quanh
                    for dr in range(-distance, distance + 1):
                        for dc in range(-distance, distance + 1):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < rows and 0 <= nc < cols and
                                self._get_cell(board, nr, nc) == ""):
                                candidates.add((nr, nc))

        # Nếu bàn cờ trống, đánh ở giữa
        if not has_pieces:
            return [(rows // 2, cols // 2)]

        return list(candidates)

    def _evaluate_board_position(self, board, row, col, symbol, win_condition, rows, cols):
        """
        Đánh giá điểm số của một vị trí dựa trên các pattern
        """
        total_score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            # Đếm số quân liên tiếp và kiểm tra 2 đầu
            count = 1
            open_ends = 0

            # Đếm về phía trước
            r, c = row + dr, col + dc
            steps_forward = 0
            while 0 <= r < rows and 0 <= c < cols and steps_forward < win_condition:
                if self._get_cell(board, r, c) == symbol:
                    count += 1
                    r += dr
                    c += dc
                    steps_forward += 1
                elif self._get_cell(board, r, c) == "":
                    open_ends += 1
                    break
                else:
                    break

            # Đếm về phía sau
            r, c = row - dr, col - dc
            steps_backward = 0
            while 0 <= r < rows and 0 <= c < cols and steps_backward < win_condition:
                if self._get_cell(board, r, c) == symbol:
                    count += 1
                    r -= dr
                    c -= dc
                    steps_backward += 1
                elif self._get_cell(board, r, c) == "":
                    open_ends += 1
                    break
                else:
                    break

            # Tính điểm dựa trên pattern
            if count >= win_condition:
                total_score += self.PATTERNS['five']
            elif count == 4:
                if open_ends == 2:
                    total_score += self.PATTERNS['open_four']
                else:
                    total_score += self.PATTERNS['four']
            elif count == 3:
                if open_ends == 2:
                    total_score += self.PATTERNS['open_three']
                else:
                    total_score += self.PATTERNS['three']
            elif count == 2:
                if open_ends == 2:
                    total_score += self.PATTERNS['open_two']
                else:
                    total_score += self.PATTERNS['two']
            else:
                total_score += self.PATTERNS['one']

        return total_score

    def _minimax(self, board, rows, cols, win_condition, depth, is_maximizing, alpha, beta):
        """
        Thuật toán Minimax với Alpha-Beta pruning
        """
        # Điều kiện dừng
        if depth >= self.max_depth:
            return self._evaluate_full_board(board, rows, cols, win_condition)

        candidates = self._get_candidate_moves(board, rows, cols, distance=1)

        if not candidates:
            return 0

        # Giới hạn số nước đi xem xét ở mỗi cấp
        if len(candidates) > 10:
            candidates = candidates[:10]

        if is_maximizing:
            max_eval = float('-inf')
            for r, c in candidates:
                self._set_cell(board, r, c, self.symbol)

                # Kiểm tra thắng
                if self._check_win(board, r, c, self.symbol, win_condition, rows, cols):
                    self._set_cell(board, r, c, "")
                    return self.PATTERNS['five']

                eval_score = self._minimax(board, rows, cols, win_condition, depth + 1, False, alpha, beta)
                self._set_cell(board, r, c, "")

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break  # Alpha-Beta pruning

            return max_eval
        else:
            min_eval = float('inf')
            for r, c in candidates:
                self._set_cell(board, r, c, self.opponent_symbol)

                # Kiểm tra thua
                if self._check_win(board, r, c, self.opponent_symbol, win_condition, rows, cols):
                    self._set_cell(board, r, c, "")
                    return -self.PATTERNS['five']

                eval_score = self._minimax(board, rows, cols, win_condition, depth + 1, True, alpha, beta)
                self._set_cell(board, r, c, "")

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    break  # Alpha-Beta pruning

            return min_eval

    def _evaluate_full_board(self, board, rows, cols, win_condition):
        """Đánh giá toàn bộ bàn cờ"""
        ai_score = 0
        opponent_score = 0

        # Đánh giá cho tất cả các vị trí có quân
        for r in range(rows):
            for c in range(cols):
                cell = self._get_cell(board, r, c)
                if cell == self.symbol:
                    ai_score += self._evaluate_board_position(board, r, c, self.symbol, win_condition, rows, cols)
                elif cell == self.opponent_symbol:
                    opponent_score += self._evaluate_board_position(board, r, c, self.opponent_symbol, win_condition, rows, cols)

        return ai_score - opponent_score

    def _find_near_move(self, board, rows, cols, distance=2):
        """Tìm ô trống gần các quân đã đánh"""
        candidates = []
        
        for r in range(rows):
            for c in range(cols):
                if self._get_cell(board, r, c) != "":
                    # Tìm các ô trống xung quanh
                    for dr in range(-distance, distance + 1):
                        for dc in range(-distance, distance + 1):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < rows and 0 <= nc < cols and 
                                self._get_cell(board, nr, nc) == "" and (nr, nc) not in candidates):
                                candidates.append((nr, nc))
        
        if candidates:
            return random.choice(candidates)
        return None

    def _check_win(self, board, row, col, symbol, win_condition, rows, cols):
        """Kiểm tra xem nước đi tại (row, col) có thắng không"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # Đếm về phía trước
            r, c = row + dr, col + dc
            while 0 <= r < rows and 0 <= c < cols and self._get_cell(board, r, c) == symbol:
                count += 1
                r += dr
                c += dc
            
            # Đếm về phía sau
            r, c = row - dr, col - dc
            while 0 <= r < rows and 0 <= c < cols and self._get_cell(board, r, c) == symbol:
                count += 1
                r -= dr
                c -= dc
            
            if count >= win_condition:
                return True
        
        return False

    def _evaluate_position(self, board, row, col, symbol, win_condition, rows, cols):
        """Đánh giá điểm số của một vị trí"""
        max_count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # Đếm về phía trước
            r, c = row + dr, col + dc
            while 0 <= r < rows and 0 <= c < cols and self._get_cell(board, r, c) == symbol:
                count += 1
                r += dr
                c += dc
            
            # Đếm về phía sau
            r, c = row - dr, col - dc
            while 0 <= r < rows and 0 <= c < cols and self._get_cell(board, r, c) == symbol:
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

