"""
Implementação do algoritmo Minimax recursivo puro (sem poda).
Desenvolvido para fins didáticos e comparação de desempenho em benchmarks acadêmicos.
"""

import time
import math
from typing import Optional, Tuple, Callable
from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.game.rules import get_legal_actions
from src.ai.evaluation import evaluate_state
from src.ai.search_stats import SearchStats


def minimax_search(
    state: GameState,
    depth: int,
    max_player: Optional[int] = None,
    eval_fn: Optional[Callable[[GameState, int, int], float]] = None,
    stats: Optional[SearchStats] = None,
) -> Tuple[Optional[MoveAction | WallAction], float, SearchStats]:
    """
    Executa a busca Minimax clássica a partir do estado fornecido.

    Retorna:
    - best_action: melhor ação a ser executada pelo jogador do turno.
    - best_score: valor numérico atribuído à melhor ação.
    - stats: estatísticas de nós visitados e tempo decorrido.
    """
    if max_player is None:
        max_player = state.turn

    if eval_fn is None:
        eval_fn = evaluate_state

    if stats is None:
        stats = SearchStats()
    else:
        stats.reset()

    start_time = time.perf_counter()

    def _minimax(
        curr_state: GameState,
        curr_depth: int,
        ply: int,
    ) -> Tuple[Optional[MoveAction | WallAction], float]:
        stats.max_depth_reached = max(stats.max_depth_reached, ply)

        # Condição de parada: profundidade atingida ou jogo terminado
        if curr_depth == 0 or curr_state.is_terminal():
            stats.states_evaluated += 1
            return None, eval_fn(curr_state, max_player, ply)

        actions = get_legal_actions(curr_state, curr_state.turn)
        if not actions:
            stats.states_evaluated += 1
            return None, eval_fn(curr_state, max_player, ply)

        is_max = (curr_state.turn == max_player)

        if is_max:
            best_val = -math.inf
            best_act = None
            for action in actions:
                stats.nodes_visited += 1
                child_state = curr_state.apply_action(action)
                _, val = _minimax(child_state, curr_depth - 1, ply + 1)
                if val > best_val or best_act is None:
                    best_val = val
                    best_act = action
            return best_act, best_val
        else:
            best_val = math.inf
            best_act = None
            for action in actions:
                stats.nodes_visited += 1
                child_state = curr_state.apply_action(action)
                _, val = _minimax(child_state, curr_depth - 1, ply + 1)
                if val < best_val or best_act is None:
                    best_val = val
                    best_act = action
            return best_act, best_val

    best_action, best_score = _minimax(state, depth, 0)
    stats.execution_time = time.perf_counter() - start_time

    return best_action, best_score, stats
