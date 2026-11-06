"""
Telas de Menu Principal e Configurações para a interface Pygame de Barricade AI.
"""

import pygame
from typing import Callable, Dict, Any
from src.utils.constants import (
    COLOR_BG,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_RED,
    COLOR_BLUE,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    MODE_P_VS_BOT,
    MODE_BOT_VS_BOT,
    MODE_P_VS_P,
)
from src.ui.components import Button, NumberSpinner, ToggleSwitch


class MainMenu:
    """Tela Inicial do Jogo."""

    def __init__(
        self,
        on_start_game: Callable[[str], None],
        on_open_settings: Callable[[], None],
        on_quit: Callable[[], None],
        fonts: Dict[str, pygame.font.Font],
    ):
        self.on_start_game = on_start_game
        self.on_open_settings = on_open_settings
        self.on_quit = on_quit
        self.fonts = fonts

        btn_w, btn_h = 360, 48
        start_x = (1100 - btn_w) // 2
        start_y = 250
        gap = 16

        self.buttons = [
            Button(
                pygame.Rect(start_x, start_y, btn_w, btn_h),
                "1. Jogador contra Bot",
                fonts["bold"],
                callback=lambda: on_start_game(MODE_P_VS_BOT),
            ),
            Button(
                pygame.Rect(start_x, start_y + (btn_h + gap), btn_w, btn_h),
                "2. Bot contra Bot (Experimentos)",
                fonts["bold"],
                callback=lambda: on_start_game(MODE_BOT_VS_BOT),
            ),
            Button(
                pygame.Rect(start_x, start_y + 2 * (btn_h + gap), btn_w, btn_h),
                "3. Jogador contra Jogador (Local)",
                fonts["bold"],
                callback=lambda: on_start_game(MODE_P_VS_P),
            ),
            Button(
                pygame.Rect(start_x, start_y + 3 * (btn_h + gap), btn_w, btn_h),
                "Configurações da IA & Regras",
                fonts["normal"],
                callback=on_open_settings,
            ),
            Button(
                pygame.Rect(start_x, start_y + 4 * (btn_h + gap), btn_w, btn_h),
                "Sair do Jogo",
                fonts["normal"],
                bg_color=(55, 30, 35),
                hover_color=(75, 40, 45),
                callback=on_quit,
            ),
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        # Título principal com brilho/estilo
        title_surf = self.fonts["giant"].render("BARRICADE AI", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(550, 110))
        surface.blit(title_surf, title_rect)

        sub_surf = self.fonts["normal"].render(
            "Jogo com Busca Adversarial — Minimax, Poda Alpha-Beta, BFS e Otimizações",
            True,
            COLOR_ACCENT,
        )
        surface.blit(sub_surf, sub_surf.get_rect(center=(550, 160)))

        # Sub-informação acadêmica
        acad_surf = self.fonts["small"].render(
            "Trabalho Acadêmico de Inteligência Artificial — Tabuleiro 7x7",
            True,
            COLOR_TEXT_MUTED,
        )
        surface.blit(acad_surf, acad_surf.get_rect(center=(550, 190)))

        for btn in self.buttons:
            btn.draw(surface)


class SettingsMenu:
    """Tela de Configuração de Parâmetros de IA e Regras."""

    def __init__(
        self,
        config: Dict[str, Any],
        on_save: Callable[[], None],
        fonts: Dict[str, pygame.font.Font],
    ):
        self.config = config
        self.on_save = on_save
        self.fonts = fonts

        box_w, box_h = 600, 48
        x = (1100 - box_w) // 2
        y = 120
        gap = 14

        self.spinners = [
            NumberSpinner(
                pygame.Rect(x, y, box_w, box_h),
                "Profundidade do Bot 1 (Plies)",
                config["bot1_depth"],
                1,
                6,
                fonts["normal"],
                on_change=lambda val: config.update({"bot1_depth": val}),
            ),
            NumberSpinner(
                pygame.Rect(x, y + (box_h + gap), box_w, box_h),
                "Profundidade do Bot 2 (Plies)",
                config["bot2_depth"],
                1,
                6,
                fonts["normal"],
                on_change=lambda val: config.update({"bot2_depth": val}),
            ),
            NumberSpinner(
                pygame.Rect(x, y + 2 * (box_h + gap), box_w, box_h),
                "Quantidade Inicial de Barricadas",
                config["initial_walls"],
                0,
                10,
                fonts["normal"],
                on_change=lambda val: config.update({"initial_walls": val}),
            ),
            NumberSpinner(
                pygame.Rect(x, y + 3 * (box_h + gap), box_w, box_h),
                "Tempo Máximo de Decisão (segundos)",
                int(config["time_limit"]),
                1,
                10,
                fonts["normal"],
                on_change=lambda val: config.update({"time_limit": float(val)}),
            ),
        ]

        toggle_y = y + 4 * (box_h + gap)
        self.toggles = [
            ToggleSwitch(
                pygame.Rect(x, toggle_y, box_w, box_h),
                "Poda Alpha-Beta Ativa",
                config["use_alpha_beta"],
                fonts["normal"],
                on_change=lambda val: config.update({"use_alpha_beta": val}),
            ),
            ToggleSwitch(
                pygame.Rect(x, toggle_y + (box_h + gap), box_w, box_h),
                "Tabela de Transposição (TT) Ativa",
                config["use_tt"],
                fonts["normal"],
                on_change=lambda val: config.update({"use_tt": val}),
            ),
            ToggleSwitch(
                pygame.Rect(x, toggle_y + 2 * (box_h + gap), box_w, box_h),
                "Ordenação de Movimentos Ativa",
                config["use_ordering"],
                fonts["normal"],
                on_change=lambda val: config.update({"use_ordering": val}),
            ),
        ]

        save_y = toggle_y + 3 * (box_h + gap) + 12
        self.save_btn = Button(
            pygame.Rect(x + 100, save_y, box_w - 200, 46),
            "Salvar e Voltar",
            fonts["bold"],
            bg_color=(35, 100, 50),
            hover_color=(45, 130, 65),
            callback=on_save,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        for sp in self.spinners:
            sp.handle_event(event)
        for tg in self.toggles:
            tg.handle_event(event)
        self.save_btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        title_surf = self.fonts["title"].render("Configurações da Inteligência Artificial", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(550, 60)))

        for sp in self.spinners:
            sp.draw(surface)
        for tg in self.toggles:
            tg.draw(surface)
        self.save_btn.draw(surface)
