"""
Regras do jogo Barricade AI:
- Geração de movimentos válidos de peões (incluindo saltos retos e diagonais).
- Posicionamento e validação de barricadas (colisão física e garantia de caminho via BFS).
- Verificação de legalidade de ações e estados terminais.
"""

from typing import List, Optional, Set, Tuple
from src.utils.constants import (
    BOARD_SIZE,
    PLAYER_RED,
    PLAYER_BLUE,
    GOAL_ROW_RED,
    GOAL_ROW_BLUE,
    WALL_HORIZONTAL,
    WALL_VERTICAL,
)
from src.game.actions import MoveAction, WallAction
from src.game.state import GameState
from src.game.board import is_in_bounds, is_valid_wall_coord, is_passage_blocked, has_wall_collision
from src.game.pathfinding import has_path_to_goal, get_shortest_path

ORTHOGONAL_STEPS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def get_legal_pawn_moves(state: GameState, player: Optional[int] = None) -> List[MoveAction]:
    """
    Retorna todos os movimentos válidos de peão para o jogador especificado (ou jogador do turno).
    Implementa as regras completas de movimento ortogonal e saltos sobre o adversário:
    1. Movimento simples de 1 casa para cima, baixo, esquerda ou direita se livre e sem barricada.
    2. Salto reto: se o adversário estiver adjacente e a casa atrás dele for válida e sem barricada.
    3. Salto diagonal: se o salto reto for bloqueado por barricada ou limite do tabuleiro,
       o jogador pode saltar para as casas laterais do adversário, se acessíveis.
    """
    if player is None:
        player = state.turn

    my_pos = state.get_player_pos(player)
    opp_player = state.get_opponent(player)
    opp_pos = state.get_player_pos(opp_player)

    moves: List[MoveAction] = []
    r, c = my_pos
    opp_r, opp_c = opp_pos

    for dr, dc in ORTHOGONAL_STEPS:
        nr, nc = r + dr, c + dc

        # Deve estar dentro do tabuleiro
        if not is_in_bounds(nr, nc):
            continue

        # Passagem entre a posição atual e o vizinho não pode estar bloqueada
        if is_passage_blocked(r, c, nr, nc, state.h_walls, state.v_walls):
            continue

        # Casa vizinha vazia: movimento normal de 1 casa
        if (nr, nc) != opp_pos:
            moves.append(MoveAction((nr, nc)))
            continue

        # Adversário adjacente nesta direção: aplicar regra de saltos
        straight_r = opp_r + dr
        straight_c = opp_c + dc

        straight_possible = (
            is_in_bounds(straight_r, straight_c)
            and not is_passage_blocked(opp_r, opp_c, straight_r, straight_c, state.h_walls, state.v_walls)
        )

        if straight_possible:
            # Salto reto é obrigatório se estiver desobstruído (diagonal não é permitida)
            moves.append(MoveAction((straight_r, straight_c)))
        else:
            # Salto reto impedido por barricada ou borda do tabuleiro:
            # Permitir saltos diagonais para as laterais do adversário
            if dr != 0:
                # Movimento era vertical -> laterais são horizontais
                lateral_dirs = [(0, -1), (0, 1)]
            else:
                # Movimento era horizontal -> laterais são verticais
                lateral_dirs = [(-1, 0), (1, 0)]

            for ldr, ldc in lateral_dirs:
                diag_r = opp_r + ldr
                diag_c = opp_c + ldc

                if is_in_bounds(diag_r, diag_c):
                    if not is_passage_blocked(opp_r, opp_c, diag_r, diag_c, state.h_walls, state.v_walls):
                        moves.append(MoveAction((diag_r, diag_c)))

    return moves


def _wall_blocks_path(wall_type: str, wr: int, wc: int, path: List[Tuple[int, int]]) -> bool:
    """
    Verifica rapidamente se uma barricada hipotética (wall_type em wr, wc)
    bloqueia alguma aresta do caminho fornecido.
    """
    if len(path) < 2:
        return False

    temp_h: Set[Tuple[int, int]] = {(wr, wc)} if wall_type == WALL_HORIZONTAL else set()
    temp_v: Set[Tuple[int, int]] = {(wr, wc)} if wall_type == WALL_VERTICAL else set()

    for i in range(len(path) - 1):
        c1 = path[i]
        c2 = path[i + 1]
        if is_passage_blocked(c1[0], c1[1], c2[0], c2[1], temp_h, temp_v):
            return True

    return False


