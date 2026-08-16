import streamlit as st
import streamlit.components.v1 as components
import math
import time

def count_solutions_bitwise(n):
    """
    Algoritmo DFS (Busca em Profundidade) com Operações Bit a Bit.
    Calcula o número total de soluções possíveis.
    O cache foi removido para fins de benchmark em tempo real.
    """
    if n in [2, 3]: return 0
    if n == 1: return 1
    
    count = 0
    done = (1 << n) - 1 

    def solve(row, ld, rd):
        nonlocal count
        if row == done:
            count += 1
            return
        
        poss = ~(row | ld | rd) & done
        while poss:
            bit = poss & -poss 
            poss -= bit
            solve(row | bit, (ld | bit) << 1, (rd | bit) >> 1)

    solve(0, 0, 0)
    return count

def get_one_solution(n):
    """
    Algoritmo padrão de Backtracking.
    Retorna apenas a PRIMEIRA solução encontrada (matriz 2D) para renderização imediata.
    Para a tela no menor tempo possível sem calcular a árvore inteira.
    """
    if n in [2, 3]: return None
    
    board_state = [-1] * n

    def is_safe(row, col):
        for i in range(row):
            if board_state[i] == col or \
               board_state[i] - i == col - row or \
               board_state[i] + i == col + row:
                return False
        return True

    def solve(row):
        if row == n:
            return True
        for col in range(n):
            if is_safe(row, col):
                board_state[row] = col
                if solve(row + 1):
                    return True
                board_state[row] = -1
        return False

    if solve(0):
        board = [[0 for _ in range(n)] for _ in range(n)]
        for r in range(n):
            board[r][board_state[r]] = 1
        return board
    
    return None

def render_centered_board(board, n):
    """Gera o HTML com CSS flexbox/grid para um tabuleiro responsivo e sem scroll."""
    html = "<div style='display: flex; justify-content: center; align-items: center; width: 100%; height: 85vh; overflow: hidden;'>"
    html += f"<div style='display: grid; grid-template-columns: repeat({n}, 1fr); grid-template-rows: repeat({n}, 1fr); width: 75vmin; height: 75vmin; border: 4px solid #222; box-shadow: 0 10px 20px rgba(0,0,0,0.3);'>"
    
    for r in range(n):
        for c in range(n):
            is_light = (r + c) % 2 == 0
            bg = "#f0d9b5" if is_light else "#b58863"
            piece = "♛" if board[r][c] == 1 else ""
            html += f"<div style='background-color: {bg}; display: flex; align-items: center; justify-content: center; font-size: calc(50vmin / {n}); color: #000; user-select: none; transition: 0.2s;'>{piece}</div>"
            
    html += "</div></div>"
    return html

def render_empty_board(n):
    """Gera um tabuleiro vazio quando não há solução matemática."""
    empty_board = [[0]*n for _ in range(n)]
    return render_centered_board(empty_board, n)

