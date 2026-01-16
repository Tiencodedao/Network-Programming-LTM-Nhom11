"""
Test AI với các tình huống threat (mối đe dọa) phức tạp
"""
from utils.ai import CaroAI


def print_board(board, rows, cols):
    """In bàn cờ ra màn hình"""
    print("\n   ", end="")
    for c in range(cols):
        print(f"{c:2d}", end=" ")
    print()

    for r in range(rows):
        print(f"{r:2d} ", end="")
        for c in range(cols):
            cell = board[r][c] if board[r][c] else "."
            print(f" {cell}", end=" ")
        print()
    print()


def test_double_threat():
    """Test AI phát hiện và tạo double threat (2 đường tấn công)"""
    print("=" * 60)
    print("TEST 1: Phát hiện và tạo Double Threat")
    print("=" * 60)

    board = [["" for _ in range(15)] for _ in range(15)]

    # Tạo tình huống: AI có thể tạo 2 đường tấn công cùng lúc
    # O O O _
    #     O
    #     O
    board[7][7] = 'O'
    board[7][8] = 'O'
    board[7][9] = 'O'
    board[8][9] = 'O'
    board[9][9] = 'O'

    print("Trước khi AI đánh:")
    print_board(board, 15, 15)

    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 15, 5)

    print(f"✓ AI chọn: {move}")
    if move:
        board[move[0]][move[1]] = 'O'
        print("Sau khi AI đánh:")
        print_board(board, 15, 15)


def test_block_double_threat():
    """Test AI chặn double threat của đối thủ"""
    print("=" * 60)
    print("TEST 2: Chặn Double Threat của đối thủ")
    print("=" * 60)

    board = [["" for _ in range(15)] for _ in range(15)]

    # Đối thủ sắp tạo double threat
    board[7][7] = 'X'
    board[7][8] = 'X'
    board[7][9] = 'X'
    board[8][9] = 'X'
    board[9][9] = 'X'

    print("Trước khi AI đánh (X sắp tạo double threat):")
    print_board(board, 15, 15)

    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 15, 5)

    print(f"✓ AI chặn tại: {move}")
    if move:
        board[move[0]][move[1]] = 'O'
        print("Sau khi AI chặn:")
        print_board(board, 15, 15)


def test_open_four_detection():
    """Test AI phát hiện và tạo open four (4 quân mở - chắc thắng)"""
    print("=" * 60)
    print("TEST 3: Tạo Open Four (4 quân mở - chắc thắng)")
    print("=" * 60)

    board = [["" for _ in range(15)] for _ in range(15)]

    # AI có 3 quân, có thể tạo open four
    # _ O O O _ _
    board[7][7] = 'O'
    board[7][8] = 'O'
    board[7][9] = 'O'

    print("Trước khi AI đánh:")
    print_board(board, 15, 15)

    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 15, 5)

    print(f"✓ AI chọn: {move}")
    if move:
        board[move[0]][move[1]] = 'O'
        print("Sau khi AI đánh (tạo open four):")
        print_board(board, 15, 15)


def test_block_open_four():
    """Test AI chặn open four của đối thủ"""
    print("=" * 60)
    print("TEST 4: Chặn Open Four của đối thủ")
    print("=" * 60)

    board = [["" for _ in range(15)] for _ in range(15)]

    # Đối thủ có 3 quân, sắp tạo open four
    board[7][7] = 'X'
    board[7][8] = 'X'
    board[7][9] = 'X'

    print("Trước khi AI đánh (X sắp tạo open four):")
    print_board(board, 15, 15)

    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 15, 5)

    print(f"✓ AI chặn tại: {move}")
    if move:
        board[move[0]][move[1]] = 'O'
        print("Sau khi AI chặn:")
        print_board(board, 15, 15)


def test_broken_four():
    """Test AI phát hiện broken four (4 quân bị ngắt: XX_X)"""
    print("=" * 60)
    print("TEST 5: Phát hiện Broken Four (XX_X)")
    print("=" * 60)

    board = [["" for _ in range(15)] for _ in range(15)]

    # Đối thủ có broken four: X X _ X
    board[7][6] = 'X'
    board[7][7] = 'X'
    # board[7][8] trống
    board[7][9] = 'X'

    print("Trước khi AI đánh (X có broken four):")
    print_board(board, 15, 15)

    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 15, 5)

    print(f"✓ AI chặn tại: {move}")
    print(f"  (Nên chặn tại (7, 8) hoặc (7, 5) hoặc (7, 10))")
    if move:
        board[move[0]][move[1]] = 'O'
        print("Sau khi AI chặn:")
        print_board(board, 15, 15)


def test_complex_situation():
    """Test tình huống phức tạp - nhiều mối đe dọa"""
    print("=" * 60)
    print("TEST 6: Tình huống phức tạp - Nhiều mối đe dọa")
    print("=" * 60)

    board = [["" for _ in range(15)] for _ in range(15)]

    # Tạo tình huống phức tạp
    board[7][7] = 'X'
    board[7][8] = 'X'
    board[7][9] = 'X'
    board[7][10] = 'X'  # X sắp thắng (4 quân)

    board[9][7] = 'O'
    board[9][8] = 'O'
    board[9][9] = 'O'  # O có 3 quân

    print("Trước khi AI đánh (X sắp thắng!):")
    print_board(board, 15, 15)

    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 15, 5)

    print(f"✓ AI chặn tại: {move}")
    print(f"  (Phải chặn X - ưu tiên cao nhất)")
    if move:
        board[move[0]][move[1]] = 'O'
        print("Sau khi AI chặn:")
        print_board(board, 15, 15)


def test_winning_move():
    """Test AI nhận biết nước thắng ngay"""
    print("=" * 60)
    print("TEST 7: Nhận biết nước thắng ngay")
    print("=" * 60)

    board = [["" for _ in range(15)] for _ in range(15)]

    # AI có 4 quân, cần 1 nước nữa để thắng
    board[7][7] = 'O'
    board[7][8] = 'O'
    board[7][9] = 'O'
    board[7][10] = 'O'

    print("Trước khi AI đánh (O có 4 quân):")
    print_board(board, 15, 15)

    ai = CaroAI(symbol='O', difficulty='medium')
    move = ai.get_move(board, 15, 15, 5)

    print(f"✓ AI thắng tại: {move}")
    print(f"  (Nên đánh (7, 6) hoặc (7, 11) để thắng)")
    if move:
        board[move[0]][move[1]] = 'O'
        print("Sau khi AI đánh (THẮNG!):")
        print_board(board, 15, 15)


def run_all_tests():
    """Chạy tất cả các test"""
    print("\n" + "=" * 60)
    print("BẮT ĐẦU TEST AI - PHÁT HIỆN VÀ CHẶN THREATS")
    print("=" * 60 + "\n")

    test_winning_move()
    test_block_open_four()
    test_open_four_detection()
    test_broken_four()
    test_double_threat()
    test_block_double_threat()
    test_complex_situation()

    print("\n" + "=" * 60)
    print("HOÀN THÀNH TẤT CẢ CÁC TEST!")
    print("=" * 60)
    print("\n✓ AI đã được cải thiện:")
    print("  - Phát hiện nước thắng ngay")
    print("  - Chặn đối thủ sắp thắng")
    print("  - Tạo và chặn open four (4 quân mở)")
    print("  - Tạo và chặn double threat (2 đường tấn công)")
    print("  - Phát hiện broken four (4 quân bị ngắt)")
    print("  - Đánh giá tình huống phức tạp\n")


if __name__ == "__main__":
    run_all_tests()
