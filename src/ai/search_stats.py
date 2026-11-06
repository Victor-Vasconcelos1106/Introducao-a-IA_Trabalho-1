"""
Estrutura para registro e análise de estatísticas de busca da IA.
Usada para comparar algoritmos em benchmarks acadêmicos e exibir métricas na interface.
"""

import time
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SearchStats:
    """Métricas coletadas durante a busca adversarial."""
    nodes_visited: int = 0
    nodes_pruned: int = 0
    max_depth_reached: int = 0
    execution_time: float = 0.0
    states_evaluated: int = 0
    tt_hits: int = 0
    tt_stores: int = 0

    def reset(self) -> None:
        """Reinicia todas as métricas."""
        self.nodes_visited = 0
        self.nodes_pruned = 0
        self.max_depth_reached = 0
        self.execution_time = 0.0
        self.states_evaluated = 0
        self.tt_hits = 0
        self.tt_stores = 0

    def to_dict(self) -> Dict[str, Any]:
        """Converte as estatísticas para dicionário legível."""
        return {
            "nodes_visited": self.nodes_visited,
            "nodes_pruned": self.nodes_pruned,
            "max_depth_reached": self.max_depth_reached,
            "execution_time_sec": round(self.execution_time, 4),
            "states_evaluated": self.states_evaluated,
            "tt_hits": self.tt_hits,
            "tt_stores": self.tt_stores,
            "nps": int(self.nodes_visited / self.execution_time) if self.execution_time > 0 else 0,
        }

    def summary_str(self) -> str:
        """Retorna resumo em texto formatado para exibição."""
        nps = int(self.nodes_visited / self.execution_time) if self.execution_time > 0 else 0
        return (
            f"Profundidade: {self.max_depth_reached} | "
            f"Nós: {self.nodes_visited} | "
            f"Podas: {self.nodes_pruned} | "
            f"Tempo: {self.execution_time:.3f}s | "
            f"Nós/s: {nps} | "
            f"TT Hits: {self.tt_hits}"
        )
