"""
Testes unitários para a geometria do tabuleiro e colisões de barricadas.
"""

import pytest
from src.game.board import (
    is_in_bounds,
    is_valid_wall_coord,
    is_passage_blocked,
    has_wall_collision,
)
from src.utils.constants import WALL_HORIZONTAL, WALL_VERTICAL


def test_in_bounds():
    assert is_in_bounds(0, 0) is True
    assert is_in_bounds(6, 6) is True
    assert is_in_bounds(3, 3) is True
    assert is_in_bounds(-1, 0) is False
    assert is_in_bounds(0, 7) is False
    assert is_in_bounds(7, 3) is False


def test_valid_wall_coord():
    assert is_valid_wall_coord(0, 0) is True
    assert is_valid_wall_coord(5, 5) is True
    assert is_valid_wall_coord(6, 0) is False
    assert is_valid_wall_coord(0, 6) is False
    assert is_valid_wall_coord(-1, 2) is False


def test_passage_blocked_horizontal_wall():
    # Barricada H em (2, 2) bloqueia:
    # (2, 2) <-> (3, 2)
    # (2, 3) <-> (3, 3)
    h_walls = {(2, 2)}
    v_walls = set()

    assert is_passage_blocked(2, 2, 3, 2, h_walls, v_walls) is True
    assert is_passage_blocked(3, 2, 2, 2, h_walls, v_walls) is True
    assert is_passage_blocked(2, 3, 3, 3, h_walls, v_walls) is True
    assert is_passage_blocked(3, 3, 2, 3, h_walls, v_walls) is True

    # Passagens adjacentes não cobertas pela barricada devem estar livres
    assert is_passage_blocked(2, 1, 3, 1, h_walls, v_walls) is False
    assert is_passage_blocked(2, 4, 3, 4, h_walls, v_walls) is False
    # Movimentos laterais na mesma linha devem estar livres
    assert is_passage_blocked(2, 2, 2, 3, h_walls, v_walls) is False


def test_passage_blocked_vertical_wall():
    # Barricada V em (2, 2) bloqueia:
    # (2, 2) <-> (2, 3)
    # (3, 2) <-> (3, 3)
    h_walls = set()
    v_walls = {(2, 2)}

    assert is_passage_blocked(2, 2, 2, 3, h_walls, v_walls) is True
    assert is_passage_blocked(2, 3, 2, 2, h_walls, v_walls) is True
    assert is_passage_blocked(3, 2, 3, 3, h_walls, v_walls) is True
    assert is_passage_blocked(3, 3, 3, 2, h_walls, v_walls) is True

    # Outras passagens desobstruídas
    assert is_passage_blocked(1, 2, 1, 3, h_walls, v_walls) is False
    assert is_passage_blocked(4, 2, 4, 3, h_walls, v_walls) is False
    assert is_passage_blocked(2, 2, 3, 2, h_walls, v_walls) is False


def test_wall_collisions_crossing():
    h_walls = {(2, 2)}
    v_walls = set()

    # Colocar V no mesmo centro (2, 2) deve cruzar (inválido)
    assert has_wall_collision(WALL_VERTICAL, 2, 2, h_walls, v_walls) is True
    # Colocar V em (2, 3) não cruza
    assert has_wall_collision(WALL_VERTICAL, 2, 3, h_walls, v_walls) is False


def test_wall_collisions_overlapping():
    h_walls = {(2, 2)}
    v_walls = set()

    # Mesma posição H
    assert has_wall_collision(WALL_HORIZONTAL, 2, 2, h_walls, v_walls) is True
    # Sobreposição parcial à esquerda (2, 1)
    assert has_wall_collision(WALL_HORIZONTAL, 2, 1, h_walls, v_walls) is True
    # Sobreposição parcial à direita (2, 3)
    assert has_wall_collision(WALL_HORIZONTAL, 2, 3, h_walls, v_walls) is True
    # Adjacente sem sobreposição (2, 4) e (2, 0)
    assert has_wall_collision(WALL_HORIZONTAL, 2, 4, h_walls, v_walls) is False
    assert has_wall_collision(WALL_HORIZONTAL, 2, 0, h_walls, v_walls) is False