def render_interactive_board(n):
    """Gera um HTML interativo (JS) para inserção manual e detecção de conflitos ao vivo."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: transparent;
            overflow: hidden;
            font-family: sans-serif;
        }}
        #board {{
            display: grid;
            grid-template-columns: repeat({n}, 1fr);
            grid-template-rows: repeat({n}, 1fr);
            width: 90vmin;
            height: 90vmin;
            border: 4px solid #222;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }}
        .cell {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: calc(60vmin / {n});
            cursor: pointer;
            user-select: none;
            transition: background-color 0.2s, transform 0.1s;
            color: #000;
        }}
        .cell:active {{
            transform: scale(0.90);
        }}
        .light {{ background-color: #f0d9b5; }}
        .dark {{ background-color: #b58863; }}
        .conflict {{
            background-color: #ff4d4d !important;
            box-shadow: inset 0 0 20px #cc0000;
        }}
    </style>
    </head>
    <body>
        <div id="board"></div>
        <script>
            const n = {n};
            let queens = [];

            function render() {{
                const board = document.getElementById('board');
                board.innerHTML = '';
                
                // Analisa todos os conflitos (mesma linha, coluna ou diagonais)
                let conflicts = new Set();
                for(let i = 0; i < queens.length; i++) {{
                    for(let j = i + 1; j < queens.length; j++) {{
                        let q1 = queens[i];
                        let q2 = queens[j];
                        if(q1.r === q2.r || q1.c === q2.c || Math.abs(q1.r - q2.r) === Math.abs(q1.c - q2.c)) {{
                            conflicts.add(q1.r + ',' + q1.c);
                            conflicts.add(q2.r + ',' + q2.c);
                        }}
                    }}
                }}

                // Renderiza o grid de quadrados
                for(let r = 0; r < n; r++) {{
                    for(let c = 0; c < n; c++) {{
                        const cell = document.createElement('div');
                        const isLight = (r + c) % 2 === 0;
                        cell.className = 'cell ' + (isLight ? 'light' : 'dark');
                        
                        if (queens.some(q => q.r === r && q.c === c)) {{
                            cell.innerHTML = '♛';
                        }}
                        
                        // Se essa célula estiver no radar de conflitos, pinta de vermelho
                        if (conflicts.has(r + ',' + c)) {{
                            cell.classList.add('conflict');
                        }}

                        // Evento de clique para adicionar/remover
                        cell.onclick = () => {{
                            const idx = queens.findIndex(q => q.r === r && q.c === c);
                            if (idx !== -1) {{
                                queens.splice(idx, 1); // Remove
                            }} else {{
                                queens.push({{r: r, c: c}}); // Adiciona
                            }}
                            render();
                        }};
                        
                        board.appendChild(cell);
                    }}
                }}
            }}
            
            // Renderização inicial
            render();
        </script>
    </body>
    </html>
    """
    return html

