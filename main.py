"""
Ponto de Entrada Principal — Barricade AI
Jogo de estratégia com busca adversarial (Minimax, Alpha-Beta, BFS e Otimizações).

Desenvolvido para trabalho acadêmico de Inteligência Artificial.
"""

import sys
import os

# Adiciona o diretório raiz ao caminho de módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.pygame_app import PygameApp


def main():
    """Inicializa e executa a aplicação gráfica."""
    print("Iniciando Barricade AI...")
    app = PygameApp()
    app.run()


if __name__ == "__main__":
    main()
