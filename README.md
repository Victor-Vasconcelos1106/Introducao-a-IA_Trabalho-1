# Barricade AI — Jogo com Busca Adversarial

Projeto de inteligência artificial aplicada a jogos de estratégia em tabuleiro, inspirado na mecânica de **Barricade.gg** / **Quoridor**. Desenvolvido em **Python** e **Pygame**, este projeto foi construído para fins acadêmicos na disciplina de Inteligência Artificial, priorizando rigor algorítmico, modularidade, documentação e análise empírica do desempenho de algoritmos de busca adversarial.

---

## Sumário

1. [Objetivo Acadêmico](#1-objetivo-acadêmico)
2. [Regras do Jogo](#2-regras-do-jogo)
3. [Tecnologias Utilizadas](#3-tecnologias-utilizadas)
4. [Instalação e Execução](#4-instalação-e-execução)
5. [Modos de Jogo](#5-modos-de-jogo)
6. [Fundamentos Teóricos da Inteligência Artificial](#6-fundamentos-teóricos-da-inteligência-artificial)
   - [Minimax Clássico](#61-minimax-clássico)
   - [Poda Alpha-Beta](#62-poda-alpha-beta)
   - [Função Heurística Ponderada](#63-função-heurística-ponderada)
   - [Busca em Largura (BFS)](#64-busca-em-largura-bfs)
   - [Tabela de Transposição (TT)](#65-tabela-de-transposição-tt)
   - [Ordenação de Movimentos (Move Ordering)](#66-ordenação-de-movimentos-move-ordering)
   - [Aprofundamento Iterativo (Iterative Deepening) e Limite de Tempo](#67-aprofundamento-iterativo-e-tempo-limite)
7. [Experimentos Acadêmicos](#7-experimentos-acadêmicos)
   - [Benchmark de Desempenho](#71-benchmark-de-desempenho)
   - [Partidas Bot vs Bot (Self-Play)](#72-partidas-bot-vs-bot-self-play)
8. [Estrutura do Projeto](#8-estrutura-do-projeto)
9. [Testes Automatizados](#9-testes-automatizados)

---

## 1. Objetivo Acadêmico

O projeto tem como objetivo demonstrar, na prática e de forma verificável, os princípios da tomada de decisão em jogos de soma zero e informação perfeita. Toda a lógica de busca adversarial foi implementada puramente em Python (sem frameworks externos de IA, LLMs ou caixas-pretas), permitindo:

- Observar a explosão combinatória do Minimax puro.
- Quantificar a redução drástica do espaço de busca obtida pela Poda Alpha-Beta.
- Avaliar o impacto da ordenação heurística de nós na frequência de cortes $\beta$.
- Analisar os ganhos de reutilização proporcionados pela Tabela de Transposição.
- Conduzir partidas automatizadas entre configurações distintas de IA para estudo comparativo.

---

## 2. Regras do Jogo

O jogo é disputado em um tabuleiro de **$7 \times 7$ casas** entre dois jogadores: **Vermelho** e **Azul**.

### 2.1. Posições e Objetivos
- **Jogador Vermelho**: Inicia na casa central inferior `(6, 3)` e vence ao alcançar qualquer casa da primeira linha (`linha 0`).
- **Jogador Azul**: Inicia na casa central superior `(0, 3)` e vence ao alcançar qualquer casa da última linha (`linha 6`).
- **Recursos**: Cada jogador inicia com **6 barricadas** (configurável de 0 a 10).

### 2.2. Ações por Turno
Em sua vez, o jogador realiza obrigatoriamente uma de duas ações:
1. **Mover o peão**: uma casa ortogonalmente (cima, baixo, esquerda ou direita).
2. **Posicionar uma barricada**: entre passagens de casas.

### 2.3. Regras Especiais de Salto
- **Salto Reto**: Quando os peões estiverem em casas adjacentes e o jogador da vez desejar avançar na direção do adversário, ele pode saltar por cima deste se a casa imediatamente atrás do oponente estiver desobstruída (dentro dos limites e sem barricada).
- **Salto Diagonal**: Caso o salto reto esteja bloqueado por uma barricada ou pelo limite do tabuleiro, o jogador da vez pode realizar um salto diagonal para qualquer uma das casas laterais acessíveis adjacentes ao adversário.

### 2.4. Posicionamento de Barricadas
- Cada barricada possui comprimento correspondente a **duas passagens entre casas** (orientação Horizontal ou Vertical).
- Não é permitido cruzar barricadas perpendicularmente na mesma interseção central.
- Não é permitida a sobreposição total ou parcial com barricadas paralelas.
- **Regra Fundamental de Conectividade**: É estritamente proibido bloquear completamente o caminho de qualquer jogador até sua linha de chegada. Cada posicionamento é validado por algoritmo BFS antes de ser aceito.
- Cada colocação consome 1 unidade do estoque de barricadas do jogador.

---

## 3. Tecnologias Utilizadas

- **Linguagem**: Python 3.10+ (compatível com 3.12)
- **Interface Gráfica**: Pygame 2.5+
- **Testes e Qualidade**: Pytest 8.0+
- **Concorrência**: Módulo `threading` nativo do Python (para buscas assíncronas sem congelamento da interface)
- **Métricas e Telemetria**: Módulos `time` e `tracemalloc` nativos

---

## 4. Instalação e Execução

### Pré-requisitos
Certifique-se de possuir o Python instalado no sistema.

### Passo 1: Clonar ou Navegar até a Pasta do Projeto
```bash
cd "Trabalho Intro a IA"
```

### Passo 2: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 3: Executar o Jogo
```bash
python main.py
```

---

## 5. Modos de Jogo

Ao iniciar a aplicação, a tela principal oferece três modalidades:

1. **Jogador contra Bot (Humano vs IA)**:
   - O jogador humano controla as peças vermelhas via cliques no tabuleiro.
   - O bot controla as peças azuis, calculando suas decisões em uma thread separada.
   - Atalhos disponíveis: `M` para movimentação de peão, `H` para barricada horizontal, `V` para barricada vertical, `Esc` para cancelar.

2. **Bot contra Bot (Ambiente de Demonstração e Experimentos)**:
   - Dois agentes disputam a partida em tempo real.
   - Controles na interface: **Pausar/Retomar**, **Avançar 1 Jogada** (passo a passo para análise detalhada) e controle de velocidade.
   - Painel lateral exibe estatísticas em tempo real para ambos os agentes.

3. **Jogador contra Jogador (PvP Local)**:
   - Dois jogadores humanos utilizam o mesmo computador, alternando turnos.
   - Ideal para testes empíricos das regras e dinâmica do jogo sem auxílio da IA.

---

## 6. Fundamentos Teóricos da Inteligência Artificial

### 6.1. Minimax Clássico
O algoritmo Minimax modela o jogo como uma árvore de decisão determinística de soma zero. Em cada nível da árvore:
- **Nó MAX**: O jogador IA seleciona a ação que maximiza o valor da utilidade.
- **Nó MIN**: O adversário escolhe a ação que minimiza o valor para o jogador MAX.

A relação de recorrência é dada por:

$$
V(s) =
\begin{cases}
\text{Eval}(s), & \text{se } s \text{ é terminal ou } \text{profundidade} = 0 \\
\max_{a \in A(s)} V(\text{Resultado}(s, a)), & \text{se } \text{jogador}(s) = \text{MAX} \\
\min_{a \in A(s)} V(\text{Resultado}(s, a)), & \text{se } \text{jogador}(s) = \text{MIN}
\end{cases}
$$

A complexidade temporal do Minimax é $\mathcal{O}(b^d)$, onde $b$ é o fator de ramificação médio e $d$ é a profundidade em plies.

### 6.2. Poda Alpha-Beta
A Poda Alpha-Beta mantém dois valores limites ao longo do percurso:
- $\alpha$: O melhor valor (máximo) já garantido para o jogador MAX no caminho atual.
- $\beta$: O melhor valor (mínimo) já garantido para o jogador MIN no caminho atual.

Sempre que em um nó MIN o valor encontrado for menor ou igual a $\alpha$ ($\text{valor} \le \alpha$), ou em um nó MAX o valor for maior ou igual a $\beta$ ($\text{valor} \ge \beta$), o ramo restante é descartado (podado), pois o adversário racional jamais permitiria alcançar aquele estado.

Com uma ordenação ótima de movimentos, a complexidade temporal cai para $\mathcal{O}(b^{d/2})$, dobrando a profundidade explorável no mesmo intervalo de tempo.

### 6.3. Função Heurística Ponderada
A utilidade de um estado não-terminal é avaliada sempre sob a perspectiva do jogador MAX. O componente central baseia-se na menor distância de cada jogador até sua meta, calculada por BFS considerando as barricadas ativas:

$$
H(s) = w_{\text{dist}} \times (D_{\text{oponente}} - D_{\text{IA}}) + w_{\text{paredes}} \times (W_{\text{IA}} - W_{\text{oponente}}) + w_{\text{avanço}} \times \Delta_{\text{progresso}}
$$

Onde:
- $D_{\text{IA}}$: Menor distância em passos do agente MAX até sua linha de vitória.
- $D_{\text{oponente}}$: Menor distância em passos do adversário até sua linha de vitória.
- $W_{\text{IA}}, W_{\text{oponente}}$: Quantidade de barricadas restantes de cada jogador.
- $\Delta_{\text{progresso}}$: Vantagem de avanço no tabuleiro.
- Estados de vitória/derrota recebem valores de magnitude dominante: $+100.000 - \text{ply}$ e $-100.000 + \text{ply}$, priorizando vitórias mais rápidas e adiando derrotas.

### 6.4. Busca em Largura (BFS)
O módulo `src/game/pathfinding.py` emprega BFS para duas funções cruciais:
1. **Validação de Barricadas**: Antes de validar a inserção de uma barricada, o BFS verifica se ambos os jogadores continuam tendo pelo menos um caminho aberto até seus objetivos.
2. **Cálculo da Heurística**: Uma BFS invertida a partir da linha de meta obtém em $\mathcal{O}(V + E)$ o caminho mínimo e as distâncias exatas de todas as casas do tabuleiro.

### 6.5. Tabela de Transposição (TT)
Estados equivalentes de jogo podem ser alcançados por diferentes permutações de jogadas (transposições). A classe `TranspositionTable` indexa os estados por uma chave hash imutável e armazena:
- Profundidade pesquisada.
- Valor numérico atribuído.
- Flag do tipo de limite (`TT_EXACT`, `TT_LOWERBOUND`, `TT_UPPERBOUND`).
- Melhor movimento identificado (`best_move`).

Ao revisitar um estado com profundidade igual ou maior, o resultado pode ser reutilizado diretamente ou utilizado para restringir a janela $[\alpha, \beta]$.

### 6.6. Ordenação de Movimentos (Move Ordering)
Para maximizar a ocorrência de podas, as ações são ordenadas previamente segundo critérios de prioridade:
1. Movimento recomendado pela Tabela de Transposição / iteração prévia.
2. Vitórias imediatas (movimento de peão até a linha de chegada).
3. Movimentos de peão que diminuem a distância BFS até a meta.
4. Barricadas posicionadas sobre o menor caminho conhecido do oponente.
5. Demais movimentações e barricadas.

### 6.7. Aprofundamento Iterativo e Tempo Limite
O algoritmo realiza buscas progressivas com profundidade $d = 1, 2, 3, \dots, D$. Se o tempo limite configurado for atingido antes da conclusão de uma profundidade, a busca encerra graciosamente e retorna a melhor ação comprovada na última profundidade totalmente concluída.

---

## 7. Experimentos Acadêmicos

O projeto inclui scripts dedicados para coleta empírica de métricas científicas:

### 7.1. Benchmark de Desempenho
Compara Minimax puro, Alpha-Beta, Alpha-Beta com Ordenação e Alpha-Beta completo em diferentes cenários (abertura, meio-jogo e final de jogo).

**Execução:**
```bash
python experiments/benchmark.py --depth 2 --csv experiments/benchmark_results.csv
```

**Exemplo de Resultados Coletados (Profundidade 2):**

| Cenário | Algoritmo | Tempo (s) | Nós Visitados | Podas Realizadas | Pico Memória (KB) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Abertura** | 1. Minimax Puro | 2.260 s | 5.432 | 0 | 28.3 KB |
| **Abertura** | 2. Alpha-Beta | 0.379 s | 224 | 5.208 | 21.1 KB |
| **Meio-Jogo** | 1. Minimax Puro | 1.486 s | 4.395 | 0 | 19.0 KB |
| **Meio-Jogo** | 2. Alpha-Beta | 0.343 s | 397 | 3.998 | 19.6 KB |
| **Meio-Jogo** | 3. Alpha-Beta + Ord. | 0.377 s | 201 | 4.194 | 21.8 KB |

> **Conclusão Acadêmica**: A Poda Alpha-Beta reduziu em mais de **95%** o número de nós explorados no estado inicial. No meio-jogo, a ordenação de movimentos cortou pela metade os nós restantes visitados pelo Alpha-Beta básico.

### 7.2. Partidas Bot vs Bot (Self-Play)
Simula partidas completas entre duas configurações distintas de bots, registrando dados turno a turno em formato tabular (CSV).

**Execução:**
```bash
python experiments/self_play.py --games 2 --red-depth 2 --blue-depth 2 --seed 42
```
Gera o relatório com o vencedor, quantidade de turnos, tempo total e nós visitados em `experiments/self_play_results.csv`.

---

## 8. Estrutura do Projeto

```
BARRICADE-AI/
│
├── main.py                     # Ponto de entrada da aplicação
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação acadêmica e manual de uso
│
├── assets/                     # Recursos audiovisuais
│   ├── images/
│   └── sounds/
│
├── src/
│   ├── game/                   # Motor e regras do jogo
│   │   ├── __init__.py
│   │   ├── actions.py          # Classes MoveAction e WallAction
│   │   ├── board.py            # Geometria e checagem de colisões/passagens
│   │   ├── pathfinding.py      # Busca em Largura (BFS) e caminhos mínimos
│   │   ├── rules.py            # Validação de movimentos e saltos especiais
│   │   └── state.py            # Representação imutável/clonável do GameState
│   │
│   ├── ai/                     # Algoritmos de busca adversarial
│   │   ├── __init__.py
│   │   ├── alpha_beta.py       # Minimax com Alpha-Beta, ID e controle de tempo
│   │   ├── evaluation.py       # Funções heurísticas (simples e ponderada)
│   │   ├── minimax.py          # Minimax recursivo puro para comparação
│   │   ├── move_ordering.py    # Ordenação heurística para maximizar cortes
│   │   ├── search_stats.py     # Coleta de métricas e telemetria
│   │   └── transposition_table.py # Tabela de transposição com flags
│   │
│   ├── ui/                     # Interface gráfica com Pygame
│   │   ├── __init__.py
│   │   ├── components.py       # Botões, interruptores e spinners interativos
│   │   ├── input_handler.py    # Mapeamento de cliques e teclas
│   │   ├── menu.py             # Menus Principal e de Configurações
│   │   ├── pygame_app.py       # Gerenciador de ciclo de vida e threads
│   │   └── renderer.py         # Renderização do tabuleiro e telemetria
│   │
│   └── utils/                  # Constantes e configurações gerais
│       ├── __init__.py
│       └── constants.py        # Cores, dimensões, pesos e IDs
│
├── tests/                      # Bateria de testes automatizados com pytest
│   ├── test_alpha_beta.py      # Testes da Poda Alpha-Beta e TT
│   ├── test_board.py           # Testes de geometria e colisões
│   ├── test_minimax.py         # Testes de legalidade e vitórias imediatas
│   ├── test_pathfinding.py     # Testes de caminhos mínimos com BFS
│   ├── test_rules.py           # Testes de saltos retos/diagonais e regras
│   └── test_ui.py              # Testes da interface em modo headless
│
└── experiments/                # Scripts de análise científica
    ├── benchmark.py            # Comparativo de algoritmos e métricas
    ├── benchmark_results.csv   # Dados gerados pelo benchmark
    ├── self_play.py            # Confronto autônomo entre agentes
    └── self_play_results.csv   # Dados gerados pelo self-play
```

---

## 9. Testes Automatizados

A integridade do motor de jogo e dos algoritmos de busca é validada por uma suíte completa de **30 testes unitários** via `pytest`.

Para rodar todos os testes:
```bash
python -m pytest
```

Saída esperada:
```
tests/test_alpha_beta.py ..... [ 16%]
tests/test_board.py ......     [ 36%]
tests/test_minimax.py ....     [ 50%]
tests/test_pathfinding.py .....[ 66%]
tests/test_rules.py ........   [ 93%]
tests/test_ui.py ..            [100%]
====================== 30 passed in 1.90s ======================
```
