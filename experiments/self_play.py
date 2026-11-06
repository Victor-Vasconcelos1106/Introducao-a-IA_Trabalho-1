"""
Experimento de Partidas Bot vs Bot (Self-Play).
Permite confrontar duas configurações distintas de inteligência artificial
e registrar métricas detalhadas de desempenho e resultado em formato CSV.
"""

import sys
import os
import time
import csv
import random
import argparse
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.game.state import GameState
from src.ai.minimax import minimax_search
from src.ai.alpha_beta import alpha_beta_search
from src.ai.transposition_table import TranspositionTable
from src.ai.evaluation import evaluate_state, evaluate_simple
from src.ai.search_stats import SearchStats
from src.utils.constants import PLAYER_RED, PLAYER_BLUE, PLAYER_NAMES


class BotConfig:
    """Configuração dos parâmetros de busca de um agente artificial."""

    def __init__(
        self,
        name: str,
        depth: int = 2,
        use_alpha_beta: bool = True,
        use_ordering: bool = True,
        use_tt: bool = True,
        time_limit: Optional[float] = 2.0,
        use_simple_eval: bool = False,
    ):
        self.name = name
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.use_ordering = use_ordering
        self.use_tt = use_tt
        self.time_limit = time_limit
        self.use_simple_eval = use_simple_eval
        self.tt: Optional[TranspositionTable] = TranspositionTable() if use_tt else None

    def decide_move(self, state: GameState) -> Tuple[Any, float, SearchStats]:
        eval_fn = evaluate_simple if self.use_simple_eval else evaluate_state
        stats = SearchStats()

        if not self.use_alpha_beta:
            action, score, stats = minimax_search(
                state=state,
                depth=self.depth,
                max_player=state.turn,
                eval_fn=eval_fn,
                stats=stats,
            )
        else:
            action, score, stats = alpha_beta_search(
                state=state,
                depth=self.depth,
                max_player=state.turn,
                use_ordering=self.use_ordering,
                use_tt=self.use_tt,
                tt=self.tt,
                iterative_deepening=True,
                time_limit=self.time_limit,
                eval_fn=eval_fn,
                stats=stats,
            )

        return action, score, stats

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "depth": self.depth,
            "alpha_beta": self.use_alpha_beta,
            "ordering": self.use_ordering,
            "tt": self.use_tt,
            "time_limit": self.time_limit,
            "simple_eval": self.use_simple_eval,
        }


