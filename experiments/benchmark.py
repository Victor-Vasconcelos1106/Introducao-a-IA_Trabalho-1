"""
Experimento de Benchmark Acadêmico para Busca Adversarial.
Compara o desempenho computacional de:
1. Minimax clássico sem poda.
2. Minimax com Poda Alpha-Beta.
3. Minimax com Alpha-Beta e Ordenação de Movimentos.
4. Minimax com Alpha-Beta, Ordenação e Tabela de Transposição.

Métricas coletadas:
- Tempo de execução (s)
- Nós explorados / visitados
- Nós podados
- Profundidade máxima atingida
- Consumo de memória (pico em KB via tracemalloc)
- Taxa de nós por segundo (NPS)
"""

import sys
import os
import time
import csv
import argparse
import tracemalloc
from typing import List, Dict, Any

# Adiciona o diretório raiz ao sys.path para importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.game.state import GameState
from src.ai.minimax import minimax_search
from src.ai.alpha_beta import alpha_beta_search
from src.ai.transposition_table import TranspositionTable
from src.ai.evaluation import evaluate_state, evaluate_simple
from src.utils.constants import PLAYER_RED, WALL_HORIZONTAL, WALL_VERTICAL


def get_test_scenarios() -> List[Dict[str, Any]]:
    """Define cenários representativos de teste para o benchmark."""
    return [
        {
            "name": "Cenário 1 — Abertura Padrão (Tab. Limpo)",
            "state": GameState(),
        },
        {
            "name": "Cenário 2 — Meio-jogo com Barricadas",
            "state": GameState(
                red_pos=(4, 3),
                blue_pos=(2, 3),
                red_walls=4,
                blue_walls=4,
                turn=PLAYER_RED,
                h_walls={(3, 2)},
                v_walls={(2, 4)},
            ),
        },
        {
            "name": "Cenário 3 — Final de Jogo (Disputa Reta)",
            "state": GameState(
                red_pos=(2, 3),
                blue_pos=(4, 3),
                red_walls=1,
                blue_walls=1,
                turn=PLAYER_RED,
                h_walls={(1, 2), (4, 2)},
            ),
        },
    ]


def run_benchmark(
    depth: int = 2,
    output_csv: str = "experiments/benchmark_results.csv",
    use_simple_eval: bool = False,
) -> List[Dict[str, Any]]:
    """Executa a bateria de testes comparativos."""
    scenarios = get_test_scenarios()
    eval_fn = evaluate_simple if use_simple_eval else evaluate_state

    algorithms = [
        {"id": "minimax", "name": "1. Minimax Puro"},
        {"id": "alpha_beta", "name": "2. Alpha-Beta"},
        {"id": "alpha_beta_ordering", "name": "3. Alpha-Beta + Ordenação"},
        {"id": "alpha_beta_all", "name": "4. Alpha-Beta + Ord + TT"},
    ]

    all_results: List[Dict[str, Any]] = []

    print("\n" + "=" * 80)
    print(f" EXPERIMENTO DE BENCHMARK DE BUSCA ADVERSARIAL — PROFUNDIDADE: {depth}")
    print("=" * 80)

    for scen in scenarios:
        scen_name = scen["name"]
        base_state: GameState = scen["state"]
        print(f"\n>> {scen_name}")
        print("-" * 80)
        print(f"{'Algoritmo':<30} | {'Tempo (s)':<10} | {'Nós Vis.':<10} | {'Podas':<8} | {'Pico Mem(KB)':<12} | {'NPS':<8}")
        print("-" * 80)

        for algo in algorithms:
            algo_id = algo["id"]
            algo_name = algo["name"]
            state_copy = base_state.clone()

            tracemalloc.start()
            start_time = time.perf_counter()

            if algo_id == "minimax":
                best_act, score, stats = minimax_search(
                    state_copy,
                    depth=depth,
                    max_player=state_copy.turn,
                    eval_fn=eval_fn,
                )
            elif algo_id == "alpha_beta":
                best_act, score, stats = alpha_beta_search(
                    state_copy,
                    depth=depth,
                    max_player=state_copy.turn,
                    use_ordering=False,
                    use_tt=False,
                    iterative_deepening=False,
                    eval_fn=eval_fn,
                )
            elif algo_id == "alpha_beta_ordering":
                best_act, score, stats = alpha_beta_search(
                    state_copy,
                    depth=depth,
                    max_player=state_copy.turn,
                    use_ordering=True,
                    use_tt=False,
                    iterative_deepening=False,
                    eval_fn=eval_fn,
                )
            elif algo_id == "alpha_beta_all":
                tt = TranspositionTable()
                best_act, score, stats = alpha_beta_search(
                    state_copy,
                    depth=depth,
                    max_player=state_copy.turn,
                    use_ordering=True,
                    use_tt=True,
                    tt=tt,
                    iterative_deepening=False,
                    eval_fn=eval_fn,
                )

            elapsed = time.perf_counter() - start_time
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            peak_kb = round(peak_mem / 1024, 2)
            nps = int(stats.nodes_visited / elapsed) if elapsed > 0 else 0

            print(
                f"{algo_name:<30} | "
                f"{elapsed:<10.4f} | "
                f"{stats.nodes_visited:<10} | "
                f"{stats.nodes_pruned:<8} | "
                f"{peak_kb:<12.2f} | "
                f"{nps:<8}"
            )

            result_entry = {
                "scenario": scen_name,
                "algorithm": algo_name,
                "depth": depth,
                "time_sec": round(elapsed, 5),
                "nodes_visited": stats.nodes_visited,
                "nodes_pruned": stats.nodes_pruned,
                "peak_mem_kb": peak_kb,
                "nps": nps,
                "score": round(score, 2),
                "best_action": str(best_act),
            }
            all_results.append(result_entry)

    # Exportar para CSV
    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        keys = list(all_results[0].keys())
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n[OK] Resultados exportados com sucesso para: {output_csv}")

    print("=" * 80 + "\n")
    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o benchmark de busca adversarial.")
    parser.add_argument("--depth", type=int, default=2, help="Profundidade da busca (padrão: 2)")
    parser.add_argument("--csv", type=str, default="experiments/benchmark_results.csv", help="Caminho do arquivo CSV de saída")
    parser.add_argument("--simple", action="store_true", help="Utilizar heurística elementar")
    args = parser.parse_args()

    run_benchmark(depth=args.depth, output_csv=args.csv, use_simple_eval=args.simple)
