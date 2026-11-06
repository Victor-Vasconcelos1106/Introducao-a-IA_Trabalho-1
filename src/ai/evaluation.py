"""
Função de avaliação heurística para busca adversarial no jogo Barricade AI.
Calcula a estimativa de utilidade de um estado sempre da perspectiva do jogador MAX.
"""

from typing import Dict, Optional
from src.utils.constants import (
    PLAYER_RED,
    PLAYER_BLUE,
    WIN_SCORE,
    LOSS_SCORE,
    EVAL_WEIGHTS,
)
from src.game.state import GameState
from src.game.pathfinding import get_shortest_distance


def evaluate_simple(state: GameState, max_player: int, ply: int = 0) -> float:
    """
    Função heurística elementar baseada puramente na diferença de distâncias mínimas:
    H(s) = 100 * (D_oponente - D_IA)
    """
    opp_player = state.get_opponent(max_player)

    if state.is_terminal():
        if state.winner == max_player:
            return float(WIN_SCORE - ply)
        elif state.winner == opp_player:
            return float(LOSS_SCORE + ply)
        return 0.0

    dist_max = get_shortest_distance(
        state.get_player_pos(max_player),
        state.get_goal_row(max_player),
        state.h_walls,
        state.v_walls,
    )
    dist_opp = get_shortest_distance(
        state.get_player_pos(opp_player),
        state.get_goal_row(opp_player),
        state.h_walls,
        state.v_walls,
    )

    return 100.0 * (dist_opp - dist_max)


def evaluate_state(
    state: GameState,
    max_player: int,
    ply: int = 0,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Função heurística completa e ponderada para avaliação de estados não-terminais.
    Considera:
    1. Distâncias mínimas via BFS até os respectivos objetivos.
    2. Quantidade e diferença de barricadas restantes (recursos estratégicos).
    3. Avanço posicional em direção à linha de chegada.
    """
    if weights is None:
        weights = EVAL_WEIGHTS

    opp_player = state.get_opponent(max_player)

    # Avaliação de estados terminais tem prioridade absoluta em magnitude
    if state.is_terminal():
        if state.winner == max_player:
            return float(WIN_SCORE - ply)
        elif state.winner == opp_player:
            return float(LOSS_SCORE + ply)
        return 0.0

    # 1. Distâncias mínimas BFS
    dist_max = get_shortest_distance(
        state.get_player_pos(max_player),
        state.get_goal_row(max_player),
        state.h_walls,
        state.v_walls,
    )
    dist_opp = get_shortest_distance(
        state.get_player_pos(opp_player),
        state.get_goal_row(opp_player),
        state.h_walls,
        state.v_walls,
    )

    # 2. Recursos de barricadas
    walls_max = state.get_player_walls(max_player)
    walls_opp = state.get_player_walls(opp_player)
    walls_diff = walls_max - walls_opp

    # 3. Avanço posicional
    pos_max = state.get_player_pos(max_player)
    pos_opp = state.get_player_pos(opp_player)

    advance_max = (6 - pos_max[0]) if max_player == PLAYER_RED else pos_max[0]
    advance_opp = (6 - pos_opp[0]) if opp_player == PLAYER_RED else pos_opp[0]
    advance_diff = advance_max - advance_opp

    w_dist = weights.get("distance", 100.0)
    w_walls = weights.get("walls", 15.0)
    w_adv = weights.get("goal_advance", 10.0)

    score = (
        w_dist * (dist_opp - dist_max)
        + w_walls * walls_diff
        + w_adv * advance_diff
    )

    return float(score)