def is_valid_wall_placement(state: GameState, action: WallAction, player: Optional[int] = None) -> bool:
    """
    Valida se o posicionamento de uma barricada é legal:
    - O jogador deve ter barricadas restantes.
    - As coordenadas da barricada devem estar dentro dos limites (0 a BOARD_SIZE - 2).
    - Não pode cruzar nem sobrepor outras barricadas.
    - Não pode bloquear completamente o caminho de nenhum dos jogadores até sua meta.
    """
    if player is None:
        player = state.turn

    # Quantidade de barricadas restantes
    if state.get_player_walls(player) <= 0:
        return False

    # Limites físicos
    if not is_valid_wall_coord(action.row, action.col):
        return False

    # Conflito de sobreposição ou cruzamento
    if has_wall_collision(action.wall_type, action.row, action.col, state.h_walls, state.v_walls):
        return False

    # Criação temporária das barricadas para teste de caminho
    temp_h = state.h_walls.copy()
    temp_v = state.v_walls.copy()
    if action.wall_type == WALL_HORIZONTAL:
        temp_h.add((action.row, action.col))
    else:
        temp_v.add((action.row, action.col))

    # Ambos os jogadores devem manter pelo menos um caminho válido até suas metas
    if not has_path_to_goal(state.red_pos, GOAL_ROW_RED, temp_h, temp_v):
        return False

    if not has_path_to_goal(state.blue_pos, GOAL_ROW_BLUE, temp_h, temp_v):
        return False

    return True


def get_legal_wall_moves(state: GameState, player: Optional[int] = None) -> List[WallAction]:
    """
    Gera todas as ações válidas de colocação de barricadas para o jogador.
    Utiliza poda por caminho conhecido para acelerar drasticamente a validação BFS.
    """
    if player is None:
        player = state.turn

    if state.get_player_walls(player) <= 0:
        return []

    # Obter caminhos atuais conhecidos de ambos os jogadores
    path_red = get_shortest_path(state.red_pos, GOAL_ROW_RED, state.h_walls, state.v_walls)
    path_blue = get_shortest_path(state.blue_pos, GOAL_ROW_BLUE, state.h_walls, state.v_walls)

    if path_red is None or path_blue is None:
        return []

    legal_walls: List[WallAction] = []
    wall_limit = BOARD_SIZE - 1

    for r in range(wall_limit):
        for c in range(wall_limit):
            for wall_type in (WALL_HORIZONTAL, WALL_VERTICAL):
                # 1. Checagem rápida de colisão física
                if has_wall_collision(wall_type, r, c, state.h_walls, state.v_walls):
                    continue

                # 2. Verificação otimizada de caminho:
                # Se a barricada não bloqueia o caminho conhecido do Vermelho, ele continua válido.
                red_path_intact = not _wall_blocks_path(wall_type, r, c, path_red)
                # Se a barricada não bloqueia o caminho conhecido do Azul, ele continua válido.
                blue_path_intact = not _wall_blocks_path(wall_type, r, c, path_blue)

                if red_path_intact and blue_path_intact:
                    # Nenhum caminho conhecido foi afetado -> 100% garantido que ambos têm caminho!
                    legal_walls.append(WallAction(wall_type, r, c))
                    continue

                # Caso tenha bloqueado o caminho conhecido de alguém, executar BFS com a barricada simulada
                temp_h = state.h_walls.copy()
                temp_v = state.v_walls.copy()
                if wall_type == WALL_HORIZONTAL:
                    temp_h.add((r, c))
                else:
                    temp_v.add((r, c))

                if not red_path_intact:
                    if not has_path_to_goal(state.red_pos, GOAL_ROW_RED, temp_h, temp_v):
                        continue

                if not blue_path_intact:
                    if not has_path_to_goal(state.blue_pos, GOAL_ROW_BLUE, temp_h, temp_v):
                        continue

                legal_walls.append(WallAction(wall_type, r, c))

    return legal_walls


def get_legal_actions(state: GameState, player: Optional[int] = None) -> List[MoveAction | WallAction]:
    """Retorna todas as ações legais (movimentações de peão e barricadas) para o jogador."""
    if state.is_terminal():
        return []

    pawn_moves = get_legal_pawn_moves(state, player)
    wall_moves = get_legal_wall_moves(state, player)
    return pawn_moves + wall_moves


def is_legal_action(state: GameState, action: MoveAction | WallAction, player: Optional[int] = None) -> bool:
    """Verifica se uma ação específica é legal no estado atual."""
    if action.is_move:
        legal_pawn_moves = get_legal_pawn_moves(state, player)
        return action in legal_pawn_moves
    elif action.is_wall:
        return is_valid_wall_placement(state, action, player)
    return False
