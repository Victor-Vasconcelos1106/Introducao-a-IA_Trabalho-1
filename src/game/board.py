"""
Geometria e validações estruturais do tabuleiro de Barricade AI.
Responsável por verificar limites, passagens bloqueadas por barricadas e
conflitos físicos entre barricadas (sobreposição e cruzamento).
"""

from typing import Set, Tuple
from src.utils.constants import BOARD_SIZE, WALL_HORIZONTAL, WALL_VERTICAL


def is_in_bounds(r: int, c: int) -> bool:
    """Verifica se a coordenada (linha, coluna) pertence ao tabuleiro 7x7."""
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def is_valid_wall_coord(r: int, c: int) -> bool:
    """Verifica se a coordenada da interseção da barricada está dentro dos limites (0 a 5)."""
    return 0 <= r < BOARD_SIZE - 1 and 0 <= c < BOARD_SIZE - 1


def is_passage_blocked(
    r1: int,
    c1: int,
    r2: int,
    c2: int,
    h_walls: Set[Tuple[int, int]],
    v_walls: Set[Tuple[int, int]]
) -> bool:
    """
    Verifica se a passagem direta entre duas casas adjacentes (r1, c1) e (r2, c2)
    está bloqueada por alguma barricada horizontal ou vertical.

    Uma barricada de tamanho 2 cobre duas passagens consecutivas:
    - Barricada Horizontal em (r, c):
      Bloqueia (r, c) <-> (r+1, c) e (r, c+1) <-> (r+1, c+1).
    - Barricada Vertical em (r, c):
      Bloqueia (r, c) <-> (r, c+1) e (r+1, c) <-> (r+1, c+1).
    """
    # Movimento vertical (mesma coluna, linhas adjacentes)
    if c1 == c2:
        top_r = min(r1, r2)
        # O bloqueio ocorre se houver uma barricada H cujo centro é (top_r, c1) ou (top_r, c1 - 1)
        if (top_r, c1) in h_walls or (top_r, c1 - 1) in h_walls:
            return True
        return False

    # Movimento horizontal (mesma linha, colunas adjacentes)
    if r1 == r2:
        left_c = min(c1, c2)
        # O bloqueio ocorre se houver uma barricada V cujo centro é (r1, left_c) ou (r1 - 1, left_c)
        if (r1, left_c) in v_walls or (r1 - 1, left_c) in v_walls:
            return True
        return False

    # Movimento não é adjacente ortogonal direto
    return True


def has_wall_collision(
    wall_type: str,
    r: int,
    c: int,
    h_walls: Set[Tuple[int, int]],
    v_walls: Set[Tuple[int, int]]
) -> bool:
    """
    Verifica se o posicionamento de uma nova barricada causa colisão física:
    - Cruzamento central perpendicular com outra barricada existente.
    - Sobreposição total ou parcial com outra barricada paralela.
    """
    if not is_valid_wall_coord(r, c):
        return True

    if wall_type == WALL_HORIZONTAL:
        # Não pode cruzar com barricada vertical na mesma interseção central (r, c)
        if (r, c) in v_walls:
            return True
        # Não pode sobrepor horizontalmente (mesma posição, ou 1 casa à esquerda/direita)
        if (r, c) in h_walls or (r, c - 1) in h_walls or (r, c + 1) in h_walls:
            return True
        return False

    elif wall_type == WALL_VERTICAL:
        # Não pode cruzar com barricada horizontal na mesma interseção central (r, c)
        if (r, c) in h_walls:
            return True
        # Não pode sobrepor verticalmente (mesma posição, ou 1 casa acima/abaixo)
        if (r, c) in v_walls or (r - 1, c) in v_walls or (r + 1, c) in v_walls:
            return True
        return False

    return True
