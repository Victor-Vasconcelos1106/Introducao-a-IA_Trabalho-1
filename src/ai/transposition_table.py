"""
Tabela de Transposição para busca adversarial.
Armazena avaliações de estados visitados para evitar trabalho redundante
e guiar a ordenação de movimentos em profundidades sucessivas.
"""

from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from src.game.actions import MoveAction, WallAction

# Tipos de limites armazenados na tabela
TT_EXACT = 0       # Valor exato do Minimax
TT_LOWERBOUND = 1  # Limite inferior (corte beta / fail-high: valor >= value)
TT_UPPERBOUND = 2  # Limite superior (falha baixa: todos nós <= alpha: valor <= value)


@dataclass
class TTEntry:
    """Entrada da Tabela de Transposição."""
    depth: int
    value: float
    flag: int
    best_move: Optional[MoveAction | WallAction]


class TranspositionTable:
    """
    Armazenamento em memória com chave hash do GameState.
    Permite substituição quando a nova busca atinge profundidade maior ou igual.
    """

    def __init__(self, max_entries: int = 500_000):
        self.table: Dict[Tuple, TTEntry] = {}
        self.max_entries: int = max_entries

    def clear(self) -> None:
        """Limpa todo o conteúdo da tabela."""
        self.table.clear()

    def size(self) -> int:
        """Retorna o número de estados armazenados."""
        return len(self.table)

    def lookup(self, key: Tuple) -> Optional[TTEntry]:
        """Recupera uma entrada pelo hash do estado, se existir."""
        return self.table.get(key)

    def get_best_move(self, key: Tuple) -> Optional[MoveAction | WallAction]:
        """Retorna a melhor ação memorizada para o estado, se disponível."""
        entry = self.table.get(key)
        return entry.best_move if entry else None

    def store(
        self,
        key: Tuple,
        depth: int,
        value: float,
        flag: int,
        best_move: Optional[MoveAction | WallAction] = None,
    ) -> None:
        """
        Armazena ou atualiza uma entrada na tabela.
        Substitui entradas anteriores se a nova profundidade for maior ou igual.
        """
        existing = self.table.get(key)
        if existing is None or depth >= existing.depth:
            # Controle de tamanho para evitar consumo excessivo de memória
            if len(self.table) >= self.max_entries and existing is None:
                # Remove aproximadamente 10% mais antigos se atingir o limite
                keys_to_remove = list(self.table.keys())[: self.max_entries // 10]
                for k in keys_to_remove:
                    self.table.pop(k, None)

            self.table[key] = TTEntry(
                depth=depth,
                value=value,
                flag=flag,
                best_move=best_move if best_move is not None else (existing.best_move if existing else None),
            )
