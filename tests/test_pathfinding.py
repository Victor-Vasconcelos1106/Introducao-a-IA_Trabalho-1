"""
Testes unitários para busca em largura (BFS) e cálculo de caminhos mínimos.
"""

import pytest
from src.game.pathfinding import (
    has_path_to_goal,
    get_shortest_distance,
    get_shortest_path,
    get_all_distances_to_goal_row,
)
from src.utils.constants import GOAL_ROW_RED, GOAL_ROW_BLUE, START_POS_RED, START_POS_BLUE


def test_initial_distances():
    # Sem barricadas, distância em linha reta para 7x7
    # Vermelho em (6, 3) até linha 0 -> 6 passos
    dist_red = get_shortest_distance(START_POS_RED, GOAL_ROW_RED, set(), set())
    assert dist_red == 6

    # Azul em (0, 3) até linha 6 -> 6 passos
    dist_blue = get_shortest_distance(START_POS_BLUE, GOAL_ROW_BLUE, set(), set())
    assert dist_blue == 6


def test_shortest_path_reconstruction():
    path = get_shortest_path((6, 3), 0, set(), set())
    assert path is not None
    assert len(path) == 7  # 6 passos = 7 nós
    assert path[0] == (6, 3)
    assert path[-1][0] == 0


def test_path_with_detour():
    # Colocar barricada H bloqueando o caminho reto do Vermelho na frente dele:
    # Vermelho em (6, 3). Barricada H em (5, 2) bloqueia:
    # (5, 2) <-> (6, 2) e (5, 3) <-> (6, 3)
    h_walls = {(5, 2)}
    v_walls = set()

    # O vermelho precisa contornar para a coluna 4 (1 passo lateral + 6 passos verticais = 7 passos)
    dist = get_shortest_distance((6, 3), 0, h_walls, v_walls)
    assert dist == 7
    assert has_path_to_goal((6, 3), 0, h_walls, v_walls) is True


def test_blocked_path_completely():
    # Encurralar completamente uma casa no canto (0, 0)
    # Bloquear (0, 0) <-> (0, 1) com V(0, 0)
    # Bloquear (0, 0) <-> (1, 0) com H(0, 0)
    h_walls = {(0, 0)}
    v_walls = {(0, 0)}

    # Casa (1, 0) tentando chegar na linha 0 tem outros caminhos, mas e de (1, 0) até linha 6?
    # Vamos bloquear completamente toda a linha de saída
    # Em 7x7, cobrir linha 1 inteira com H(0, 0), H(0, 2), H(0, 4)
    # Note: H(0, 0) cobre cols 0, 1; H(0, 2) cobre 2, 3; H(0, 4) cobre 4, 5.
    # Falta col 6. Adicionar H(0, 5) causaria sobreposição com H(0, 4), mas
    # podemos fechar col 6 com V walls ou fechando o jogador em um quadrado.
    # Vamos fechar o peão em (6, 3):
    # Cima: H(5, 2) e H(5, 3) se sobrepõem, mas H(5, 2) cobre col 2, 3 e H(5, 4) cobre 4, 5
    # Então H(5, 2) cobre (5, 2)-(6, 2) e (5, 3)-(6, 3).
    # Esquerda de (6, 3): V(5, 2) fecha entre col 2 e 3? V(5, 2) fecha (5, 2)-(5, 3) e (6, 2)-(6, 3).
    # Direita de (6, 3): V(5, 3) fecha (5, 3)-(5, 4) e (6, 3)-(6, 4).
    # Assim, (6, 3) não pode ir para cima (H 5, 2), nem para esquerda (V 5, 2), nem para direita (V 5, 3),
    # e baixo é a borda do tabuleiro (linha 6)!
    h_trapped = {(5, 2)}
    v_trapped = {(5, 2), (5, 3)}

    assert has_path_to_goal((6, 3), 0, h_trapped, v_trapped) is False
    assert get_shortest_distance((6, 3), 0, h_trapped, v_trapped) == 999
    assert get_shortest_path((6, 3), 0, h_trapped, v_trapped) is None


def test_all_distances_to_goal():
    dist_map = get_all_distances_to_goal_row(0, set(), set())
    assert len(dist_map) == 49
    assert dist_map[(6, 3)] == 6
    assert dist_map[(0, 0)] == 0
    assert dist_map[(0, 6)] == 0
    assert dist_map[(3, 3)] == 3
