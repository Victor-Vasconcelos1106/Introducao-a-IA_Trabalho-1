"""
Implementação do algoritmo Minimax com Poda Alpha-Beta e otimizações avançadas:
- Poda Alpha-Beta clássica.
- Ordenação de movimentos (Move Ordering).
- Tabela de Transposição (TT) com limites exatos, inferiores e superiores.
- Aprofundamento Iterativo (Iterative Deepening).
- Controle estrito de tempo limite com retorno gracioso da melhor jogada anterior.
"""

import time
import math
from typing import Optional, Tuple, Callable
from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.game.rules import get_legal_actions
from src.ai.evaluation import evaluate_state
from src.ai.search_stats import SearchStats
from src.ai.transposition_table import (
    TranspositionTable,
    TT_EXACT,
    TT_LOWERBOUND,
    TT_UPPERBOUND,
)
from src.ai.move_ordering import order_actions
from src.utils.constants import WIN_SCORE


class SearchTimeoutException(Exception):
    """Exceção interna para interromper a busca quando o tempo limite expirar."""
    pass


def alpha_beta_search(
    state: GameState,
    depth: int,
    max_player: Optional[int] = None,
    use_ordering: bool = True,
    use_tt: bool = True,
    tt: Optional[TranspositionTable] = None,
    iterative_deepening: bool = False,
    time_limit: Optional[float] = None,
    eval_fn: Optional[Callable[[GameState, int, int], float]] = None,
    stats: Optional[SearchStats] = None,
) -> Tuple[Optional[MoveAction | WallAction], float, SearchStats]:
    """
    Executa busca adversarial com poda Alpha-Beta e otimizações configuráveis.

    Parâmetros:
    - state: estado atual do jogo.
    - depth: profundidade máxima de busca (plies).
    - max_player: jogador sob a perspectiva de maximização (padrão: jogador do turno).
    - use_ordering: habilita ordenação de movimentos.
    - use_tt: habilita uso da tabela de transposição.
    - tt: instância compartilhada da Tabela de Transposição (opcional).
    - iterative_deepening: busca de profundidade 1 até 'depth'.
    - time_limit: tempo máximo em segundos (se atingido, retorna o melhor resultado da última profundidade completa).
    - eval_fn: função de avaliação heurística.
    - stats: objeto coletor de estatísticas.
    """
    if max_player is None:
        max_player = state.turn

    if eval_fn is None:
        eval_fn = evaluate_state

    if stats is None:
        stats = SearchStats()
    else:
        stats.reset()

    if use_tt and tt is None:
        tt = TranspositionTable()

    start_time = time.perf_counter()

    def check_timeout() -> None:
        if time_limit is not None and (time.perf_counter() - start_time) >= time_limit:
            raise SearchTimeoutException()

    def _search_node(
        curr_state: GameState,
        curr_depth: int,
        alpha: float,
        beta: float,
        ply: int,
    ) -> Tuple[Optional[MoveAction | WallAction], float]:
        # Verificação periódica de tempo a cada 64 nós
        if (stats.nodes_visited & 63) == 0:
            check_timeout()

        stats.max_depth_reached = max(stats.max_depth_reached, ply)

        # 1. Verificação de estado terminal ou profundidade máxima
        if curr_depth == 0 or curr_state.is_terminal():
            stats.states_evaluated += 1
            return None, eval_fn(curr_state, max_player, ply)

        key = curr_state.to_hash_key()
        tt_move = None
        orig_alpha = alpha
        orig_beta = beta

        # 2. Consulta à Tabela de Transposição
        if use_tt and tt is not None:
            entry = tt.lookup(key)
            if entry is not None:
                tt_move = entry.best_move
                if entry.depth >= curr_depth:
                    stats.tt_hits += 1
                    if entry.flag == TT_EXACT:
                        return entry.best_move, entry.value
                    elif entry.flag == TT_LOWERBOUND:
                        alpha = max(alpha, entry.value)
                    elif entry.flag == TT_UPPERBOUND:
                        beta = min(beta, entry.value)

                    if alpha >= beta:
                        return entry.best_move, entry.value

        # 3. Geração de ações legais
        actions = get_legal_actions(curr_state, curr_state.turn)
        if not actions:
            stats.states_evaluated += 1
            return None, eval_fn(curr_state, max_player, ply)

        # 4. Ordenação de movimentos
        if use_ordering:
            actions = order_actions(actions, curr_state, curr_state.turn, tt_best_move=tt_move)

        is_max = (curr_state.turn == max_player)
        best_act = actions[0] if actions else None

        if is_max:
            best_val = -math.inf
            for idx, action in enumerate(actions):
                stats.nodes_visited += 1
                child_state = curr_state.apply_action(action)
                _, val = _search_node(child_state, curr_depth - 1, alpha, beta, ply + 1)

                if val > best_val:
                    best_val = val
                    best_act = action

                alpha = max(alpha, best_val)
                if beta <= alpha:
                    stats.nodes_pruned += (len(actions) - idx - 1)
                    break
        else:
            best_val = math.inf
            for idx, action in enumerate(actions):
                stats.nodes_visited += 1
                child_state = curr_state.apply_action(action)
                _, val = _search_node(child_state, curr_depth - 1, alpha, beta, ply + 1)

                if val < best_val:
                    best_val = val
                    best_act = action

                beta = min(beta, best_val)
                if beta <= alpha:
                    stats.nodes_pruned += (len(actions) - idx - 1)
                    break

        # 5. Armazenamento na Tabela de Transposição
        if use_tt and tt is not None:
            if best_val <= orig_alpha:
                flag = TT_UPPERBOUND
            elif best_val >= orig_beta:
                flag = TT_LOWERBOUND
            else:
                flag = TT_EXACT
            tt.store(key, curr_depth, best_val, flag, best_act)
            stats.tt_stores += 1

        return best_act, best_val

    # Estratégia de Execução: Aprofundamento Iterativo ou Busca Direta
    best_action_found: Optional[MoveAction | WallAction] = None
    best_score_found: float = 0.0

    if iterative_deepening or time_limit is not None:
        target_max_depth = max(1, depth)
        for d in range(1, target_max_depth + 1):
            try:
                cur_act, cur_score = _search_node(state, d, -math.inf, math.inf, 0)
                if cur_act is not None:
                    best_action_found = cur_act
                    best_score_found = cur_score
                    stats.max_depth_reached = d

                # Se encontrou vitória forçada imediata, não precisa aprofundar mais
                if best_score_found >= WIN_SCORE - 100:
                    break
            except SearchTimeoutException:
                # Interrompido pelo limite de tempo: encerra e mantém a melhor jogada da profundidade anterior
                break
    else:
        try:
            best_action_found, best_score_found = _search_node(state, depth, -math.inf, math.inf, 0)
        except SearchTimeoutException:
            pass

    # Garantia de segurança: se nenhuma ação foi escolhida (ex: timeout instantâneo), escolhe primeira legal
    if best_action_found is None:
        fallback_actions = get_legal_actions(state, state.turn)
        if fallback_actions:
            best_action_found = fallback_actions[0]

    stats.execution_time = time.perf_counter() - start_time
    return best_action_found, best_score_found, stats
