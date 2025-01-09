# main.py
import time
import psutil
import matplotlib.pyplot as plt
import numpy as np
from gui import GameGUI
from player import RandomPlayer, MinimaxPlayer, AlphaBetaPlayer, MCTSPlayer, HumanPlayer
from game import NineBoardTicTacToe
import itertools
import pygame
import matplotlib.pyplot as plt
from matplotlib.table import Table
import sys
import threading
import copy

# 添加全局标志
program_should_exit = False

def initialize_pygame():
    pygame.init()
    return GameGUI()

def ai_vs_ai(player1, player2, num_games=10):
    global program_should_exit
    results = {'X': 0, 'O': 0, 'Draw': 0}
    player_stats = {
        player1.name: {'total_time': 0, 'total_moves': 0, 'total_cpu': 0},
        player2.name: {'total_time': 0, 'total_moves': 0, 'total_cpu': 0}
    }
    gui = GameGUI()
    for game_num in range(num_games):
        if program_should_exit:
            return None, None
        game = NineBoardTicTacToe()
        gui.game = game
        gui.set_players(player1, player2)
        gui.set_game_info(game_num + 1, num_games, results)
        current_player = player1
        while not game.game_over:
            if gui.should_quit():
                program_should_exit = True
                pygame.quit()
                return None, None

            start_time = time.time()
            start_cpu = psutil.cpu_percent()
            move = current_player.get_move(game)
            end_time = time.time()
            end_cpu = psutil.cpu_percent()
            
            player_stats[current_player.name]['total_time'] += end_time - start_time
            player_stats[current_player.name]['total_moves'] += 1
            player_stats[current_player.name]['total_cpu'] += end_cpu - start_cpu
            
            if move:
                game.make_move(*move)
                gui.draw_board()
                pygame.display.flip()
                pygame.time.wait(500)  # 等待500毫秒，便于观察
            current_player = player2 if current_player == player1 else player1

        if game.winner == 'Draw':
            results['Draw'] += 1
        else:
            results[game.winner] += 1
        gui.show_winner()
        pygame.time.wait(1000)  # 等待1秒后开始下一局

    pygame.quit()
    return results, player_stats

def plot_stats(all_stats):
    agents = list(all_stats.keys())
    avg_times = [stats['avg_time'] for stats in all_stats.values()]
    avg_cpus = [stats['avg_cpu'] for stats in all_stats.values()]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

    ax1.bar(agents, avg_times)
    ax1.set_ylabel('Average Time per Move (s)')
    ax1.set_title('Average Time per Move for Each Agent')

    ax2.bar(agents, avg_cpus)
    ax2.set_ylabel('Average CPU Usage per Move (%)')
    ax2.set_title('Average CPU Usage per Move for Each Agent')

    plt.tight_layout()
    plt.savefig('agent_stats.png')
    plt.close()

def plot_results(all_stats):
    agents = list(all_stats.keys())
    wins = [stats['wins'] for stats in all_stats.values()]
    losses = [stats['losses'] for stats in all_stats.values()]
    draws = [stats['draws'] for stats in all_stats.values()]

    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(agents))
    width = 0.25

    ax.bar(x - width, wins, width, label='Wins')
    ax.bar(x, losses, width, label='Losses')
    ax.bar(x + width, draws, width, label='Draws')

    ax.set_ylabel('Number of Games')
    ax.set_title('Game Results for Each Agent')
    ax.set_xticks(x)
    ax.set_xticklabels(agents)
    ax.legend()

    plt.tight_layout()
    plt.savefig('game_results.png')
    plt.close()

