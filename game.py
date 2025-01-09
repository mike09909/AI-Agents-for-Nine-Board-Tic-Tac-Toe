# game.py
import copy

class NineBoardTicTacToe:
    def __init__(self):
        # 初始化九个小棋盘
        self.boards = [[' ' for _ in range(9)] for _ in range(9)]
        # 当前可用的大棋盘索引，如果为 -1，则玩家可在任意棋盘上落子
        self.current_board_index = -1
        # 记录游戏是否结束
        self.game_over = False
        # 当前玩家，'X' 先手，'O' 后手
        self.current_player = 'X'
        # 记录每个小棋盘的赢家
        self.board_winners = [' ' for _ in range(9)]
        # 总的赢家
        self.winner = None

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def is_full(self, board):
        return ' ' not in board

    def check_winner(self, board):
        # 检查行、列、对角线
        lines = [
            [board[0], board[1], board[2]],
            [board[3], board[4], board[5]],
            [board[6], board[7], board[8]],
            [board[0], board[3], board[6]],
            [board[1], board[4], board[7]],
            [board[2], board[5], board[8]],
            [board[0], board[4], board[8]],
            [board[2], board[4], board[6]],
        ]
        for line in lines:
            if line[0] == line[1] == line[2] and line[0] != ' ':
                return line[0]
        return None

    def make_move(self, board_index, cell_index):
        if self.board_winners[board_index] != ' ':
            return False, "该棋盘已有人获胜。"
        if self.boards[board_index][cell_index] != ' ':
            return False, "该位置已被占用。"
        self.boards[board_index][cell_index] = self.current_player
        winner = self.check_winner(self.boards[board_index])
        if winner:
            self.board_winners[board_index] = winner

        # 将 cell_index 转换为 (row, col)，然后计算下一个 board_index
        cell_row = cell_index // 3
        cell_col = cell_index % 3
        next_board_index = cell_row * 3 + cell_col
        self.current_board_index = next_board_index

        # 如果下一个棋盘已满或已有人赢得，则玩家可选择任意棋盘
        if self.is_full(self.boards[self.current_board_index]) or self.board_winners[self.current_board_index] != ' ':
            self.current_board_index = -1

        # 检查游戏是否结束
        self.check_game_over()
        if not self.game_over:
            self.switch_player()
        return True, ""

    def get_valid_moves(self):
        moves = []
        if self.current_board_index == -1:
            boards_to_check = [i for i in range(9) if self.board_winners[i] == ' ' and not self.is_full(self.boards[i])]
        else:
            if self.board_winners[self.current_board_index] == ' ' and not self.is_full(self.boards[self.current_board_index]):
                boards_to_check = [self.current_board_index]
            else:
                boards_to_check = [i for i in range(9) if self.board_winners[i] == ' ' and not self.is_full(self.boards[i])]
                self.current_board_index = -1
        for board_idx in boards_to_check:
            for cell_idx in range(9):
                if self.boards[board_idx][cell_idx] == ' ':
                    moves.append((board_idx, cell_idx))
        return moves

    def is_terminal(self):
        return self.game_over

    def check_game_over(self):
        # 检查大棋盘的赢家
        winner = self.check_winner(self.board_winners)
        if winner:
            self.game_over = True
            self.winner = winner
        elif all(winner != ' ' or self.is_full(self.boards[i]) for i, winner in enumerate(self.board_winners)):
            self.game_over = True
            self.winner = 'Draw'

    def evaluate(self):
        # 简单评估函数，可以根据需要改进
        score = 0
        for winner in self.board_winners:
            if winner == 'X':
                score += 1
            elif winner == 'O':
                score -= 1
        return score

    def clone(self):
        return copy.deepcopy(self)