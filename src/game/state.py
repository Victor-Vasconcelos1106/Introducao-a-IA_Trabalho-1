"""
Representação do estado do jogo Barricade AI.
Contém posições dos peões, barricadas no tabuleiro, recursos disponíveis e turno atual.
"""

from typing import Set, Tuple, Optional
from src.utils.constants import (
    BOARD_SIZE,
    PLAYER_RED,
    PLAYER_BLUE,
    PLAYER_NONE,
    START_POS_RED,
    START_POS_BLUE,
    GOAL_ROW_RED,
    GOAL_ROW_BLUE,
    DEFAULT_WALLS_COUNT,
    WALL_HORIZONTAL,
    WALL_VERTICAL,
)
from src.game.actions import MoveAction, WallAction


class GameState:
    """
    Estado imutável / facilmente clonável do jogo Barricade.
    Mantém rastreabilidade completa do tabuleiro e do progresso dos jogadores.
    """

    def __init__(
        self,
        red_pos: Tuple[int, int] = START_POS_RED,
        blue_pos: Tuple[int, int] = START_POS_BLUE,
        red_walls: int = DEFAULT_WALLS_COUNT,
        blue_walls: int = DEFAULT_WALLS_COUNT,
        turn: int = PLAYER_RED,
        h_walls: Optional[Set[Tuple[int, int]]] = None,
        v_walls: Optional[Set[Tuple[int, int]]] = None,
        move_count: int = 0,
    ):
        self.red_pos: Tuple[int, int] = red_pos
        self.blue_pos: Tuple[int, int] = blue_pos
        self.red_walls: int = red_walls
        self.blue_walls: int = blue_walls
        self.turn: int = turn
        self.h_walls: Set[Tuple[int, int]] = set() if h_walls is None else set(h_walls)
        self.v_walls: Set[Tuple[int, int]] = set() if v_walls is None else set(v_walls)
        self.move_count: int = move_count

        self._hash: Optional[int] = None

    def clone(self) -> "GameState":
        """Cria uma cópia rápida e independente do estado atual."""
        cloned = GameState(
            red_pos=self.red_pos,
            blue_pos=self.blue_pos,
            red_walls=self.red_walls,
            blue_walls=self.blue_walls,
            turn=self.turn,
            h_walls=self.h_walls.copy(),
            v_walls=self.v_walls.copy(),
            move_count=self.move_count,
        )
        return cloned

    def get_player_pos(self, player: int) -> Tuple[int, int]:
        """Retorna a posição (linha, coluna) do jogador especificado."""
        return self.red_pos if player == PLAYER_RED else self.blue_pos

    def get_player_walls(self, player: int) -> int:
        """Retorna o número de barricadas restantes do jogador especificado."""
        return self.red_walls if player == PLAYER_RED else self.blue_walls

    @staticmethod
    def get_opponent(player: int) -> int:
        """Retorna o identificador do jogador adversário."""
        return PLAYER_BLUE if player == PLAYER_RED else PLAYER_RED

    def get_goal_row(self, player: int) -> int:
        """Retorna a linha objetivo para o jogador."""
        return GOAL_ROW_RED if player == PLAYER_RED else GOAL_ROW_BLUE

    def is_terminal(self) -> bool:
        """Retorna True se algum jogador atingiu sua linha de vitória."""
        return self.red_pos[0] == GOAL_ROW_RED or self.blue_pos[0] == GOAL_ROW_BLUE

    @property
    def winner(self) -> int:
        """Retorna o vencedor da partida ou PLAYER_NONE se em andamento."""
        if self.red_pos[0] == GOAL_ROW_RED:
            return PLAYER_RED
        if self.blue_pos[0] == GOAL_ROW_BLUE:
            return PLAYER_BLUE
        return PLAYER_NONE

    def apply_action(self, action: MoveAction | WallAction) -> "GameState":
        """
        Aplica uma ação válida e retorna um NOVO estado de jogo com o turno alternado.
        Não valida legalidade internamente (deve ser validada antes via rules).
        """
        next_state = self.clone()
        next_state.move_count += 1

        if action.is_move:
            # Movimento de peão
            if self.turn == PLAYER_RED:
                next_state.red_pos = action.to_pos
            else:
                next_state.blue_pos = action.to_pos
        elif action.is_wall:
            # Posicionamento de barricada
            if action.wall_type == WALL_HORIZONTAL:
                next_state.h_walls.add((action.row, action.col))
            else:
                next_state.v_walls.add((action.row, action.col))

            if self.turn == PLAYER_RED:
                next_state.red_walls -= 1
            else:
                next_state.blue_walls -= 1

        # Alterna o turno
        next_state.turn = self.get_opponent(self.turn)
        return next_state

    def to_hash_key(self) -> Tuple:
        """
        Gera uma chave imutável completa do estado, usada para indexação
        em Tabelas de Transposição (TT) e conjuntos.
        """
        return (
            self.red_pos,
            self.blue_pos,
            self.red_walls,
            self.blue_walls,
            self.turn,
            frozenset(self.h_walls),
            frozenset(self.v_walls),
        )

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self.to_hash_key())
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameState):
            return False
        return (
            self.turn == other.turn
            and self.red_pos == other.red_pos
            and self.blue_pos == other.blue_pos
            and self.red_walls == other.red_walls
            and self.blue_walls == other.blue_walls
            and self.h_walls == other.h_walls
            and self.v_walls == other.v_walls
        )

    def __repr__(self) -> str:
        return (
            f"GameState(turn={self.turn}, red={self.red_pos}[{self.red_walls}], "
            f"blue={self.blue_pos}[{self.blue_walls}], "
            f"walls_h={len(self.h_walls)}, walls_v={len(self.v_walls)})"
        )