def plot_detailed_stats(all_stats):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    ax.axis('tight')

    data = []
    columns = ['Agent', 'Win Rate', 'Loss Rate', 'Draw Rate', 'Avg Time (s)', 'Avg CPU (%)']

    for agent, stats in all_stats.items():
        data.append([
            agent,
            f"{stats['win_rate']:.2%}",
            f"{stats['loss_rate']:.2%}",
            f"{stats['draw_rate']:.2%}",
            f"{stats['avg_time']:.4f}",
            f"{stats['avg_cpu']:.2f}"
        ])

    table = ax.table(cellText=data, colLabels=columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    plt.title("Detailed Statistics for Each Agent")
    plt.tight_layout()
    plt.savefig('detailed_stats.png', dpi=300, bbox_inches='tight')
    plt.close()

def human_vs_ai(gui):
    ai_choice = gui.show_ai_selection()
    if ai_choice is None:
        print("AI selection cancelled")
        return

    ai_name, ai_params = ai_choice
    print(f"Selected AI: {ai_name}, Parameters: {ai_params}")  # Debug info
    human_player = HumanPlayer(name='Human')

    if ai_name == "Random":
        ai_player = RandomPlayer(name='RandomAI')
    elif ai_name == "Minimax":
        depth = ai_params.get("Depth", 5)
        time_limit = ai_params.get("Time Limit", 5)
        ai_player = MinimaxPlayer(depth=depth, time_limit=time_limit, name=f'MinimaxAI_{depth}')
    elif ai_name == "AlphaBeta":
        depth = ai_params.get("Depth", 5)
        time_limit = ai_params.get("Time Limit", 5)
        ai_player = AlphaBetaPlayer(depth=depth, time_limit=time_limit, name=f'AlphaBetaAI_{depth}')
    elif ai_name == "MCTS":
        iterations = ai_params.get("Iterations", 1000)
        time_limit = ai_params.get("Time Limit", 5)
        ai_player = MCTSPlayer(iterations=iterations, time_limit=time_limit, name=f'MCTSAI_{iterations}')
    else:
        print(f"Invalid AI choice: {ai_name}")
        return

    print(f"Starting Human vs {ai_player.name}")  # Debug info
    gui.set_players(human_player, ai_player)
    gui.run()

def main():
    global program_should_exit
    pygame.init()
    gui = initialize_pygame()
    
    try:
        print("Showing selection screen")
        choice = gui.show_selection_screen()
        print(f"User choice: {choice}")

        if choice == "ai_vs_ai":
            print("Showing AI settings screen")
            ai_settings = gui.show_ai_settings()
            print(f"Returned AI settings: {ai_settings}")

            if ai_settings:
                print("AI settings confirmed, starting AI vs AI")
                selected_agents = ai_settings["selected_agents"]
                print(f"Selected agents: {selected_agents}")  # 新增日志
                players = []
                for agent in selected_agents:
                    print(f"Creating agent: {agent}")  # 新增日志
                    if agent == "Random":
                        players.append(RandomPlayer(name='RandomAgent'))
                        print("Created RandomAgent")
                    elif agent == "Minimax":
                        depth = ai_settings["Minimax Depth"]
                        time_limit = ai_settings["Minimax Time Limit"]
                        players.append(MinimaxPlayer(depth=depth, 
                                                             time_limit=time_limit, 
                                                             name=f'MinimaxAgent_D{depth}_T{time_limit}'))
                        print(f"Created MinimaxAgent with depth {depth} and time limit {time_limit}")
                    elif agent == "Minimax (Full Search)":
                        players.append(MinimaxPlayer(depth=float('inf'), 
                                                             time_limit=float('inf'), 
                                                             name='MinimaxAgent_FullSearch'))
                        print("Created MinimaxAgent with full search (depth and time limit set to infinity)")
                    elif agent == "AlphaBeta":
                        depth = ai_settings["AlphaBeta Depth"]
                        time_limit = ai_settings["AlphaBeta Time Limit"]
                        players.append(AlphaBetaPlayer(depth=depth, 
                                                               time_limit=time_limit, 
                                                               name=f'AlphaBetaAgent_D{depth}_T{time_limit}'))
                        print(f"Created AlphaBetaAgent with depth {depth} and time limit {time_limit}")
                    elif agent == "AlphaBeta (Full Search)":
                        players.append(AlphaBetaPlayer(depth=float('inf'), 
                                                               time_limit=float('inf'), 
                                                               name='AlphaBetaAgent_FullSearch'))
                        print("Created AlphaBetaAgent with full search (depth and time limit set to infinity)")
                    elif agent == "MCTS":
                        iterations = ai_settings["MCTS Iterations"]
                        time_limit = ai_settings["MCTS Time Limit"]
                        players.append(MCTSPlayer(iterations=iterations, 
                                                  time_limit=time_limit, 
                                                  name=f'MCTSAgent_I{iterations}_T{time_limit}'))
                        print(f"Created MCTSAgent with {iterations} iterations and time limit {time_limit}")
                    print(f"Player added: {players[-1].name}")  # 新增日志

                print(f"All players created: {[player.name for player in players]}")  # 新增日志

                all_stats = {player.name: {'total_time': 0, 'total_moves': 0, 'total_cpu': 0, 'wins': 0, 'losses': 0, 'draws': 0} for player in players}
                total_games = 0

                for player1, player2 in itertools.combinations(players, 2):
                    if program_should_exit:
                        break
                    print(f"\nStarting match: {player1.name} vs {player2.name}")
                    results, player_stats = ai_vs_ai(player1, player2)
                    if results is None:
                        print("User closed the game window")
                        break
                    
                    total_games += sum(results.values())
                    
                    # 更新统计信息
                    for player_name, stats in player_stats.items():
                        all_stats[player_name]['total_time'] += stats['total_time']
                        all_stats[player_name]['total_moves'] += stats['total_moves']
                        all_stats[player_name]['total_cpu'] += stats['total_cpu']

                    all_stats[player1.name]['wins'] += results['X']
                    all_stats[player1.name]['losses'] += results['O']
                    all_stats[player1.name]['draws'] += results['Draw']
                    all_stats[player2.name]['wins'] += results['O']
                    all_stats[player2.name]['losses'] += results['X']
                    all_stats[player2.name]['draws'] += results['Draw']

                    # 打印本次对战的胜率
                    print(f"\nMatch results: {player1.name} vs {player2.name}")
                    print(f"{player1.name}: Wins: {results['X']}, Losses: {results['O']}, Draws: {results['Draw']}")
                    print(f"{player2.name}: Wins: {results['O']}, Losses: {results['X']}, Draws: {results['Draw']}")
                    
                    total_games_match = sum(results.values())
                    if total_games_match > 0:
                        print(f"{player1.name} Win Rate: {results['X'] / total_games_match:.2%}")
                        print(f"{player2.name} Win Rate: {results['O'] / total_games_match:.2%}")
                        print(f"Draw Rate: {results['Draw'] / total_games_match:.2%}")

                if not program_should_exit:
                    # 计算平均值和胜率
                    for player_name, stats in all_stats.items():
                        if stats['total_moves'] > 0:
                            stats['avg_time'] = stats['total_time'] / stats['total_moves']
                            stats['avg_cpu'] = stats['total_cpu'] / stats['total_moves']
                        else:
                            stats['avg_time'] = 0
                            stats['avg_cpu'] = 0
                        
                        total_games_player = stats['wins'] + stats['losses'] + stats['draws']
                        if total_games_player > 0:
                            stats['win_rate'] = stats['wins'] / total_games_player
                            stats['loss_rate'] = stats['losses'] / total_games_player
                            stats['draw_rate'] = stats['draws'] / total_games_player
                        else:
                            stats['win_rate'] = stats['loss_rate'] = stats['draw_rate'] = 0

                    # 打印详细统计信息
                    print("\nDetailed Statistics:")
                    print(f"Total games played: {total_games}")
                    for player_name, stats in all_stats.items():
                        print(f"\n{player_name}:")
                        print(f"  Wins: {stats['wins']} ({stats['win_rate']:.2%})")
                        print(f"  Losses: {stats['losses']} ({stats['loss_rate']:.2%})")
                        print(f"  Draws: {stats['draws']} ({stats['draw_rate']:.2%})")
                        print(f"  Average move time: {stats['avg_time']:.4f} seconds")
                        print(f"  Average CPU usage: {stats['avg_cpu']:.2f}%")

                    # 绘制统计图表
                    plot_stats(all_stats)
                    plot_results(all_stats)
                    plot_detailed_stats(all_stats)
                    print("AI vs AI completed, statistics charts generated")
            else:
                print("AI settings not confirmed or returned None. Exiting.")
        elif choice == "human_vs_ai":
            human_vs_ai(gui)
        elif choice is None:
            print("Game closed")
        else:
            print("Invalid choice")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()