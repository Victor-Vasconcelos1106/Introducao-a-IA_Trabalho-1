"""
Aplicação Principal Pygame para Barricade AI.
Coordena telas, loop de eventos, renderização a 60 FPS e execução assíncrona da IA em thread separada.
"""

import sys
import time
import threading
import pygame
from typing import Dict, Any, Optional, List

from src.utils.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_RED,
    COLOR_BLUE,
    PLAYER_RED,
    PLAYER_BLUE,
    PLAYER_NONE,
    MODE_P_VS_BOT,
    MODE_BOT_VS_BOT,
    MODE_P_VS_P,
    DEFAULT_WALLS_COUNT,
    DEFAULT_SEARCH_DEPTH,
    DEFAULT_TIME_LIMIT,
    WALL_HORIZONTAL,
    WALL_VERTICAL,
)
from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.game.rules import get_legal_pawn_moves, get_legal_actions
from src.game.pathfinding import get_shortest_distance
from src.ai.alpha_beta import alpha_beta_search
from src.ai.minimax import minimax_search
from src.ai.transposition_table import TranspositionTable
from src.ai.search_stats import SearchStats
from src.ui.renderer import BoardRenderer, UIRenderer
from src.ui.components import Button
from src.ui.input_handler import InputHandler
from src.ui.menu import MainMenu, SettingsMenu


