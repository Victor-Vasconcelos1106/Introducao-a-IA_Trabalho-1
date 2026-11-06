"""
Componentes visuais reutilizáveis para a interface gráfica com Pygame:
Botões, Contadores/Sliders, Indicadores e Caixas de Diálogo.
"""

import pygame
from typing import Callable, Optional, Tuple
from src.utils.constants import (
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    COLOR_ACCENT,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)


class Button:
    """Botão interativo com efeito hover e callback de clique."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        bg_color: Tuple[int, int, int] = COLOR_BUTTON,
        hover_color: Tuple[int, int, int] = COLOR_BUTTON_HOVER,
        text_color: Tuple[int, int, int] = COLOR_BUTTON_TEXT,
        border_radius: int = 8,
        callback: Optional[Callable[[], None]] = None,
    ):
        self.rect = rect
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.callback = callback
        self.is_hovered = False
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.enabled:
            color = (40, 44, 52)
            txt_color = (100, 105, 115)
        else:
            color = self.hover_color if self.is_hovered else self.bg_color
            txt_color = self.text_color

        # Desenho do retângulo com cantos arredondados
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        # Borda sutil
        border_col = COLOR_ACCENT if (self.is_hovered and self.enabled) else COLOR_PANEL_BORDER
        pygame.draw.rect(surface, border_col, self.rect, width=1, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, txt_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class NumberSpinner:
    """Componente para incrementar/decrementar valores numéricos (ex: Profundidade, Barricadas)."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        value: int,
        min_val: int,
        max_val: int,
        font: pygame.font.Font,
        step: int = 1,
        on_change: Optional[Callable[[int], None]] = None,
    ):
        self.rect = rect
        self.label = label
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.font = font
        self.step = step
        self.on_change = on_change

        btn_w = 32
        self.minus_btn = Button(
            pygame.Rect(rect.right - 2 * btn_w - 6, rect.y + 4, btn_w, rect.height - 8),
            "-",
            font,
            callback=self.decrement,
        )
        self.plus_btn = Button(
            pygame.Rect(rect.right - btn_w, rect.y + 4, btn_w, rect.height - 8),
            "+",
            font,
            callback=self.increment,
        )

    def decrement(self) -> None:
        if self.value - self.step >= self.min_val:
            self.value -= self.step
            if self.on_change:
                self.on_change(self.value)

    def increment(self) -> None:
        if self.value + self.step <= self.max_val:
            self.value += self.step
            if self.on_change:
                self.on_change(self.value)

    def handle_event(self, event: pygame.event.Event) -> bool:
        handled_minus = self.minus_btn.handle_event(event)
        handled_plus = self.plus_btn.handle_event(event)
        return handled_minus or handled_plus

    def draw(self, surface: pygame.Surface) -> None:
        # Fundo do spinner
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, width=1, border_radius=6)

        # Rótulo
        label_surf = self.font.render(self.label, True, COLOR_TEXT)
        surface.blit(label_surf, (self.rect.x + 12, self.rect.y + (self.rect.height - label_surf.get_height()) // 2))

        # Valor
        val_str = str(self.value)
        val_surf = self.font.render(val_str, True, COLOR_ACCENT)
        val_x = self.minus_btn.rect.left - val_surf.get_width() - 16
        surface.blit(val_surf, (val_x, self.rect.y + (self.rect.height - val_surf.get_height()) // 2))

        # Botões
        self.minus_btn.draw(surface)
        self.plus_btn.draw(surface)


class ToggleSwitch:
    """Componente para alternar opções booleanas (SIM / NÃO)."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        value: bool,
        font: pygame.font.Font,
        on_change: Optional[Callable[[bool], None]] = None,
    ):
        self.rect = rect
        self.label = label
        self.value = value
        self.font = font
        self.on_change = on_change

        switch_w = 64
        self.switch_rect = pygame.Rect(rect.right - switch_w, rect.y + 4, switch_w, rect.height - 8)

    def toggle(self) -> None:
        self.value = not self.value
        if self.on_change:
            self.on_change(self.value)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.switch_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.toggle()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, width=1, border_radius=6)

        label_surf = self.font.render(self.label, True, COLOR_TEXT)
        surface.blit(label_surf, (self.rect.x + 12, self.rect.y + (self.rect.height - label_surf.get_height()) // 2))

        # Fundo do interruptor
        bg_color = (46, 160, 67) if self.value else (60, 66, 78)
        pygame.draw.rect(surface, bg_color, self.switch_rect, border_radius=12)

        txt = "ON" if self.value else "OFF"
        txt_surf = self.font.render(txt, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=self.switch_rect.center)
        surface.blit(txt_surf, txt_rect)
