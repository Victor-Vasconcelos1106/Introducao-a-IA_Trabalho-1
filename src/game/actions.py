"""
Definições de ações do jogo Barricade AI.
Representa movimentações de peão e posicionamento de barricadas.
"""

from dataclasses import dataclass
from typing import Tuple, Optional
from src.utils.constants import WALL_HORIZONTAL, WALL_VERTICAL


@dataclass(frozen=True)
class MoveAction:
    """Ação de movimentação de peão para uma casa de destino."""
    to_pos: Tuple[int, int]  # (linha, coluna)

    @property
    def is_wall(self) -> bool:
        return False

    @property
    def is_move(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"Move({self.to_pos[0]}, {self.to_pos[1]})"

    def __repr__(self) -> str:
        return f"MoveAction(to_pos={self.to_pos})"


@dataclass(frozen=True)
class WallAction:
    """Ação de posicionamento de barricada horizontal ('H') ou vertical ('V')."""
    wall_type: str            # 'H' ou 'V'
    row: int                  # 0 <= row < BOARD_SIZE - 1
    col: int                  # 0 <= col < BOARD_SIZE - 1

    @property
    def is_wall(self) -> bool:
        return True

    @property
    def is_move(self) -> bool:
        return False

    def __str__(self) -> str:
        orient = "H" if self.wall_type == WALL_HORIZONTAL else "V"
        return f"Wall({orient}, {self.row}, {self.col})"

    def __repr__(self) -> str:
        return f"WallAction('{self.wall_type}', {self.row}, {self.col})"
