"""
Testes unitários para Minimax com Poda Alpha-Beta, Tabela de Transposição e Ordenação de Movimentos.
"""

import pytest
from src.game.state import GameState
from src.game.rules import get_legal_actions
from src.ai.minimax import minimax_search
from src.ai.alpha_beta import alpha_beta_search
from src.ai.transposition_table import TranspositionTable, TT_EXACT
from src.ai.evaluation import evaluate_simple
from src.utils.constants import PLAYER_RED, PLAYER_BLUE


def test_alpha_beta_finds_immediate_win():
    # Vermelho em (1, 3) deve vencer imediatamente movendo para (0, 3)
    state = GameState(red_pos=(1, 3), blue_pos=(3, 3), turn=PLAYER_RED)
    best_action, score, stats = alpha_beta_search(state, depth=1)

    assert best_action is not None
    assert best_action.is_move
    assert best_action.to_pos[0] == 0
    assert score > 90_000


def test_alpha_beta_pruning_efficiency_vs_minimax():
    # Em profundidade 2 com busca simples, Alpha-Beta deve visitar menos nós que o Minimax
    # e encontrar o mesmo score exato!
    state = GameState(red_pos=(4, 3), blue_pos=(2, 3), red_walls=1, blue_walls=1)

    # Minimax puro
    _, score_mm, stats_mm = minimax_search(state, depth=2, eval_fn=evaluate_simple)

    # Alpha-Beta sem TT e sem ordenação para comparação justa
    _, score_ab, stats_ab = alpha_beta_search(
        state,
        depth=2,
        use_ordering=False,
        use_tt=False,
        iterative_deepening=False,
        eval_fn=evaluate_simple,
    )

    # Scores devem ser idênticos
    assert score_ab == pytest.approx(score_mm)
    # Alpha-Beta deve visitar menos ou igual quantidade de nós
    assert stats_ab.nodes_visited <= stats_mm.nodes_visited
    assert stats_ab.nodes_pruned >= 0


def test_alpha_beta_with_ordering_reduces_nodes():
    # Com ordenação ativa, a poda ocorre ainda mais cedo
    state = GameState(red_pos=(4, 3), blue_pos=(2, 3), red_walls=2, blue_walls=2)

    _, _, stats_no_ord = alpha_beta_search(
        state,
        depth=2,
        use_ordering=False,
        use_tt=False,
        iterative_deepening=False,
    )

    _, _, stats_with_ord = alpha_beta_search(
        state,
        depth=2,
        use_ordering=True,
        use_tt=False,
        iterative_deepening=False,
    )

    assert stats_with_ord.nodes_visited <= stats_no_ord.nodes_visited


def test_transposition_table_lookup_and_store():
    tt = TranspositionTable()
    state = GameState(red_pos=(3, 3), blue_pos=(1, 3))
    key = state.to_hash_key()

    assert tt.lookup(key) is None
    tt.store(key, depth=2, value=42.0, flag=TT_EXACT, best_move=None)

    entry = tt.lookup(key)
    assert entry is not None
    assert entry.depth == 2
    assert entry.value == 42.0
    assert entry.flag == TT_EXACT


def test_time_limit_and_fallback():
    state = GameState()
    # Limite de tempo extremamente curto (0.001s)
    best_action, _, stats = alpha_beta_search(
        state,
        depth=5,
        time_limit=0.001,
        iterative_deepening=True,
    )

    # Sempre deve retornar uma ação legal válida
    assert best_action is not None
    legal_actions = get_legal_actions(state, state.turn)
    assert best_action in legal_actions
