"""
Constantes globais do jogo Barricade AI.
Define configurações de tabuleiro, regras, jogadores, avaliação e interface gráfica.
"""

# Configurações do Tabuleiro
BOARD_SIZE = 7

# Identificadores de Jogadores
PLAYER_NONE = 0
PLAYER_RED = 1    # Começa embaixo (linha 6, coluna 3) e deve atingir a linha 0
PLAYER_BLUE = 2   # Começa em cima (linha 0, coluna 3) e deve atingir a linha 6

PLAYER_NAMES = {
    PLAYER_RED: "Vermelho",
    PLAYER_BLUE: "Azul"
}

# Posições Iniciais
START_POS_RED = (6, 3)
START_POS_BLUE = (0, 3)

# Linhas de Vitória
GOAL_ROW_RED = 0
GOAL_ROW_BLUE = 6

# Recursos Iniciais
DEFAULT_WALLS_COUNT = 6

# Orientações de Barricadas
WALL_HORIZONTAL = 'H'
WALL_VERTICAL = 'V'

# Modos de Jogo
MODE_P_VS_BOT = "Player_vs_Bot"
MODE_BOT_VS_BOT = "Bot_vs_Bot"
MODE_P_VS_P = "Player_vs_Player"

# Configurações Padrão de IA
DEFAULT_SEARCH_DEPTH = 3
DEFAULT_TIME_LIMIT = 3.0  # segundos por decisão
DEFAULT_USE_ALPHA_BETA = True
DEFAULT_USE_TT = True
DEFAULT_USE_ORDERING = True

# Pesos da Função Heurística (configuráveis para experimentos acadêmicos)
EVAL_WEIGHTS = {
    "distance": 100.0,       # Peso para (dist_oponente - dist_ia)
    "walls": 15.0,          # Peso para (paredes_ia - paredes_oponente)
    "mobility": 5.0,        # Peso para opções de movimento imediatas
    "goal_advance": 10.0,   # Incentivo posicional ao avanço
}

WIN_SCORE = 100000
LOSS_SCORE = -100000

# Cores da Interface Gráfica (RGB)
COLOR_BG = (22, 27, 34)              # Fundo escuro moderno
COLOR_PANEL_BG = (33, 38, 45)        # Fundo dos painéis laterais
COLOR_PANEL_BORDER = (48, 54, 61)    # Borda dos painéis
COLOR_BOARD_BG = (13, 17, 23)        # Fundo do tabuleiro
COLOR_CELL = (40, 46, 56)            # Casas do tabuleiro
COLOR_CELL_HOVER = (60, 68, 82)      # Casa ao passar o mouse
COLOR_VALID_MOVE = (46, 160, 67, 180)# Verde translúcido para movimentos válidos
COLOR_VALID_MOVE_BORDER = (56, 190, 80)

COLOR_RED = (235, 69, 95)            # Peão Vermelho vibrante
COLOR_RED_GLOW = (255, 99, 125)
COLOR_BLUE = (43, 150, 246)          # Peão Azul vibrante
COLOR_BLUE_GLOW = (80, 180, 255)

COLOR_WALL = (220, 160, 40)          # Barricada colocada (âmbar)
COLOR_WALL_PREVIEW_VALID = (46, 204, 113, 180) # Verde preview
COLOR_WALL_PREVIEW_INVALID = (231, 76, 60, 180)# Vermelho preview

COLOR_TEXT = (240, 246, 252)         # Texto principal
COLOR_TEXT_MUTED = (139, 148, 158)   # Texto secundário
COLOR_ACCENT = (88, 166, 255)        # Destaque ciano/azul

COLOR_BUTTON = (50, 56, 66)
COLOR_BUTTON_HOVER = (68, 76, 90)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_SUCCESS = (46, 160, 67)
COLOR_DANGER = (218, 54, 51)
COLOR_WARNING = (210, 153, 34)

# Dimensões da Janela
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750
FPS = 60