class PygameApp:
    """Gerenciador central da aplicação e do ciclo de vida da interface gráfica."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Barricade AI — Jogo com Busca Adversarial")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Inicialização de Fontes
        self.fonts = {
            "small": pygame.font.SysFont("Segoe UI, Arial", 14),
            "normal": pygame.font.SysFont("Segoe UI, Arial", 18),
            "bold": pygame.font.SysFont("Segoe UI, Arial", 18, bold=True),
            "title": pygame.font.SysFont("Segoe UI, Arial", 26, bold=True),
            "giant": pygame.font.SysFont("Segoe UI, Arial", 46, bold=True),
        }

        # Configurações Padrão
        self.config: Dict[str, Any] = {
            "bot1_depth": DEFAULT_SEARCH_DEPTH,
            "bot2_depth": DEFAULT_SEARCH_DEPTH,
            "initial_walls": DEFAULT_WALLS_COUNT,
            "time_limit": DEFAULT_TIME_LIMIT,
            "use_alpha_beta": True,
            "use_tt": True,
            "use_ordering": True,
            "bot_delay": 0.4,  # Intervalo em segundos no modo Bot vs Bot
        }

        # Estado da Aplicação: 'MAIN_MENU', 'SETTINGS', 'GAMEPLAY', 'GAME_OVER'
        self.app_state: str = "MAIN_MENU"
        self.game_mode: str = MODE_P_VS_BOT

        # Renderizadores e Controles
        self.board_renderer = BoardRenderer(board_x=50, board_y=95, cell_size=64, gap_size=14)
        self.ui_renderer = UIRenderer(self.board_renderer)
        self.input_handler = InputHandler(self.board_renderer)

        # Menus
        self.main_menu = MainMenu(
            on_start_game=self.start_game,
            on_open_settings=lambda: self.set_app_state("SETTINGS"),
            on_quit=self.quit_app,
            fonts=self.fonts,
        )
        self.settings_menu = SettingsMenu(
            config=self.config,
            on_save=lambda: self.set_app_state("MAIN_MENU"),
            fonts=self.fonts,
        )

        # Estado do Jogo
        self.game_state: Optional[GameState] = None
        self.tt_red = TranspositionTable()
        self.tt_blue = TranspositionTable()

        # Controle de Threads para busca em background
        self.ai_thread: Optional[threading.Thread] = None
        self.ai_result: Optional[Tuple[Any, float, SearchStats]] = None
        self.is_thinking: bool = False
        self.current_ai_stats = SearchStats()
        self.dual_stats: Dict[str, int] = {"red_nodes": 0, "blue_nodes": 0}

        # Controles do Modo Bot vs Bot
        self.bot_vs_bot_paused: bool = False
        self.step_one_move: bool = False
        self.last_bot_move_time: float = 0.0

        # Botões da tela de gameplay
        self._init_gameplay_buttons()

    def _init_gameplay_buttons(self) -> None:
        """Inicializa botões de ação e controle da interface durante a partida."""
        bx = 50
        by = 645
        bw, bh = 110, 38
        gap = 10

        self.btn_move_mode = Button(
            pygame.Rect(bx, by, bw, bh),
            "Peão (M)",
            self.fonts["small"],
            callback=lambda: self.input_handler.set_mode("MOVE"),
        )
        self.btn_wall_h = Button(
            pygame.Rect(bx + (bw + gap), by, bw, bh),
            "Barricada H",
            self.fonts["small"],
            callback=lambda: self.input_handler.set_mode("WALL_H"),
        )
        self.btn_wall_v = Button(
            pygame.Rect(bx + 2 * (bw + gap), by, bw, bh),
            "Barricada V",
            self.fonts["small"],
            callback=lambda: self.input_handler.set_mode("WALL_V"),
        )
        self.btn_cancel = Button(
            pygame.Rect(bx + 3 * (bw + gap), by, bw, bh),
            "Cancelar",
            self.fonts["small"],
            callback=lambda: self.input_handler.set_mode("MOVE"),
        )

        # Botão Menu Principal
        self.btn_menu = Button(
            pygame.Rect(910, 680, 140, 42),
            "Menu Principal",
            self.fonts["small"],
            bg_color=(50, 40, 45),
            hover_color=(70, 50, 55),
            callback=lambda: self.set_app_state("MAIN_MENU"),
        )

        # Controles específicos de Bot vs Bot
        self.btn_pause_bot = Button(
            pygame.Rect(620, 580, 130, 40),
            "Pausar",
            self.fonts["small"],
            callback=self.toggle_bot_pause,
        )
        self.btn_step_bot = Button(
            pygame.Rect(760, 580, 130, 40),
            "Avançar 1 Jogada",
            self.fonts["small"],
            callback=self.trigger_step_move,
        )

        # Botões de Fim de Jogo
        self.btn_play_again = Button(
            pygame.Rect(430, 440, 160, 46),
            "Jogar Novamente",
            self.fonts["bold"],
            bg_color=(35, 120, 60),
            hover_color=(45, 150, 75),
            callback=lambda: self.start_game(self.game_mode),
        )
        self.btn_gameover_menu = Button(
            pygame.Rect(610, 440, 160, 46),
            "Menu Principal",
            self.fonts["normal"],
            callback=lambda: self.set_app_state("MAIN_MENU"),
        )

    def set_app_state(self, state: str) -> None:
        self.app_state = state

    def quit_app(self) -> None:
        self.is_running = False

    def toggle_bot_pause(self) -> None:
        self.bot_vs_bot_paused = not self.bot_vs_bot_paused
        self.btn_pause_bot.text = "Retomar" if self.bot_vs_bot_paused else "Pausar"

    def trigger_step_move(self) -> None:
        self.step_one_move = True

    def start_game(self, mode: str) -> None:
        """Inicia uma nova partida com as configurações atuais."""
        self.game_mode = mode
        walls = self.config["initial_walls"]
        self.game_state = GameState(red_walls=walls, blue_walls=walls)
        self.tt_red.clear()
        self.tt_blue.clear()
        self.current_ai_stats.reset()
        self.dual_stats = {"red_nodes": 0, "blue_nodes": 0}
        self.is_thinking = False
        self.ai_result = None
        self.bot_vs_bot_paused = False
        self.step_one_move = False
        self.btn_pause_bot.text = "Pausar"
        self.input_handler.set_mode("MOVE")
        self.input_handler.status_message = None
        self.app_state = "GAMEPLAY"

    def is_current_turn_bot(self) -> bool:
        """Verifica se o turno atual deve ser jogado pela IA."""
        if self.game_state is None:
            return False
        if self.game_mode == MODE_BOT_VS_BOT:
            return True
        if self.game_mode == MODE_P_VS_BOT and self.game_state.turn == PLAYER_BLUE:
            return True
        return False

    def _async_ai_search(self, state: GameState, is_red: bool) -> None:
        """Rotina executada em thread secundária para calcular a jogada da IA sem congelar a UI."""
        depth = self.config["bot1_depth"] if is_red else self.config["bot2_depth"]
        use_ab = self.config["use_alpha_beta"]
        use_tt = self.config["use_tt"]
        use_ord = self.config["use_ordering"]
        limit = self.config["time_limit"]
        tt = self.tt_red if is_red else self.tt_blue
        stats = SearchStats()

        if not use_ab:
            action, score, stats = minimax_search(
                state=state,
                depth=depth,
                max_player=state.turn,
                stats=stats,
            )
        else:
            action, score, stats = alpha_beta_search(
                state=state,
                depth=depth,
                max_player=state.turn,
                use_ordering=use_ord,
                use_tt=use_tt,
                tt=tt if use_tt else None,
                iterative_deepening=True,
                time_limit=limit,
                stats=stats,
            )

        self.ai_result = (action, score, stats)

    def update(self) -> None:
        """Atualização lógica por frame."""
        if self.app_state == "GAMEPLAY" and self.game_state is not None:
            # 1. Checa vitória
            if self.game_state.is_terminal():
                self.app_state = "GAME_OVER"
                return

            # 2. Coleta de resultado da IA que estava calculando em background
            if self.ai_result is not None:
                action, score, stats = self.ai_result
                self.ai_result = None
                self.is_thinking = False
                self.current_ai_stats = stats

                if self.game_state.turn == PLAYER_RED:
                    self.dual_stats["red_nodes"] += stats.nodes_visited
                else:
                    self.dual_stats["blue_nodes"] += stats.nodes_visited

                if action is not None:
                    self.game_state = self.game_state.apply_action(action)
                    self.last_bot_move_time = time.time()
                    if self.game_mode == MODE_BOT_VS_BOT:
                        self.step_one_move = False

            # 3. Disparo de novo cálculo de Bot
            elif not self.is_thinking and self.is_current_turn_bot():
                # No modo Bot vs Bot, respeita pausa e velocidade configurada
                if self.game_mode == MODE_BOT_VS_BOT:
                    if self.bot_vs_bot_paused and not self.step_one_move:
                        return
                    if (time.time() - self.last_bot_move_time) < self.config["bot_delay"]:
                        return

                self.is_thinking = True
                is_red = (self.game_state.turn == PLAYER_RED)
                clone_state = self.game_state.clone()
                self.ai_thread = threading.Thread(
                    target=self._async_ai_search,
                    args=(clone_state, is_red),
                    daemon=True,
                )
                self.ai_thread.start()

    def handle_events(self) -> None:
        """Processamento de eventos de entrada do Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_app()
                return

            if self.app_state == "MAIN_MENU":
                self.main_menu.handle_event(event)

            elif self.app_state == "SETTINGS":
                self.settings_menu.handle_event(event)

            elif self.app_state == "GAMEPLAY":
                self.btn_menu.handle_event(event)
                self.btn_move_mode.handle_event(event)
                self.btn_wall_h.handle_event(event)
                self.btn_wall_v.handle_event(event)
                self.btn_cancel.handle_event(event)

                if self.game_mode == MODE_BOT_VS_BOT:
                    self.btn_pause_bot.handle_event(event)
                    self.btn_step_bot.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_mode == MODE_BOT_VS_BOT:
                        self.toggle_bot_pause()
                    else:
                        self.input_handler.handle_key_down(event.key)

                # Se for a vez do humano (e o bot não estiver pensando)
                if not self.is_current_turn_bot() and not self.is_thinking and self.game_state is not None:
                    if event.type == pygame.MOUSEMOTION:
                        self.input_handler.handle_mouse_motion(
                            event.pos,
                            self.game_state,
                            self.game_state.turn,
                        )

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        valid_pawn_moves = get_legal_pawn_moves(self.game_state, self.game_state.turn)
                        action = self.input_handler.handle_mouse_click(
                            event.pos,
                            self.game_state,
                            self.game_state.turn,
                            valid_pawn_moves,
                        )
                        if action is not None:
                            self.game_state = self.game_state.apply_action(action)
                            self.input_handler.status_message = None

            elif self.app_state == "GAME_OVER":
                self.btn_play_again.handle_event(event)
                self.btn_gameover_menu.handle_event(event)

    def draw(self) -> None:
        """Renderização principal na tela."""
        self.screen.fill(COLOR_BG)

        if self.app_state == "MAIN_MENU":
            self.main_menu.draw(self.screen)

        elif self.app_state == "SETTINGS":
            self.settings_menu.draw(self.screen)

        elif self.app_state in ("GAMEPLAY", "GAME_OVER"):
            if self.game_state is not None:
                # 1. Barra superior
                self.ui_renderer.draw_top_bar(
                    self.screen,
                    self.game_state,
                    self.game_mode,
                    self.is_thinking,
                    self.fonts,
                )

                # 2. Movimentos legais para o jogador do turno (se for humano)
                valid_pawn_moves = []
                if not self.is_current_turn_bot() and self.input_handler.input_mode == "MOVE":
                    valid_pawn_moves = get_legal_pawn_moves(self.game_state, self.game_state.turn)

                # 3. Desenho do Tabuleiro
                self.board_renderer.draw_board(
                    self.screen,
                    self.game_state,
                    self.input_handler.hover_cell,
                    valid_pawn_moves,
                    self.input_handler.wall_preview,
                    self.fonts,
                )

                # 4. Botões de Ação na barra inferior
                self.btn_move_mode.draw(self.screen)
                self.btn_wall_h.draw(self.screen)
                self.btn_wall_v.draw(self.screen)
                self.btn_cancel.draw(self.screen)
                self.btn_menu.draw(self.screen)

                # Mensagem de status ou erro de jogada
                if self.input_handler.status_message:
                    msg_surf = self.fonts["small"].render(self.input_handler.status_message, True, (240, 100, 100))
                    self.screen.blit(msg_surf, (50, 695))

                # 5. Painel Lateral de Informações da IA
                dist_r = get_shortest_distance(
                    self.game_state.red_pos,
                    0,
                    self.game_state.h_walls,
                    self.game_state.v_walls,
                )
                dist_b = get_shortest_distance(
                    self.game_state.blue_pos,
                    6,
                    self.game_state.h_walls,
                    self.game_state.v_walls,
                )

                algo_name = "Minimax + Alpha-Beta" if self.config["use_alpha_beta"] else "Minimax Clássico"
                active_depth = self.config["bot1_depth"] if self.game_state.turn == PLAYER_RED else self.config["bot2_depth"]

                panel_rect = pygame.Rect(610, 95, 440, 460)
                dual = self.dual_stats if self.game_mode == MODE_BOT_VS_BOT else None
                self.ui_renderer.draw_ai_panel(
                    self.screen,
                    panel_rect,
                    algo_name,
                    active_depth,
                    self.current_ai_stats,
                    dist_r,
                    dist_b,
                    dual,
                    self.fonts,
                )

                # Botões do modo Bot vs Bot
                if self.game_mode == MODE_BOT_VS_BOT:
                    self.btn_pause_bot.draw(self.screen)
                    self.btn_step_bot.draw(self.screen)

            # Tela de Vitória / Derrota
            if self.app_state == "GAME_OVER" and self.game_state is not None:
                self.ui_renderer.draw_game_over_overlay(self.screen, self.game_state.winner, self.fonts)
                self.btn_play_again.draw(self.screen)
                self.btn_gameover_menu.draw(self.screen)

        pygame.display.flip()

    def run(self) -> None:
        """Loop principal de execução do jogo."""
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
