"""
Tratamento de entrada do usuário para o jogo Barricade AI.
Mapeia eventos do Pygame para intenções e ações de jogo (movimento e posicionamento).
"""

import pygame
from typing import Optional, Tuple, List
from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.game.rules import is_valid_wall_placement
from src.ui.renderer import BoardRenderer
from src.utils.constants import WALL_HORIZONTAL, WALL_VERTICAL


class InputHandler:
    """Gerencia cliques, movimentos de mouse e atalhos de teclado durante o jogo."""

    def __init__(self, board_renderer: BoardRenderer):
        self.board = board_renderer
        # Modo de ação selecionado: 'MOVE', 'WALL_H', 'WALL_V'
        self.input_mode: str = "MOVE"
        self.hover_cell: Optional[Tuple[int, int]] = None
        self.wall_preview: Optional[Tuple[WallAction, bool]] = None
        self.status_message: Optional[str] = None

    def set_mode(self, mode: str) -> None:
        """Altera o modo de ação ('MOVE', 'WALL_H', 'WALL_V')."""
        self.input_mode = mode
        self.wall_preview = None

    def handle_mouse_motion(
        self,
        mouse_pos: Tuple[int, int],
        state: GameState,
        player: int,
    ) -> None:
        """Atualiza a casa sob hover e o preview da barricada."""
        px, py = mouse_pos

        if self.input_mode == "MOVE":
            self.hover_cell = self.board.get_cell_at_pixel(px, py)
            self.wall_preview = None
        else:
            self.hover_cell = None
            wall_info = self.board.get_wall_at_pixel(px, py)
            if wall_info is not None:
                detected_type, wr, wc = wall_info
                # Se o usuário escolheu explicitamente H ou V, mantém a orientação escolhida
                w_type = WALL_HORIZONTAL if self.input_mode == "WALL_H" else (
                    WALL_VERTICAL if self.input_mode == "WALL_V" else detected_type
                )
                action = WallAction(w_type, wr, wc)
                is_valid = is_valid_wall_placement(state, action, player)
                self.wall_preview = (action, is_valid)
            else:
                self.wall_preview = None

    def handle_mouse_click(
        self,
        mouse_pos: Tuple[int, int],
        state: GameState,
        player: int,
        valid_moves: List[MoveAction],
    ) -> Optional[MoveAction | WallAction]:
        """Processa clique do mouse e retorna uma ação válida se selecionada."""
        px, py = mouse_pos

        # Se estiver no modo de movimentação de peão
        if self.input_mode == "MOVE":
            cell = self.board.get_cell_at_pixel(px, py)
            if cell is not None:
                candidate_move = MoveAction(cell)
                if candidate_move in valid_moves:
                    return candidate_move
                else:
                    self.status_message = "Movimento inválido para esta casa!"
            else:
                # Se clicou diretamente em uma fenda, seleciona automaticamente o modo barricada
                wall_info = self.board.get_wall_at_pixel(px, py)
                if wall_info is not None:
                    w_type, wr, wc = wall_info
                    action = WallAction(w_type, wr, wc)
                    if is_valid_wall_placement(state, action, player):
                        return action
                    else:
                        self.status_message = "Posicionamento inválido de barricada!"

        # Se estiver em modo de colocação de barricada
        elif self.input_mode in ("WALL_H", "WALL_V", "WALL"):
            if self.wall_preview is not None:
                action, is_valid = self.wall_preview
                if is_valid:
                    # Volta para modo MOVE após colocar barricada
                    self.input_mode = "MOVE"
                    self.wall_preview = None
                    return action
                else:
                    self.status_message = "Barricada inválida (colisão ou bloqueio total)!"

        return None

    def handle_key_down(self, key: int) -> None:
        """Trata atalhos de teclado úteis."""
        if key == pygame.K_ESCAPE or key == pygame.K_m:
            self.input_mode = "MOVE"
            self.wall_preview = None
            self.status_message = None
        elif key == pygame.K_h:
            self.input_mode = "WALL_H"
            self.status_message = "Modo: Barricada Horizontal. Clique no tabuleiro."
        elif key == pygame.K_v:
            self.input_mode = "WALL_V"
            self.status_message = "Modo: Barricada Vertical. Clique no tabuleiro."
