# gui.py
import pygame
from game import NineBoardTicTacToe

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (66, 133, 244)
RED = (219, 68, 55)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)

class GameGUI:
    def __init__(self, width=700, height=800):
        pygame.init()
        self.size = width, height
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('Ultimate Tic-Tac-Toe')
        self.font = pygame.font.SysFont(None, 30)
        self.small_font = pygame.font.SysFont(None, 24)
        self.game = NineBoardTicTacToe()
        self.running = True
        
        # Optimized board size
        self.board_size = 540
        self.cell_size = self.board_size // 9
        self.board_margin = self.board_size // 45
        
        # Calculate board offset to center it
        self.offset_x = (width - self.board_size) // 2
        self.offset_y = (height - self.board_size - 180) // 2  # Leave more space for extra info
        
        self.players = {}
        self.current_player = None
        self.game_info = None

    def set_players(self, player1, player2):
        self.players = {'X': player1, 'O': player2}
        self.current_player = self.players[self.game.current_player]

    def set_game_info(self, current_game, total_games, results):
        self.game_info = {
            'current_game': current_game,
            'total_games': total_games,
            'results': results
        }

    def draw_board(self):
        self.screen.fill(WHITE)
        for board_row in range(3):
            for board_col in range(3):
                board_idx = board_row * 3 + board_col
                board_x = self.offset_x + board_col * 3 * self.cell_size + self.board_margin * board_col
                board_y = self.offset_y + board_row * 3 * self.cell_size + self.board_margin * board_row
                
                # Highlight the next playable board(s)
                if self.game.current_board_index == -1 or self.game.current_board_index == board_idx:
                    highlight_rect = pygame.Rect(board_x, board_y, self.cell_size * 3, self.cell_size * 3)
                    pygame.draw.rect(self.screen, GRAY, highlight_rect)
                
                # Draw small boards
                for cell_row in range(3):
                    for cell_col in range(3):
                        cell_idx = cell_row * 3 + cell_col
                        rect = pygame.Rect(
                            board_x + cell_col * self.cell_size,
                            board_y + cell_row * self.cell_size,
                            self.cell_size,
                            self.cell_size
                        )
                        pygame.draw.rect(self.screen, BLACK, rect, 1)
                        mark = self.game.boards[board_idx][cell_idx]
                        if mark != ' ':
                            color = BLUE if mark == 'X' else RED
                            text = self.font.render(mark, True, color)
                            text_rect = text.get_rect(center=rect.center)
                            self.screen.blit(text, text_rect)
                
                # If a small board has been won, mark it
                winner = self.game.board_winners[board_idx]
                if winner != ' ':
                    color = BLUE if winner == 'X' else RED
                    s = pygame.Surface((self.cell_size * 3, self.cell_size * 3), pygame.SRCALPHA)
                    s.fill((*color, 50))
                    self.screen.blit(s, (board_x, board_y))

        # Display agent names and game info
        info_y = self.offset_y + self.board_size + 30
        
        x_text = self.small_font.render(f"X: {self.players['X'].name}", True, BLUE)
        o_text = self.small_font.render(f"O: {self.players['O'].name}", True, RED)
        self.screen.blit(x_text, (self.offset_x, info_y))
        self.screen.blit(o_text, (self.offset_x + self.board_size - o_text.get_width(), info_y))

        if self.game_info:
            info_y += 35
            game_info_text = self.small_font.render(f"Game {self.game_info['current_game']}/{self.game_info['total_games']}", True, BLACK)
            self.screen.blit(game_info_text, (self.size[0] // 2 - game_info_text.get_width() // 2, info_y))

            info_y += 35
            results = self.game_info['results']
            x_results = self.small_font.render(f"Win: {results['X']}, Lose: {results['O']}, Draw: {results['Draw']}", True, BLUE)
            o_results = self.small_font.render(f"Win: {results['O']}, Lose: {results['X']}, Draw: {results['Draw']}", True, RED)
            self.screen.blit(x_results, (self.offset_x, info_y))
            self.screen.blit(o_results, (self.offset_x + self.board_size - o_results.get_width(), info_y))

        pygame.display.flip()

    def get_cell_from_pos(self, pos):
        x, y = pos
        for board_row in range(3):
            for board_col in range(3):
                board_idx = board_row * 3 + board_col
                board_x_start = self.offset_x + board_col * 3 * self.cell_size + self.board_margin * board_col
                board_y_start = self.offset_y + board_row * 3 * self.cell_size + self.board_margin * board_row
                board_rect = pygame.Rect(
                    board_x_start,
                    board_y_start,
                    self.cell_size * 3,
                    self.cell_size * 3
                )
                if board_rect.collidepoint(x, y):
                    for cell_row in range(3):
                        for cell_col in range(3):
                            cell_idx = cell_row * 3 + cell_col
                            cell_x_start = board_x_start + cell_col * self.cell_size
                            cell_y_start = board_y_start + cell_row * self.cell_size
                            cell_rect = pygame.Rect(
                                cell_x_start,
                                cell_y_start,
                                self.cell_size,
                                self.cell_size
                            )
                            if cell_rect.collidepoint(x, y):
                                return board_idx, cell_idx
        return None, None

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.draw_board()
            if self.game.game_over:
                self.show_winner()
                continue
            # AI player
            if self.current_player.name != 'Human':
                pygame.time.wait(500)  # Wait a bit to simulate thinking time
                move = self.current_player.get_move(self.game)
                if move:
                    self.game.make_move(*move)
                    self.current_player = self.players[self.game.current_player]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_player.name == 'Human':
                        pos = pygame.mouse.get_pos()
                        board_idx, cell_idx = self.get_cell_from_pos(pos)
                        if board_idx is not None and cell_idx is not None:
                            valid_moves = self.game.get_valid_moves()
                            if (board_idx, cell_idx) in valid_moves:
                                self.game.make_move(board_idx, cell_idx)
                                self.current_player = self.players[self.game.current_player]
            clock.tick(30)

    def show_winner(self):
        winner = self.game.winner
        if winner == 'Draw':
            message = 'Draw!'
        else:
            message = f'Player {winner} ({self.players[winner].name}) wins!'
        text = self.font.render(message, True, BLACK)
        rect = text.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        # Wait for a while, but don't exit
        pygame.time.wait(2000)

    def draw_button(self, text, x, y, w, h, color, text_color):
        pygame.draw.rect(self.screen, color, (x, y, w, h))
        text_surf = self.font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(text_surf, text_rect)

    def should_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
        return False

    def show_selection_screen(self):
        self.screen.fill(WHITE)
        title = self.font.render("Choose Game Mode", True, BLACK)
        title_rect = title.get_rect(center=(self.size[0] // 2, 100))
        self.screen.blit(title, title_rect)

        button_width, button_height = 200, 50
        button_x = self.size[0] // 2 - button_width // 2

        human_vs_ai_button = pygame.Rect(button_x, 200, button_width, button_height)
        ai_vs_ai_button = pygame.Rect(button_x, 300, button_width, button_height)

        self.draw_button("Human vs AI", button_x, 200, button_width, button_height, GREEN, WHITE)
        self.draw_button("AI vs AI", button_x, 300, button_width, button_height, BLUE, WHITE)

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if human_vs_ai_button.collidepoint(mouse_pos):
                        return "human_vs_ai"
                    elif ai_vs_ai_button.collidepoint(mouse_pos):
                        return "ai_vs_ai"
            
            pygame.time.wait(10)  # Short sleep to reduce CPU usage

    def show_ai_settings(self):
        self.screen.fill(WHITE)
        title = self.font.render("AI Settings", True, BLACK)
        title_rect = title.get_rect(center=(self.size[0] // 2, 30))
        self.screen.blit(title, title_rect)

        ai_agents = [
            {"name": "Random", "selected": True, "params": []},
            {"name": "Minimax", "selected": False, "params": [
                {"name": "Depth", "value": "5", "note": "Search depth"},
                {"name": "Time Limit", "value": "5", "note": "Max time (s)"}
            ]},
            {"name": "AlphaBeta", "selected": False, "params": [
                {"name": "Depth", "value": "5", "note": "Search depth"},
                {"name": "Time Limit", "value": "5", "note": "Max time (s)"}
            ]},
            {"name": "MCTS", "selected": False, "params": [
                {"name": "Iterations", "value": "500", "note": "Simulations"},
                {"name": "Time Limit", "value": "5", "note": "Max time (s)"}
            ]},
            {"name": "Minimax (Full Search)", "selected": False, "params": []},
            {"name": "AlphaBeta (Full Search)", "selected": False, "params": []}
        ]

        confirm_button = pygame.Rect(250, 650, 200, 40)
        error_message = ""

        active_box = None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if confirm_button.collidepoint(event.pos):
                        selected_agents = [agent["name"] for agent in ai_agents if agent["selected"]]
                        if len(selected_agents) < 2:
                            error_message = "Please select at least two AI agents to start the game."
                        else:
                            return {
                                "selected_agents": selected_agents,
                                **{f"{agent['name']} {param['name']}": int(param['value']) 
                                   for agent in ai_agents if agent["selected"] and agent["params"]
                                   for param in agent["params"]}
                            }
                    for i, agent in enumerate(ai_agents):
                        checkbox_rect = pygame.Rect(50, 70 + i * 85, 20, 20)
                        if checkbox_rect.collidepoint(event.pos):
                            agent["selected"] = not agent["selected"]
                            error_message = ""  # Clear error message when user makes a new selection
                        if agent["selected"] and agent["params"]:
                            for j, param in enumerate(agent["params"]):
                                rect = pygame.Rect(100, 100 + i * 85 + j * 30, 300, 25)
                                if rect.collidepoint(event.pos):
                                    active_box = (i, j)
                if event.type == pygame.KEYDOWN:
                    if active_box is not None:
                        i, j = active_box
                        if event.key == pygame.K_BACKSPACE:
                            ai_agents[i]["params"][j]["value"] = ai_agents[i]["params"][j]["value"][:-1]
                        elif event.key == pygame.K_RETURN:
                            active_box = None
                        elif event.unicode.isdigit():
                            ai_agents[i]["params"][j]["value"] += event.unicode

            self.screen.fill(WHITE)
            self.screen.blit(title, title_rect)

            for i, agent in enumerate(ai_agents):
                checkbox_rect = pygame.Rect(50, 70 + i * 85, 20, 20)
                pygame.draw.rect(self.screen, BLACK, checkbox_rect, 2)
                if agent["selected"]:
                    pygame.draw.rect(self.screen, BLACK, checkbox_rect.inflate(-8, -8))
                agent_text = self.font.render(agent["name"], True, BLACK)
                self.screen.blit(agent_text, (80, 70 + i * 85))

                if agent["selected"] and agent["params"]:
                    for j, param in enumerate(agent["params"]):
                        rect = pygame.Rect(100, 100 + i * 85 + j * 30, 300, 25)
                        pygame.draw.rect(self.screen, BLACK, rect, 2)
                        text_surface = self.small_font.render(f"{param['name']}: {param['value']}", True, BLACK)
                        self.screen.blit(text_surface, (rect.x + 5, rect.y + 5))
                        note_surface = self.small_font.render(param["note"], True, GRAY)
                        self.screen.blit(note_surface, (rect.x + 310, rect.y + 5))

            pygame.draw.rect(self.screen, BLACK, confirm_button)
            confirm_text = self.font.render("Confirm", True, WHITE)
            confirm_text_rect = confirm_text.get_rect(center=confirm_button.center)
            self.screen.blit(confirm_text, confirm_text_rect)

            if error_message:
                error_surface = self.small_font.render(error_message, True, RED)
                error_rect = error_surface.get_rect(center=(self.size[0] // 2, 620))
                self.screen.blit(error_surface, error_rect)

            pygame.display.flip()
            pygame.time.wait(10)  # Short sleep to reduce CPU usage

    def show_ai_selection(self):
        self.screen.fill(WHITE)
        title = self.font.render("Choose AI Agent", True, BLACK)
        title_rect = title.get_rect(center=(self.size[0] // 2, 50))
        self.screen.blit(title, title_rect)

        ai_options = [
            {"name": "Random", "params": []},
            {"name": "Minimax", "params": ["Depth", "Time Limit"]},
            {"name": "AlphaBeta", "params": ["Depth", "Time Limit"]},
            {"name": "MCTS", "params": ["Iterations", "Time Limit"]}
        ]

        button_width, button_height = 200, 50
        button_x = self.size[0] // 2 - button_width // 2

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for i, ai in enumerate(ai_options):
                        button_rect = pygame.Rect(button_x, 150 + i * 70, button_width, button_height)
                        if button_rect.collidepoint(mouse_pos):
                            print(f"Selected {ai['name']} AI")  # Debug info
                            if ai["params"]:
                                params = self.show_ai_params(ai["name"], ai["params"])
                                if params:
                                    return ai["name"], params
                            else:
                                return ai["name"], {}

            self.screen.fill(WHITE)
            self.screen.blit(title, title_rect)
            for i, ai in enumerate(ai_options):
                self.draw_button(ai["name"], button_x, 150 + i * 70, button_width, button_height, BLUE, WHITE)
            
            pygame.display.flip()
            pygame.time.wait(10)  # Short sleep to reduce CPU usage

    def show_ai_params(self, ai_name, params):
        self.screen.fill(WHITE)
        title = self.font.render(f"Set {ai_name} Parameters", True, BLACK)
        title_rect = title.get_rect(center=(self.size[0] // 2, 50))
        self.screen.blit(title, title_rect)

        # Set more appropriate default values and add notes
        default_values_and_notes = {
            "Depth": {"value": "5", "note": "Search depth (higher = stronger but slower)"},
            "Time Limit": {"value": "5", "note": "Max time per move in seconds"},
            "Iterations": {"value": "500", "note": "Number of simulations (higher = stronger but slower)"}
        }

        input_boxes = [{"name": param, 
                        "value": default_values_and_notes.get(param, {}).get("value", "5"),
                        "note": default_values_and_notes.get(param, {}).get("note", "")} 
                       for param in params]

        confirm_button = pygame.Rect(250, 400, 200, 50)

        active_box = None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if confirm_button.collidepoint(event.pos):
                        print(f"Confirmed {ai_name} parameters")  # Debug info
                        return {box["name"]: int(box["value"]) for box in input_boxes}
                    for i, box in enumerate(input_boxes):
                        rect = pygame.Rect(100, 100 + i * 80, 400, 40)
                        if rect.collidepoint(event.pos):
                            active_box = i
                if event.type == pygame.KEYDOWN:
                    if active_box is not None:
                        if event.key == pygame.K_BACKSPACE:
                            input_boxes[active_box]["value"] = input_boxes[active_box]["value"][:-1]
                        elif event.key == pygame.K_RETURN:
                            active_box = None
                        elif event.unicode.isdigit():
                            input_boxes[active_box]["value"] += event.unicode

            self.screen.fill(WHITE)
            self.screen.blit(title, title_rect)
            for i, box in enumerate(input_boxes):
                y = 100 + i * 80
                pygame.draw.rect(self.screen, BLACK, (100, y, 400, 40), 2)
                label = self.small_font.render(box["name"], True, BLACK)
                self.screen.blit(label, (110, y + 10))
                value = self.small_font.render(box["value"], True, BLACK)
                self.screen.blit(value, (350, y + 10))
                note = self.small_font.render(box["note"], True, GRAY)
                self.screen.blit(note, (110, y + 45))
                if i == active_box:
                    pygame.draw.rect(self.screen, BLUE, (100, y, 400, 40), 3)

            pygame.draw.rect(self.screen, GREEN, confirm_button)
            confirm_text = self.font.render("Confirm", True, WHITE)
            confirm_text_rect = confirm_text.get_rect(center=confirm_button.center)
            self.screen.blit(confirm_text, confirm_text_rect)
            
            pygame.display.flip()
            pygame.time.wait(10)  # Short sleep to reduce CPU usage