"""
Testes unitários para regras do jogo, movimentação de peões, saltos e colocação de barricadas.
"""

import pytest
from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.game.rules import (
    get_legal_pawn_moves,
    get_legal_wall_moves,
    is_valid_wall_placement,
    is_legal_action,
)
from src.utils.constants import (
    PLAYER_RED,
    PLAYER_BLUE,
    WALL_HORIZONTAL,
    WALL_VERTICAL,
    START_POS_RED,
    START_POS_BLUE,
)


def test_initial_state_and_moves():
    state = GameState()
    assert state.red_pos == (6, 3)
    assert state.blue_pos == (0, 3)
    assert state.red_walls == 6
    assert state.blue_walls == 6
    assert state.turn == PLAYER_RED
    assert not state.is_terminal()

    # Movimentos iniciais do Vermelho a partir de (6, 3):
    # Cima: (5, 3), Esquerda: (6, 2), Direita: (6, 4). Baixo (7, 3) está fora do tabuleiro.
    moves = get_legal_pawn_moves(state, PLAYER_RED)
    targets = {m.to_pos for m in moves}
    assert targets == {(5, 3), (6, 2), (6, 4)}


def test_straight_jump_over_opponent():
    # Colocar Vermelho em (3, 3) e Azul em (2, 3)
    state = GameState(red_pos=(3, 3), blue_pos=(2, 3), turn=PLAYER_RED)

    moves = get_legal_pawn_moves(state, PLAYER_RED)
    targets = {m.to_pos for m in moves}

    # Deve incluir o salto reto para (1, 3)
    assert (1, 3) in targets
    # Outros movimentos normais: (3, 2), (3, 4), (4, 3)
    assert (3, 2) in targets
    assert (3, 4) in targets
    assert (4, 3) in targets
    # Salto diagonal NÃO deve ser permitido se o reto estiver livre
    assert (2, 2) not in targets
    assert (2, 4) not in targets


def test_diagonal_jump_when_straight_is_blocked_by_wall():
    # Vermelho em (3, 3), Azul em (2, 3)
    # Barricada H em (1, 2) bloqueia a passagem (1, 3) <-> (2, 3)
    state = GameState(
        red_pos=(3, 3),
        blue_pos=(2, 3),
        turn=PLAYER_RED,
        h_walls={(1, 2)},
    )

    moves = get_legal_pawn_moves(state, PLAYER_RED)
    targets = {m.to_pos for m in moves}

    # O salto reto para (1, 3) está bloqueado!
    assert (1, 3) not in targets
    # Saltos diagonais laterais devem estar presentes: (2, 2) e (2, 4)
    assert (2, 2) in targets
    assert (2, 4) in targets


def test_diagonal_jump_when_straight_is_blocked_by_board_boundary():
    # Azul em (0, 3), Vermelho em (1, 3), turno do Vermelho
    # Salto reto seria (-1, 3), fora do tabuleiro
    state = GameState(red_pos=(1, 3), blue_pos=(0, 3), turn=PLAYER_RED)

    moves = get_legal_pawn_moves(state, PLAYER_RED)
    targets = {m.to_pos for m in moves}

    # Deve conter as diagonais (0, 2) e (0, 4)
    assert (0, 2) in targets
    assert (0, 4) in targets


def test_wall_placement_cannot_completely_block():
    # Configurar cenário onde o peão Vermelho está cercado em 3 lados
    # e uma última barricada fecharia seu caminho
    state = GameState(
        red_pos=(6, 3),
        blue_pos=(0, 3),
        turn=PLAYER_BLUE,
        h_walls={(5, 2)},  # bloqueia cima
        v_walls={(5, 2)},  # bloqueia esquerda
    )
    # A barricada V(5, 3) fecharia a direita de (6, 3), encurralando totalmente
    blocking_wall = WallAction(WALL_VERTICAL, 5, 3)
    assert is_valid_wall_placement(state, blocking_wall, PLAYER_BLUE) is False

    # Outra barricada que não fecha o caminho deve ser válida
    safe_wall = WallAction(WALL_VERTICAL, 2, 2)
    assert is_valid_wall_placement(state, safe_wall, PLAYER_BLUE) is True


def test_zero_walls_remaining():
    state = GameState(red_pos=(6, 3), blue_pos=(0, 3), red_walls=0, turn=PLAYER_RED)
    wall_action = WallAction(WALL_HORIZONTAL, 3, 3)
    assert is_valid_wall_placement(state, wall_action, PLAYER_RED) is False
    assert len(get_legal_wall_moves(state, PLAYER_RED)) == 0


def test_apply_action_and_turn_alternation():
    state = GameState()
    # Jogador Vermelho move para (5, 3)
    next_state = state.apply_action(MoveAction((5, 3)))
    assert next_state.red_pos == (5, 3)
    assert next_state.turn == PLAYER_BLUE
    assert next_state.move_count == 1

    # Jogador Azul coloca barricada H em (2, 2)
    wall_act = WallAction(WALL_HORIZONTAL, 2, 2)
    next_state2 = next_state.apply_action(wall_act)
    assert (2, 2) in next_state2.h_walls
    assert next_state2.blue_walls == 5
    assert next_state2.turn == PLAYER_RED


def test_terminal_state_winner():
    # Vermelho chega à linha 0
    state_red_win = GameState(red_pos=(0, 2), blue_pos=(3, 3))
    assert state_red_win.is_terminal()
    assert state_red_win.winner == PLAYER_RED

    # Azul chega à linha 6
    state_blue_win = GameState(red_pos=(4, 3), blue_pos=(6, 1))
    assert state_blue_win.is_terminal()
    assert state_blue_win.winner == PLAYER_BLUE
