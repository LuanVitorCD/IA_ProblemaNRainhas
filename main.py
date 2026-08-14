import streamlit as st
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

def main():
    st.set_page_config(page_title="N-Rainhas IA Profiler", layout="wide", initial_sidebar_state="expanded")
    
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
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    st.sidebar.title("Configurações IA ⚙️")
    st.sidebar.markdown("---")
    
    n = st.sidebar.slider("Tamanho do Tabuleiro (N)", min_value=1, max_value=20, value=8, step=1)
    
    # Toggle para ativar/desativar a varredura completa da árvore (pode ser pesado para N > 14)
    calcular_todas = st.sidebar.toggle("Calcular TODAS as soluções", value=False, help="Se ativado, o algoritmo percorrerá toda a árvore de estado para encontrar todas as ramificações de sucesso. Para N alto, demora muito.")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Estatísticas & Performance ⏱️")

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
    if calcular_todas:
        with st.sidebar:
            with st.spinner(f"Explorando a árvore para N={n}..."):
                t0_all = time.perf_counter()
                valid_solutions = count_solutions_bitwise(n)
                t1_all = time.perf_counter()
                time_all_ms = (t1_all - t0_all) * 1000

    fmt_combinations = f"{total_combinations:,}".replace(",", ".")
    
    st.sidebar.metric(label=f"Espaço de Estados Total", value=fmt_combinations, help="De quantas formas é possível jogar N rainhas aleatoriamente.")
    
    # Mostrar métricas condicionais de acordo com a escolha
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric(label="Tempo (1 Solução)", value=f"{time_one_ms:.2f} ms")
    with col2:
        if calcular_todas:
            st.metric(label="Tempo (Varredura)", value=f"{time_all_ms/1000:.2f} s" if time_all_ms > 1000 else f"{time_all_ms:.2f} ms")
        else:
            st.metric(label="Tempo (Varredura)", value="Desativado")
            
    # Resultado numérico da varredura
    st.sidebar.metric(label="Soluções Seguras", value=f"{valid_solutions:,}".replace(",", ".") if isinstance(valid_solutions, int) else valid_solutions)
    
    if n in [2, 3]:
        st.sidebar.error(f"Não existe solução para N={n}.")

    st.sidebar.markdown("---")
    info_html = """
    <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; font-size: 14px;'>
        <b style='color: #4CAF50;'>Problema de Satisfação de Restrições (CSP)</b><br>
        O <b>Problema das N-Rainhas</b> é resolvido através do algoritmo de <i>Backtracking</i> (Busca em Profundidade).<br><br>
        <b>Complexidade de Tempo:</b> <code>O(N!)</code><br>
        O pior caso cresce de forma fatorial. A versão completa utiliza <b>Bitwise Pruning</b> para pular milhares de galhos inúteis da árvore, mas a barreira teórica assintótica permanece O(N!).
    </div>
    """
    st.sidebar.markdown(info_html, unsafe_allow_html=True)

    if board is not None:
        board_html = render_centered_board(board, n)
        st.markdown(board_html, unsafe_allow_html=True)
    else:
        board_html = render_empty_board(n)
        st.markdown(board_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()