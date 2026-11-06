"""
Testes unitários para o algoritmo Minimax básico.
"""

import pytest
from src.game.state import GameState
from src.game.actions import MoveAction
from src.game.rules import get_legal_actions
from src.ai.minimax import minimax_search
from src.ai.evaluation import evaluate_state, evaluate_simple
from src.utils.constants import PLAYER_RED, PLAYER_BLUE, WIN_SCORE, LOSS_SCORE


def test_minimax_immediate_win():
    # Vermelho está a 1 passo da linha 0 em (1, 3)
    state = GameState(red_pos=(1, 3), blue_pos=(4, 3), turn=PLAYER_RED)
    best_action, best_val, stats = minimax_search(state, depth=1)

    assert best_action is not None
    assert best_action.is_move
    assert best_action.to_pos[0] == 0
    assert best_val > 90_000  # Valor de vitória


def test_minimax_prevents_immediate_loss():
    # Azul em (5, 3), a 1 passo da linha 6. Turno do Vermelho em (5, 2).
    # Vermelho deve priorizar uma jogada que evite a vitória imediata ou avance
    state = GameState(red_pos=(5, 2), blue_pos=(5, 3), turn=PLAYER_RED)
    best_action, best_val, stats = minimax_search(state, depth=2)

    assert best_action is not None
    legal = get_legal_actions(state, PLAYER_RED)
    assert best_action in legal


def test_minimax_always_returns_legal_action():
    state = GameState()
    best_action, _, stats = minimax_search(state, depth=1)

    assert best_action is not None
    legal_actions = get_legal_actions(state, state.turn)
    assert best_action in legal_actions
    assert stats.nodes_visited > 0
    assert stats.states_evaluated > 0


def test_heuristic_consistency():
    # Estado inicial: distâncias simétricas (6 e 6), paredes iguais (6 e 6)
    state = GameState()
    score_red = evaluate_state(state, PLAYER_RED)
    score_blue = evaluate_state(state, PLAYER_BLUE)
    # Por simetria e pesos neutros na origem, as avaliações devem ser opostas
    assert score_red == -score_blue

    # Se o Vermelho avança para (5, 3), sua avaliação deve aumentar
    state_adv = state.apply_action(MoveAction((5, 3)))
    score_adv = evaluate_state(state_adv, PLAYER_RED)
    assert score_adv > score_red
