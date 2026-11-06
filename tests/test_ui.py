"""
Testes unitários e de integração para a interface gráfica e componentes Pygame (modo headless).
"""

import os
import pytest

# Configura o driver de vídeo do SDL para 'dummy' para execução em ambiente CI/headless
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.ui.pygame_app import PygameApp
from src.ui.renderer import BoardRenderer
from src.ui.input_handler import InputHandler
from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.utils.constants import WALL_HORIZONTAL, WALL_VERTICAL, PLAYER_RED, MODE_BOT_VS_BOT


def test_board_renderer_coordinates():
    renderer = BoardRenderer(board_x=50, board_y=95, cell_size=64, gap_size=14)
    # Canto superior esquerdo (0, 0)
    rect_00 = renderer.get_cell_rect(0, 0)
    assert rect_00.x == 50
    assert rect_00.y == 95
    assert rect_00.width == 64
    assert rect_00.height == 64

    # Ponto dentro da casa (0, 0)
    cell = renderer.get_cell_at_pixel(60, 100)
    assert cell == (0, 0)

    # Barricada H em (0, 0)
    h_rect = renderer.get_wall_rect(WALL_HORIZONTAL, 0, 0)
    assert h_rect.x == 50
    assert h_rect.y == 95 + 64
    assert h_rect.height == 14
    assert h_rect.width == 2 * 64 + 14


def test_pygame_app_lifecycle():
    app = PygameApp()
    assert app.app_state == "MAIN_MENU"

    # Iniciar jogo contra Bot
    app.start_game("Player_vs_Bot")
    assert app.app_state == "GAMEPLAY"
    assert app.game_state is not None
    assert app.game_state.turn == PLAYER_RED

    # Um ciclo de update e draw no modo headless não deve gerar exceções
    app.update()
    app.draw()

    # Iniciar modo Bot vs Bot
    app.start_game(MODE_BOT_VS_BOT)
    assert app.game_mode == MODE_BOT_VS_BOT
    assert app.is_current_turn_bot() is True

    app.quit_app()
    assert app.is_running is False
