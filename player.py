# player.py
import random
import time
from ai import minimax_depth_limited, mcts
from functools import lru_cache

class RandomPlayer:
    def __init__(self, name='Random'):
        self.name = name

    def get_move(self, game):
        moves = game.get_valid_moves()
        return random.choice(moves) if moves else None

class MinimaxPlayer:
    def __init__(self, depth=3, time_limit=5, name='Minimax'):
        self.max_depth = depth
        self.time_limit = time_limit
        self.name = name

    def get_move(self, game):
        start_time = time.time()
        best_move = None
        if self.max_depth == float('inf'):
            depth = 1
            while time.time() - start_time < self.time_limit:
                _, move = minimax_depth_limited(game, depth, game.current_player == 'X')
                if move:
                    best_move = move
                depth += 1
        else:
            for depth in range(1, self.max_depth + 1):
                _, move = minimax_depth_limited(game, depth, game.current_player == 'X')
                if move:
                    best_move = move
                if time.time() - start_time > self.time_limit:
                    break
        return best_move

# AlphaBetaPlayer 现在是 MinimaxPlayer 的别名
AlphaBetaPlayer = MinimaxPlayer

class MCTSPlayer:
    def __init__(self, iterations=1000, time_limit=5, name='MCTS'):
        self.iterations = iterations
        self.time_limit = time_limit
        self.name = name

    def get_move(self, game):
        return mcts(game, self.iterations, self.time_limit)

class HumanPlayer:
    def __init__(self, name='Human'):
        self.name = name

    def get_move(self, game):
        return None  # 人类玩家的移动在GUI中处理