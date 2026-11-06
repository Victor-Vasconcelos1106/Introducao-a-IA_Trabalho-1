"""
Renderizador visual para o jogo Barricade AI.
Desenha o tabuleiro 7x7, peões, barricadas, destaques de jogadas válidas,
painel de telemetria da IA e tela de resultado final com Pygame.
"""

import pygame
import math
from typing import Optional, Set, Tuple, List, Dict, Any
from src.utils.constants import (
    BOARD_SIZE,
    PLAYER_RED,
    PLAYER_BLUE,
    PLAYER_NAMES,
    WALL_HORIZONTAL,
    WALL_VERTICAL,
    COLOR_BG,
    COLOR_BOARD_BG,
    COLOR_CELL,
    COLOR_CELL_HOVER,
    COLOR_VALID_MOVE,
    COLOR_VALID_MOVE_BORDER,
    COLOR_RED,
    COLOR_RED_GLOW,
    COLOR_BLUE,
    COLOR_BLUE_GLOW,
    COLOR_WALL,
    COLOR_WALL_PREVIEW_VALID,
    COLOR_WALL_PREVIEW_INVALID,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
)
from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.ai.search_stats import SearchStats


class BoardRenderer:
    """Responsável por todo o desenho geométrico e renderização da interface."""

    def __init__(
        self,
        board_x: int = 40,
        board_y: int = 90,
        cell_size: int = 66,
        gap_size: int = 14,
    ):
        self.board_x = board_x
        self.board_y = board_y
        self.cell_size = cell_size
        self.gap_size = gap_size
        self.total_size = BOARD_SIZE * cell_size + (BOARD_SIZE - 1) * gap_size

    def get_cell_rect(self, r: int, c: int) -> pygame.Rect:
        """Retorna o retângulo correspondente à casa (r, c) em pixels."""
        x = self.board_x + c * (self.cell_size + self.gap_size)
        y = self.board_y + r * (self.cell_size + self.gap_size)
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    def get_cell_at_pixel(self, px: int, py: int) -> Optional[Tuple[int, int]]:
        """Retorna a coordenada (r, c) da casa sob o pixel do mouse, ou None."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                rect = self.get_cell_rect(r, c)
                if rect.collidepoint(px, py):
                    return (r, c)
        return None

    def get_wall_rect(self, wall_type: str, r: int, c: int) -> pygame.Rect:
        """
        Retorna o retângulo correspondente à barricada em pixels:
        - 'H': ocupa a fenda entre linha r e r+1, cobrindo colunas c e c+1.
        - 'V': ocupa a fenda entre coluna c e c+1, cobrindo linhas r e r+1.
        """
        step = self.cell_size + self.gap_size
        wall_len = 2 * self.cell_size + self.gap_size

        if wall_type == WALL_HORIZONTAL:
            x = self.board_x + c * step
            y = self.board_y + r * step + self.cell_size
            return pygame.Rect(x, y, wall_len, self.gap_size)
        else:
            x = self.board_x + c * step + self.cell_size
            y = self.board_y + r * step
            return pygame.Rect(x, y, self.gap_size, wall_len)

    def get_wall_at_pixel(self, px: int, py: int) -> Optional[Tuple[str, int, int]]:
        """
        Detecta se o mouse está sobre uma fenda ou interseção de barricada.
        Retorna (wall_type, r, c) ou None.
        """
        # Checar proximidade de fendas horizontais e verticais
        best_wall: Optional[Tuple[str, int, int]] = None
        min_dist = float("inf")

        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE - 1):
                # Retângulo da barricada H
                h_rect = self.get_wall_rect(WALL_HORIZONTAL, r, c)
                if h_rect.collidepoint(px, py):
                    return (WALL_HORIZONTAL, r, c)

                # Retângulo da barricada V
                v_rect = self.get_wall_rect(WALL_VERTICAL, r, c)
                if v_rect.collidepoint(px, py):
                    return (WALL_VERTICAL, r, c)

                # Interseção central
                step = self.cell_size + self.gap_size
                inter_x = self.board_x + c * step + self.cell_size
                inter_y = self.board_y + r * step + self.cell_size
                inter_rect = pygame.Rect(inter_x - 4, inter_y - 4, self.gap_size + 8, self.gap_size + 8)

                if inter_rect.collidepoint(px, py):
                    # Decide orientação pela inclinação relativa
                    dx = abs(px - (inter_x + self.gap_size // 2))
                    dy = abs(py - (inter_y + self.gap_size // 2))
                    w_type = WALL_VERTICAL if dy > dx else WALL_HORIZONTAL
                    return (w_type, r, c)

        return None

    def draw_board(
        self,
        surface: pygame.Surface,
        state: GameState,
        hover_cell: Optional[Tuple[int, int]],
        valid_moves: List[MoveAction],
        wall_preview: Optional[Tuple[WallAction, bool]],
        fonts: Dict[str, pygame.font.Font],
    ) -> None:
        """Renderiza todo o tabuleiro, ranhuras, casas, peões e barricadas."""
        # Moldura de fundo do tabuleiro
        pad = 12
        board_bg_rect = pygame.Rect(
            self.board_x - pad,
            self.board_y - pad,
            self.total_size + 2 * pad,
            self.total_size + 2 * pad,
        )
        pygame.draw.rect(surface, COLOR_BOARD_BG, board_bg_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, board_bg_rect, width=2, border_radius=12)

        # Casas (grid 7x7)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                rect = self.get_cell_rect(r, c)
                color = COLOR_CELL_HOVER if (hover_cell == (r, c)) else COLOR_CELL

                # Destaque das linhas de chegada (linhas 0 e 6)
                if r == 0:
                    pygame.draw.rect(surface, (35, 45, 60), rect, border_radius=6)
                elif r == 6:
                    pygame.draw.rect(surface, (55, 35, 40), rect, border_radius=6)
                else:
                    pygame.draw.rect(surface, color, rect, border_radius=6)

                pygame.draw.rect(surface, (50, 56, 68), rect, width=1, border_radius=6)

        # Ranhuras entre casas (indicadores sutis de posicionamento)
        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE - 1):
                step = self.cell_size + self.gap_size
                ix = self.board_x + c * step + self.cell_size
                iy = self.board_y + r * step + self.cell_size
                pygame.draw.circle(surface, (30, 36, 46), (ix + self.gap_size // 2, iy + self.gap_size // 2), 3)

        # Barricadas fixadas no tabuleiro
        for hr, hc in state.h_walls:
            rect = self.get_wall_rect(WALL_HORIZONTAL, hr, hc)
            pygame.draw.rect(surface, COLOR_WALL, rect, border_radius=4)
            pygame.draw.rect(surface, (255, 200, 80), rect, width=1, border_radius=4)

        for vr, vc in state.v_walls:
            rect = self.get_wall_rect(WALL_VERTICAL, vr, vc)
            pygame.draw.rect(surface, COLOR_WALL, rect, border_radius=4)
            pygame.draw.rect(surface, (255, 200, 80), rect, width=1, border_radius=4)

        # Destaque de casas com movimentos válidos (círculos translúcidos)
        valid_destinations = {m.to_pos for m in valid_moves}
        for tr, tc in valid_destinations:
            cell_rect = self.get_cell_rect(tr, tc)
            center = cell_rect.center

            # Círculo externo
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(
                s,
                COLOR_VALID_MOVE,
                (self.cell_size // 2, self.cell_size // 2),
                self.cell_size // 2 - 8,
            )
            surface.blit(s, cell_rect.topleft)
            pygame.draw.circle(
                surface,
                COLOR_VALID_MOVE_BORDER,
                center,
                self.cell_size // 2 - 8,
                width=2,
            )

        # Peões dos jogadores
        self._draw_pawn(surface, state.red_pos, COLOR_RED, COLOR_RED_GLOW, "V", fonts["bold"])
        self._draw_pawn(surface, state.blue_pos, COLOR_BLUE, COLOR_BLUE_GLOW, "A", fonts["bold"])

        # Preview de barricada em tempo real (sob o cursor)
        if wall_preview is not None:
            w_action, is_valid = wall_preview
            w_rect = self.get_wall_rect(w_action.wall_type, w_action.row, w_action.col)
            color = COLOR_WALL_PREVIEW_VALID if is_valid else COLOR_WALL_PREVIEW_INVALID

            s = pygame.Surface((w_rect.width, w_rect.height), pygame.SRCALPHA)
            s.fill(color)
            surface.blit(s, w_rect.topleft)
            border_col = (70, 220, 130) if is_valid else (240, 80, 80)
            pygame.draw.rect(surface, border_col, w_rect, width=2, border_radius=4)

    def _draw_pawn(
        self,
        surface: pygame.Surface,
        pos: Tuple[int, int],
        color: Tuple[int, int, int],
        glow_color: Tuple[int, int, int],
        label: str,
        font: pygame.font.Font,
    ) -> None:
        """Desenha um peão elegante com brilho e borda destacada."""
        rect = self.get_cell_rect(pos[0], pos[1])
        center = rect.center
        radius = self.cell_size // 2 - 10

        # Brilho externo sutil
        s = pygame.Surface((radius * 2 + 16, radius * 2 + 16), pygame.SRCALPHA)
        pygame.draw.circle(s, (*glow_color, 60), (radius + 8, radius + 8), radius + 6)
        surface.blit(s, (center[0] - radius - 8, center[1] - radius - 8))

        # Corpo do peão
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, (255, 255, 255), center, radius, width=2)

        # Letra indicadora no centro do peão
        text_surf = font.render(label, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=center)
        surface.blit(text_surf, text_rect)


class UIRenderer:
    """Gerencia a renderização de cabeçalhos, painel de IA e diálogos."""

    def __init__(self, board_renderer: BoardRenderer):
        self.board = board_renderer

    def draw_top_bar(
        self,
        surface: pygame.Surface,
        state: GameState,
        mode: str,
        is_bot_thinking: bool,
        fonts: Dict[str, pygame.font.Font],
    ) -> None:
        """Desenha a barra superior com informações de turno e barricadas."""
        bar_rect = pygame.Rect(40, 18, 1020, 56)
        pygame.draw.rect(surface, COLOR_PANEL_BG, bar_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, bar_rect, width=1, border_radius=10)

        # Indicador de turno
        turn_color = COLOR_RED if state.turn == PLAYER_RED else COLOR_BLUE
        turn_name = PLAYER_NAMES[state.turn]
        status_text = f"Vez de: {turn_name}"
        if is_bot_thinking:
            status_text += " (Bot pensando...)"

        pygame.draw.circle(surface, turn_color, (68, 46), 10)
        status_surf = fonts["bold"].render(status_text, True, COLOR_TEXT)
        surface.blit(status_surf, (88, 36))

        # Barricadas restantes do Vermelho
        red_walls_surf = fonts["normal"].render(f"Barricadas Vermelho: {state.red_walls}", True, COLOR_RED)
        surface.blit(red_walls_surf, (490, 36))

        # Barricadas restantes do Azul
        blue_walls_surf = fonts["normal"].render(f"Barricadas Azul: {state.blue_walls}", True, COLOR_BLUE)
        surface.blit(blue_walls_surf, (770, 36))

    def draw_ai_panel(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
        ai_name: str,
        depth: int,
        stats: SearchStats,
        dist_red: int,
        dist_blue: int,
        dual_stats: Optional[Dict[str, Any]],
        fonts: Dict[str, pygame.font.Font],
    ) -> None:
        """Desenha o painel lateral com métricas da IA."""
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, panel_rect, width=1, border_radius=12)

        x = panel_rect.x + 20
        y = panel_rect.y + 18
        line_h = 28

        title_surf = fonts["title"].render("Telemetria da IA", True, COLOR_ACCENT)
        surface.blit(title_surf, (x, y))
        y += 38

        # Linha separadora
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x, y), (panel_rect.right - 20, y), 1)
        y += 14

        info_items = [
            ("Algoritmo", ai_name),
            ("Profundidade (Plies)", str(depth)),
            ("Nós Visitados", f"{stats.nodes_visited:,}"),
            ("Nós Podados", f"{stats.nodes_pruned:,}"),
            ("Tempo de Decisão", f"{stats.execution_time:.3f} s"),
            ("Estados Avaliados", f"{stats.states_evaluated:,}"),
            ("Nós por Segundo (NPS)", f"{int(stats.nodes_visited / stats.execution_time) if stats.execution_time > 0 else 0:,}"),
            ("Tabela Transposição Hits", f"{stats.tt_hits:,}"),
            ("Distância Vermelho (Meta)", str(dist_red)),
            ("Distância Azul (Meta)", str(dist_blue)),
        ]

        for label, val in info_items:
            lbl_surf = fonts["normal"].render(label + ":", True, COLOR_TEXT_MUTED)
            val_surf = fonts["bold"].render(val, True, COLOR_TEXT)
            surface.blit(lbl_surf, (x, y))
            surface.blit(val_surf, (panel_rect.right - val_surf.get_width() - 20, y))
            y += line_h

        # Se for Bot vs Bot com dados de ambos
        if dual_stats:
            y += 10
            pygame.draw.line(surface, COLOR_PANEL_BORDER, (x, y), (panel_rect.right - 20, y), 1)
            y += 12
            dual_title = fonts["bold"].render("Comparativo Bot vs Bot", True, COLOR_ACCENT)
            surface.blit(dual_title, (x, y))
            y += 26
            b1_txt = f"Red Nós Totais: {dual_stats.get('red_nodes', 0):,}"
            b2_txt = f"Blue Nós Totais: {dual_stats.get('blue_nodes', 0):,}"
            surface.blit(fonts["small"].render(b1_txt, True, COLOR_RED), (x, y))
            y += 20
            surface.blit(fonts["small"].render(b2_txt, True, COLOR_BLUE), (x, y))

    def draw_game_over_overlay(
        self,
        surface: pygame.Surface,
        winner: int,
        fonts: Dict[str, pygame.font.Font],
    ) -> None:
        """Desenha a tela de resultado final com vitória ou derrota."""
        # Fundo semitransparente escuro
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((10, 14, 20, 210))
        surface.blit(overlay, (0, 0))

        # Caixa central
        box_w, box_h = 520, 260
        box_x = (surface.get_width() - box_w) // 2
        box_y = (surface.get_height() - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(surface, COLOR_PANEL_BG, box_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_ACCENT, box_rect, width=2, border_radius=16)

        winner_name = PLAYER_NAMES.get(winner, "Desconhecido")
        winner_color = COLOR_RED if winner == PLAYER_RED else COLOR_BLUE

        title_surf = fonts["title"].render("FIM DE PARTIDA!", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(box_rect.centerx, box_y + 45)))

        sub_text = f"Vitória do Jogador {winner_name}!"
        sub_surf = fonts["bold"].render(sub_text, True, winner_color)
        surface.blit(sub_surf, sub_surf.get_rect(center=(box_rect.centerx, box_y + 95)))
