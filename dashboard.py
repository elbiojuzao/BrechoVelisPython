import customtkinter as ctk
from utils import conectar_banco_dados, desconectar_banco_dados
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def criar_dashboard_visao_geral():
    dashboard_vg = ctk.CTkToplevel()
    dashboard_vg.title("Visão Geral de Vendas")
    dashboard_vg.minsize(500, 400)

    frame_kpis = ctk.CTkFrame(dashboard_vg)
    frame_kpis.pack(padx=20, pady=20, fill="both", expand=True)

    label_total_vendas = ctk.CTkLabel(frame_kpis, text="Total de Vendas Pagas:")
    label_total_vendas.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    valor_total_vendas = ctk.CTkLabel(frame_kpis, text="Carregando...", font=("Arial", 16, "bold"))
    valor_total_vendas.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    label_num_vendas = ctk.CTkLabel(frame_kpis, text="Número Total de Vendas:")
    label_num_vendas.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    valor_num_vendas = ctk.CTkLabel(frame_kpis, text="Carregando...", font=("Arial", 16, "bold"))
    valor_num_vendas.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    label_ticket_medio = ctk.CTkLabel(frame_kpis, text="Ticket Médio:")
    label_ticket_medio.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    valor_ticket_medio = ctk.CTkLabel(frame_kpis, text="Carregando...", font=("Arial", 16, "bold"))
    valor_ticket_medio.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    # Conectar ao banco e atualizar KPIs
    conexao = conectar_banco_dados()
    if conexao:
        cursor = conexao.cursor()

        cursor.execute("SELECT SUM(valor) FROM vendas WHERE pago = 'Sim'")
        total_vendas = cursor.fetchone()[0] or 0
        valor_total_vendas.configure(text=f"R$ {total_vendas:.2f}")

        cursor.execute("SELECT COUNT(*) FROM vendas WHERE pago = 'Sim'")
        num_vendas = cursor.fetchone()[0] or 0
        valor_num_vendas.configure(text=str(num_vendas))

        if num_vendas > 0:
            ticket_medio = total_vendas / num_vendas
            valor_ticket_medio.configure(text=f"R$ {ticket_medio:.2f}")
        else:
            valor_ticket_medio.configure(text="R$ 0.00")

        # 📌 Buscar faturamento dos últimos 6 meses
        cursor.execute("""
            SELECT STRFTIME('%m/%Y', data) AS mes, SUM(valor) 
            FROM vendas 
            WHERE pago = 'Sim' 
            GROUP BY mes 
            ORDER BY mes DESC 
            LIMIT 6
        """)
        dados_faturamento = cursor.fetchall()

        conexao.close()

        # 📊 Criar gráfico de faturamento
        if dados_faturamento:
            meses = [item[0] for item in dados_faturamento][::-1]
            valores = [item[1] for item in dados_faturamento][::-1]

            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(meses, valores, color="royalblue")
            ax.set_title("Faturamento dos Últimos 6 Meses")
            ax.set_ylabel("R$")

            canvas = FigureCanvasTkAgg(fig, master=dashboard_vg)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

def criar_dashboard_desempenho_clientes():
    dashboard_dc = ctk.CTkToplevel()
    dashboard_dc.title("Desempenho de Clientes")

    # Conectar ao banco de dados
    conexao = conectar_banco_dados()
    if not conexao:
        ctk.CTkLabel(dashboard_dc, text="Erro ao conectar ao banco de dados.").pack(padx=10, pady=10)

    cursor = conexao.cursor()

    # Calcular Número Total de Clientes Únicos
    cursor.execute("SELECT COUNT(DISTINCT nome) FROM vendas WHERE nome IS NOT NULL AND nome != ''")
    total_clientes = cursor.fetchone()[0]

    # Clientes que Mais Compraram
    cursor.execute("SELECT nome, COUNT(*) AS num_compras FROM vendas WHERE pago = 'Sim' AND nome IS NOT NULL AND nome != '' GROUP BY nome ORDER BY num_compras DESC LIMIT 10")
    clientes_mais_compraram = cursor.fetchall()

    # Clientes que Mais Gastaram
    cursor.execute("SELECT nome, SUM(valor) AS total_gasto FROM vendas WHERE pago = 'Sim' AND valor IS NOT NULL AND nome IS NOT NULL AND nome != '' GROUP BY nome ORDER BY total_gasto DESC LIMIT 10")
    clientes_mais_gastaram = cursor.fetchall()

    # --- Widgets para exibir as informações ---
    ctk.CTkLabel(dashboard_dc, text="Total de Clientes Únicos:", font=("Arial", 12)).pack(pady=5)
    ctk.CTkLabel(dashboard_dc, text=total_clientes, font=("Arial", 16, "bold")).pack()

    ctk.CTkLabel(dashboard_dc, text="\nClientes que Mais Compraram:", font=("Arial", 12)).pack(pady=5)
    for nome, num_compras in clientes_mais_compraram:
        ctk.CTkLabel(dashboard_dc, text=f"{nome}: {num_compras} compras").pack()

    ctk.CTkLabel(dashboard_dc, text="\nClientes que Mais Gastaram:", font=("Arial", 12)).pack(pady=5)
    for nome, total_gasto in clientes_mais_gastaram:
        ctk.CTkLabel(dashboard_dc, text=f"{nome}: R$ {total_gasto:.2f}").pack()

    desconectar_banco_dados(conexao)

def main(dark_mode):
    if dark_mode:
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")

    dashboard_inicial = ctk.CTkToplevel()
    dashboard_inicial.title("Dashboards")

    botao_visao_geral = ctk.CTkButton(dashboard_inicial, text="Visão Geral de Vendas", command=criar_dashboard_visao_geral)
    botao_visao_geral.pack(pady=20, padx=20)

    botao_desempenho_clientes = ctk.CTkButton(dashboard_inicial, text="Desempenho de Clientes", command=criar_dashboard_desempenho_clientes)
    botao_desempenho_clientes.pack(pady=20, padx=20)