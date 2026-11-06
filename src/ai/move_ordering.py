"""
Ordenação de movimentos para otimização da busca com Poda Alpha-Beta.
Organiza as ações legais da mais promissora para a menos promissora,
maximizando a taxa de podas na árvore de busca.
"""

from typing import List, Optional
from src.game.actions import MoveAction, WallAction
from src.game.state import GameState
from src.game.board import is_passage_blocked
from src.game.pathfinding import get_shortest_distance, get_shortest_path
from src.game.rules import _wall_blocks_path


def score_action(
    action: MoveAction | WallAction,
    state: GameState,
    player: int,
    tt_best_move: Optional[MoveAction | WallAction],
    opp_path: Optional[List],
    curr_my_dist: int,
) -> float:
    """Atribui uma pontuação heurística preliminar a uma ação para ordenação."""
    # 1. Ação sugerida pela Tabela de Transposição (ou Iterative Deepening)
    if tt_best_move is not None and action == tt_best_move:
        return 1_000_000.0

    goal_row = state.get_goal_row(player)

    # 2. Movimentos de Peão
    if action.is_move:
        # Vitória imediata!
        if action.to_pos[0] == goal_row:
            return 500_000.0

        # Avaliar se aproxima da meta
        new_dist = get_shortest_distance(
            action.to_pos,
            goal_row,
            state.h_walls,
            state.v_walls,
        )
        dist_improvement = curr_my_dist - new_dist
        # Peões que avançam recebem alta pontuação
        return 10_000.0 + (dist_improvement * 2000.0)

    # 3. Barricadas
    elif action.is_wall:
        # Se a barricada corta diretamente o menor caminho atual do adversário:
        if opp_path and _wall_blocks_path(action.wall_type, action.row, action.col, opp_path):
            return 8_000.0

        # Barricadas próximas ao adversário
        opp_pos = state.get_player_pos(state.get_opponent(player))
        dist_to_opp = abs(action.row - opp_pos[0]) + abs(action.col - opp_pos[1])
        if dist_to_opp <= 2:
            return 3_000.0 - (dist_to_opp * 500.0)

        return 500.0

    return 0.0


def order_actions(
    actions: List[MoveAction | WallAction],
    state: GameState,
    player: int,
    tt_best_move: Optional[MoveAction | WallAction] = None,
) -> List[MoveAction | WallAction]:
    """
    Ordena as ações legais em ordem decrescente de prioridade:
    1. Melhor movimento da Tabela de Transposição.
    2. Vitórias imediatas.
    3. Peões que avançam em direção à meta.
    4. Barricadas que cortam o caminho do oponente.
    5. Demais movimentações e barricadas.
    """
    if len(actions) <= 1:
        return actions

    opp_player = state.get_opponent(player)
    opp_path = get_shortest_path(
        state.get_player_pos(opp_player),
        state.get_goal_row(opp_player),
        state.h_walls,
        state.v_walls,
    )
    my_dist = get_shortest_distance(
        state.get_player_pos(player),
        state.get_goal_row(player),
        state.h_walls,
        state.v_walls,
    )

    scored_actions = [
        (score_action(action, state, player, tt_best_move, opp_path, my_dist), action)
        for action in actions
    ]

    # Ordena pelo score decrescente
    scored_actions.sort(key=lambda item: item[0], reverse=True)
    return [action for _, action in scored_actions]
