# ai.py
import random
import math
import time
from functools import lru_cache
from collections import deque

# 使用lru_cache来缓存评估结果
@lru_cache(maxsize=10000)
def cached_evaluate(game_state):
    return game_state.evaluate()

# Minimax (深度限制搜索)
def minimax_depth_limited(game, depth, maximizing_player, alpha=-float('inf'), beta=float('inf')):
    if depth == 0 or game.is_terminal():
        return cached_evaluate(game), None

    best_move = None
    valid_moves = game.get_valid_moves()
    if maximizing_player:
        max_eval = -float('inf')
        for move in valid_moves:
            new_game = game.clone()
            new_game.make_move(*move)
            eval, _ = minimax_depth_limited(new_game, depth - 1, False, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_game = game.clone()
            new_game.make_move(*move)
            eval, _ = minimax_depth_limited(new_game, depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# Monte Carlo Tree Search
class MCTSNode:
    __slots__ = ('game', 'parent', 'move', 'children', 'visits', 'score', 'untried_moves')

    def __init__(self, game, parent=None, move=None):
        self.game = game
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0
        self.untried_moves = game.get_valid_moves()

    def select(self):
        return max(self.children, key=lambda c: c.uct_value())

    def expand(self):
        move = self.untried_moves.pop()
        new_game = self.game.clone()
        new_game.make_move(*move)
        child = MCTSNode(new_game, self, move)
        self.children.append(child)
        return child

    def simulate(self):
        game = self.game.clone()
        while not game.is_terminal():
            move = random.choice(game.get_valid_moves())
            game.make_move(*move)
        return cached_evaluate(game)

    def backpropagate(self, result):
        self.visits += 1
        self.score += result
        if self.parent:
            self.parent.backpropagate(result)

    def uct_value(self, c=1.41):
        if self.visits == 0:
            return float('inf')
        return self.score / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

def mcts(game, iterations=100, time_limit=1):
    root = MCTSNode(game)
    end_time = time.time() + time_limit
    for _ in range(iterations):
        if time.time() > end_time:
            break
        node = root
        while node.untried_moves == [] and node.children != []:
            node = node.select()
        if node.untried_moves != []:
            node = node.expand()
        result = node.simulate()
        node.backpropagate(result)
    return max(root.children, key=lambda c: c.visits).move