"""
Algoritmos de busca em largura (BFS) para cálculo de menores distâncias
e validação de caminhos no jogo Barricade AI.
"""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from src.utils.constants import BOARD_SIZE
from src.game.board import is_in_bounds, is_passage_blocked

# Movimentos ortogonais possíveis a partir de qualquer casa
ORTHOGONAL_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def get_all_distances_to_goal_row(
    goal_row: int,
    h_walls: Set[Tuple[int, int]],
    v_walls: Set[Tuple[int, int]]
) -> Dict[Tuple[int, int], int]:
    """
    Executa uma BFS invertida a partir de todas as casas da linha de chegada (goal_row).
    Retorna um dicionário mapeando cada casa acessível (r, c) à sua menor distância até a meta.
    Se uma casa não constar no dicionário, significa que não há caminho até a meta.
    """
    distances: Dict[Tuple[int, int], int] = {}
    queue: deque[Tuple[int, int]] = deque()

    # Inicializa todas as casas da linha de meta com distância 0
    for col in range(BOARD_SIZE):
        cell = (goal_row, col)
        distances[cell] = 0
        queue.append(cell)

    while queue:
        r, c = queue.popleft()
        curr_dist = distances[(r, c)]

        for dr, dc in ORTHOGONAL_DIRECTIONS:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            if is_in_bounds(nr, nc) and neighbor not in distances:
                # Verifica se a passagem não está bloqueada por barricada
                if not is_passage_blocked(r, c, nr, nc, h_walls, v_walls):
                    distances[neighbor] = curr_dist + 1
                    queue.append(neighbor)

    return distances


def has_path_to_goal(
    start_pos: Tuple[int, int],
    goal_row: int,
    h_walls: Set[Tuple[int, int]],
    v_walls: Set[Tuple[int, int]]
) -> bool:
    """
    Verifica se existe pelo menos um caminho válido da posição inicial
    até qualquer casa da linha de chegada especificada.
    """
    if start_pos[0] == goal_row:
        return True

    visited: Set[Tuple[int, int]] = {start_pos}
    queue: deque[Tuple[int, int]] = deque([start_pos])

    while queue:
        r, c = queue.popleft()
        if r == goal_row:
            return True

        for dr, dc in ORTHOGONAL_DIRECTIONS:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            if is_in_bounds(nr, nc) and neighbor not in visited:
                if not is_passage_blocked(r, c, nr, nc, h_walls, v_walls):
                    visited.add(neighbor)
                    queue.append(neighbor)

    return False


def get_shortest_distance(
    start_pos: Tuple[int, int],
    goal_row: int,
    h_walls: Set[Tuple[int, int]],
    v_walls: Set[Tuple[int, int]]
) -> int:
    """
    Calcula a menor distância (número de passos) da posição start_pos até a linha goal_row.
    Retorna 999 se não houver caminho.
    """
    if start_pos[0] == goal_row:
        return 0

    visited: Set[Tuple[int, int]] = {start_pos}
    queue: deque[Tuple[int, int, int]] = deque([(start_pos[0], start_pos[1], 0)])

    while queue:
        r, c, dist = queue.popleft()
        if r == goal_row:
            return dist

        for dr, dc in ORTHOGONAL_DIRECTIONS:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            if is_in_bounds(nr, nc) and neighbor not in visited:
                if not is_passage_blocked(r, c, nr, nc, h_walls, v_walls):
                    visited.add(neighbor)
                    queue.append((nr, nc, dist + 1))

    return 999


def get_shortest_path(
    start_pos: Tuple[int, int],
    goal_row: int,
    h_walls: Set[Tuple[int, int]],
    v_walls: Set[Tuple[int, int]]
) -> Optional[List[Tuple[int, int]]]:
    """
    Reconstrói o menor caminho completo da posição start_pos até a linha goal_row.
    Retorna uma lista de coordenadas [(r0, c0), (r1, c1), ...] ou None se inalcançável.
    """
    if start_pos[0] == goal_row:
        return [start_pos]

    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
    visited: Set[Tuple[int, int]] = {start_pos}
    queue: deque[Tuple[int, int]] = deque([start_pos])
    target_reached: Optional[Tuple[int, int]] = None

    while queue:
        r, c = queue.popleft()
        if r == goal_row:
            target_reached = (r, c)
            break

        for dr, dc in ORTHOGONAL_DIRECTIONS:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            if is_in_bounds(nr, nc) and neighbor not in visited:
                if not is_passage_blocked(r, c, nr, nc, h_walls, v_walls):
                    visited.add(neighbor)
                    parent[neighbor] = (r, c)
                    queue.append(neighbor)

    if target_reached is None:
        return None

    # Reconstrói caminho do destino até a origem
    path = [target_reached]
    curr = target_reached
    while curr != start_pos:
        curr = parent[curr]
        path.append(curr)

    path.reverse()
    return path