def play_game(
    bot_red: BotConfig,
    bot_blue: BotConfig,
    initial_walls: int = 6,
    max_turns: int = 150,
) -> Dict[str, Any]:
    """Simula uma partida completa entre dois bots."""
    state = GameState(red_walls=initial_walls, blue_walls=initial_walls)
    game_start = time.perf_counter()

    red_total_nodes = 0
    blue_total_nodes = 0
    red_total_time = 0.0
    blue_total_time = 0.0
    turn_count = 0

    while not state.is_terminal() and turn_count < max_turns:
        turn_count += 1
        current_bot = bot_red if state.turn == PLAYER_RED else bot_blue

        action, score, stats = current_bot.decide_move(state)

        if state.turn == PLAYER_RED:
            red_total_nodes += stats.nodes_visited
            red_total_time += stats.execution_time
        else:
            blue_total_nodes += stats.nodes_visited
            blue_total_time += stats.execution_time

        if action is None:
            # Não foi encontrada ação válida (empate ou bloqueio anômalo)
            break

        state = state.apply_action(action)

    total_game_time = time.perf_counter() - game_start
    winner = state.winner
    winner_name = PLAYER_NAMES.get(winner, "Empate/Limite de Turnos")

    return {
        "winner": winner_name,
        "winner_player_id": winner,
        "turns": turn_count,
        "duration_sec": round(total_game_time, 3),
        "red_bot": bot_red.name,
        "blue_bot": bot_blue.name,
        "red_nodes_total": red_total_nodes,
        "blue_nodes_total": blue_total_nodes,
        "red_time_total": round(red_total_time, 3),
        "blue_time_total": round(blue_total_time, 3),
        "red_avg_time_turn": round(red_total_time / max(1, (turn_count + 1) // 2), 4),
        "blue_avg_time_turn": round(blue_total_time / max(1, turn_count // 2), 4),
        "final_red_pos": str(state.red_pos),
        "final_blue_pos": str(state.blue_pos),
        "final_walls_h": len(state.h_walls),
        "final_walls_v": len(state.v_walls),
    }


def run_self_play_series(
    games: int = 5,
    red_depth: int = 2,
    blue_depth: int = 2,
    output_csv: str = "experiments/self_play_results.csv",
    seed: int = 42,
) -> None:
    """Executa uma série de partidas para análise estatística e grava no CSV."""
    random.seed(seed)

    bot_red = BotConfig(
        name=f"BotRed_D{red_depth}",
        depth=red_depth,
        use_alpha_beta=True,
        use_ordering=True,
        use_tt=True,
        time_limit=2.0,
    )

    bot_blue = BotConfig(
        name=f"BotBlue_D{blue_depth}",
        depth=blue_depth,
        use_alpha_beta=True,
        use_ordering=False,  # Para comparar bot com ordenação vs sem ordenação
        use_tt=True,
        time_limit=2.0,
    )

    print("\n" + "=" * 80)
    print(f" EXPERIMENTO SELF-PLAY: {bot_red.name} (Vermelho) vs {bot_blue.name} (Azul)")
    print(f" Total de Partidas: {games} | Semente Aleatória: {seed}")
    print("=" * 80)

    results: List[Dict[str, Any]] = []
    red_wins = 0
    blue_wins = 0
    draws = 0

    for g in range(1, games + 1):
        # Limpar TT para cada partida independente
        if bot_red.tt:
            bot_red.tt.clear()
        if bot_blue.tt:
            bot_blue.tt.clear()

        print(f"\n[Partida {g}/{games}] Iniciando...")
        match_data = play_game(bot_red, bot_blue)
        match_data["game_index"] = g
        match_data["random_seed"] = seed
        results.append(match_data)

        if match_data["winner_player_id"] == PLAYER_RED:
            red_wins += 1
        elif match_data["winner_player_id"] == PLAYER_BLUE:
            blue_wins += 1
        else:
            draws += 1

        print(
            f"-> Vencedor: {match_data['winner']} | "
            f"Turnos: {match_data['turns']} | "
            f"Duração: {match_data['duration_sec']}s | "
            f"Nós Red: {match_data['red_nodes_total']} | "
            f"Nós Blue: {match_data['blue_nodes_total']}"
        )

    # Exporta para CSV
    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        keys = ["game_index"] + [k for k in results[0].keys() if k != "game_index"]
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"\n[OK] Resultados gravados em: {output_csv}")

    print("\n" + "-" * 40)
    print(" RESUMO DA SÉRIE")
    print("-" * 40)
    print(f" Vitórias {bot_red.name}: {red_wins} ({red_wins / games * 100:.1f}%)")
    print(f" Vitórias {bot_blue.name}: {blue_wins} ({blue_wins / games * 100:.1f}%)")
    print(f" Empates: {draws}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa séries de partidas Bot vs Bot.")
    parser.add_argument("--games", type=int, default=2, help="Número de partidas a simular (padrão: 2)")
    parser.add_argument("--red-depth", type=int, default=2, help="Profundidade do Bot Vermelho")
    parser.add_argument("--blue-depth", type=int, default=2, help="Profundidade do Bot Azul")
    parser.add_argument("--seed", type=int, default=42, help="Semente aleatória para reprodutibilidade")
    parser.add_argument("--csv", type=str, default="experiments/self_play_results.csv", help="Caminho do CSV")
    args = parser.parse_args()

    run_self_play_series(
        games=args.games,
        red_depth=args.red_depth,
        blue_depth=args.blue_depth,
        output_csv=args.csv,
        seed=args.seed,
    )