def main():
    st.set_page_config(page_title="N-Rainhas IA Profiler", layout="wide", initial_sidebar_state="expanded")

    primary_color = st.get_option("theme.primaryColor")
    
    # CSS para ocultar itens inúteis mas preservar o Header onde o botão de abrir sidebar reside
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 0rem !important;
                padding-left: 0rem !important;
                padding-right: 0rem !important;
                max-height: 100vh;
            }
            html, body, [data-testid="stAppViewContainer"] {
                overflow: hidden !important;
            }

            div {
                text-align: justify;
            }
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)


    title_html = f"""
                <div style='background-color: #1e1e1e; padding: 5px; border-radius: 5px; border-left: 4px solid {primary_color}; margin-left: 10px;'>
                    <h1 style='font-size: 32px; margin-left: 10px;'><b>Problema das N-Rainhas</b><br>
                        <i style='font-size: 20px; margin-left: 10px;'><b style='color: {primary_color};'>Grupo: </b> Ana, Luan e Wesley</i>
                    </h1>
                </div>
                """
    
    st.sidebar.markdown(title_html, unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    info_html = """
            <div style='background-color: #1e1e1e; padding: 15px; border-radius: 5px; border-left: 2px solid #5ea1ff; font-size: 16px; margin-bottom: 15px;'>
                <b style='color: #5ea1ff;'>Problema de Satisfação de Restrições (CSP)</b><br>
                O <b>Problema das N-Rainhas</b> é resolvido através do algoritmo de <i>Backtracking</i> (Busca em Profundidade).<br><br>
                <b>Complexidade de Tempo: <code>O(N!)</code></b><br>
                O pior caso cresce de forma fatorial. A versão completa utiliza <b>Bitwise Pruning</b> para pular milhares de galhos inúteis da árvore, mas a barreira teórica assintótica permanece O(N!).
            </div>
            """
    with st.sidebar.expander("Explicação Algoritmo", expanded=True, icon="ℹ️"):
        st.markdown(info_html, unsafe_allow_html=True)

    st.sidebar.divider()

    st.sidebar.subheader("Configurações do Algoritmo")
    n = st.sidebar.slider("Tamanho do Tabuleiro (N)", min_value=1, max_value=20, value=8, step=1, help="Define o tamanho do tabuleiro NxN e o número de rainhas a serem posicionadas. Para N > 14, a varredura completa pode ser lenta então o limite imposto pelo grupo é de até 20.")
    
    # Novo toggle para o Modo Manual
    modo_manual = st.sidebar.toggle("Modo Manual (Interativo)", value=False, help="Permite inserir e remover rainhas com cliques. Detecta e colore conflitos instantaneamente em vermelho.")
    
    # Toggle para ativar/desativar a varredura completa da árvore (pode ser pesado para N > 14)
    calcular_todas = st.sidebar.toggle("Calcular TODAS as soluções", value=False, help="Se ativado, o algoritmo percorrerá toda a árvore de estado para encontrar todas as ramificações de sucesso. Para N alto, demora muito.")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Estatísticas & Performance")


    # 1. Combinações Brutas Iniciais
    total_combinations = math.comb(n*n, n)
    
    # 2. Medindo tempo da PRIMEIRA solução
    t0_one = time.perf_counter()
    board = get_one_solution(n)
    t1_one = time.perf_counter()
    time_one_ms = (t1_one - t0_one) * 1000

    # 3. Medindo tempo de TODAS as soluções (se ativado)
    valid_solutions = "?"
    time_all_ms = 0
    # Desativa a carga pesada da IA se o usuário estiver brincando no modo manual
    if calcular_todas and not modo_manual:
        with st.sidebar:
            with st.spinner(f"Explorando a árvore para N={n}..."):
                t0_all = time.perf_counter()
                valid_solutions = count_solutions_bitwise(n)
                t1_all = time.perf_counter()
                time_all_ms = (t1_all - t0_all) * 1000

    fmt_combinations = f"{total_combinations:,}".replace(",", ".")
    
    st.sidebar.metric(label=f"Espaço de Estados Total", value=fmt_combinations, help="De quantas formas é possível jogar N rainhas aleatoriamente.")
    
    if not modo_manual:
        # Mostrar métricas condicionais de acordo com a escolha (Modo IA)
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric(label="Tempo (1 Solução)", value=f"{time_one_ms:.2f} ms", help="Tempo para encontrar a primeira solução válida (Backtracking).")
        with col2:
            if calcular_todas:
                st.metric(label="Tempo (Varredura)", value=f"{time_all_ms/1000:.2f} s" if time_all_ms > 1000 else f"{time_all_ms:.2f} ms", help="Tempo para explorar todas as soluções possíveis.")
            else:
                st.metric(label="Tempo (Varredura)", value="Desativado", help="Varredura completa da árvore está desativada. Ative para calcular todas as soluções possíveis.")
                
        # Resultado numérico da varredura
        st.sidebar.metric(label="Soluções Seguras", value=f"{valid_solutions:,}".replace(",", ".") if isinstance(valid_solutions, int) else valid_solutions, help="Número total de soluções válidas encontradas (Backtracking + Bitwise).") 
        
        if n in [2, 3]:
            st.sidebar.error(f"Não existe solução para N={n}.")
    else:
        # Mensagem pro modo manual
        st.sidebar.info("**Modo Manual Ativo** \n\nClique no tabuleiro para testar as rainhas. As métricas de desempenho da IA estão em pausa.")

    if modo_manual:
        # Modo Manual usa a integração com iframe para rodar o Javascript cliente interativo
        html_interativo = render_interactive_board(n)
        components.html(html_interativo, height=750)
    else:
        # Modo IA carrega o gabarito instantâneo
        if board is not None:
            board_html = render_centered_board(board, n)
            st.markdown(board_html, unsafe_allow_html=True)
        else:
            board_html = render_empty_board(n)
            st.markdown(board_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()