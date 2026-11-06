"""Módulo de regras, estado e tabuleiro de Barricade AI."""

from src.game.state import GameState
from src.game.actions import MoveAction, WallAction
from src.game.rules import (
    get_legal_pawn_moves,
    get_legal_wall_moves,
    get_legal_actions,
    is_valid_wall_placement,
    is_legal_action,
)
from src.game.pathfinding import (
    has_path_to_goal,
    get_shortest_distance,
    get_shortest_path,
    get_all_distances_to_goal_row,
)

__all__ = [
    "GameState",
    "MoveAction",
    "WallAction",
    "get_legal_pawn_moves",
    "get_legal_wall_moves",
    "get_legal_actions",
    "is_valid_wall_placement",
    "is_legal_action",
    "has_path_to_goal",
    "get_shortest_distance",
    "get_shortest_path",
    "get_all_distances_to_goal_row",
]
