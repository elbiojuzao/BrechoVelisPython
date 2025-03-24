import customtkinter as ctk
from datetime import datetime
import calendar
import locale
from utils import conectar_banco_dados, desconectar_banco_dados

def criar_dashboard_visao_geral():
    dashboard_vg = ctk.CTkToplevel()
    dashboard_vg.title("Visão Geral de Vendas")
    dashboard_vg.minsize(300, 200)

    # Definir a localidade para português do Brasil
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except locale.Error:
            print("Erro ao definir a localidade para português.")

    meses_ano = ["Todos os Meses"] + [calendar.month_name[i] for i in range(1, 13)]
    mes_atual = datetime.now().month
    mes_atual_nome = calendar.month_name[mes_atual]
    mes_padrao = mes_atual_nome if mes_atual_nome in meses_ano else "Todos os Meses"

    mes_selecionado = ctk.StringVar(dashboard_vg)
    mes_selecionado.set(mes_padrao)

    # Criando um CTkCanvas diretamente para isolar o problema
    canvas_kpis = ctk.CTkCanvas(dashboard_vg, width=400, height=200, highlightthickness=0)
    canvas_kpis.place(x=10, y=10)

    label_selecionar_mes = ctk.CTkLabel(dashboard_vg, text="Selecionar Mês:")
    label_selecionar_mes.place(x=10, y=220)
    dropdown_meses = ctk.CTkComboBox(dashboard_vg, textvariable=mes_selecionado, values=meses_ano, state="readonly")
    dropdown_meses.place(x=10, y=250)

    label_total_vendas = ctk.CTkLabel(canvas_kpis, text="Total de Vendas Pagas:")
    label_total_vendas.place(x=10, y=10)
    valor_total_vendas = ctk.CTkLabel(canvas_kpis, text="R$ 0.00", font=("Arial", 16, "bold"))
    valor_total_vendas.place(x=200, y=10)

    label_num_vendas = ctk.CTkLabel(canvas_kpis, text="Número Total de Vendas Pagas:")
    label_num_vendas.place(x=10, y=50)
    valor_num_vendas = ctk.CTkLabel(canvas_kpis, text="0", font=("Arial", 16, "bold"))
    valor_num_vendas.place(x=200, y=50)

    label_ticket_medio = ctk.CTkLabel(canvas_kpis, text="Ticket Médio (Vendas Pagas):")
    label_ticket_medio.place(x=10, y=90)
    valor_ticket_medio = ctk.CTkLabel(canvas_kpis, text="R$ 0.00", font=("Arial", 16, "bold"))
    valor_ticket_medio.place(x=200, y=90)

    def atualizar_visao_geral(event):
        mes_sel = mes_selecionado.get()
        mes_numero = None
        ano_atual = datetime.now().year

        if mes_sel != "Todos os Meses":
            try:
                mes_numero = datetime.strptime(mes_sel, "%B").month
            except ValueError:
                try:
                    mes_numero = datetime.strptime(mes_sel, "%b").month
                except ValueError:
                    ctk.CTkMessagebox(title="Erro", message=f"Não foi possível identificar o mês: {mes_sel}")
                    return

        conexao = conectar_banco_dados()
        if not conexao:
            ctk.CTkMessagebox(title="Erro", message="Erro ao conectar ao banco de dados.")

        cursor = conexao.cursor()
        condicao_mes = ""
        parametros = []

        if mes_numero:
            condicao_mes = "AND STRFTIME('%m', data) = ? AND STRFTIME('%Y', data) = ?"
            parametros = [f"{mes_numero:02d}", str(ano_atual)]

        # Calcular Total de Vendas Pagas
        cursor.execute(f"SELECT SUM(valor) FROM vendas WHERE pago = 'Sim' {condicao_mes}", parametros)
        total_vendas = cursor.fetchone()[0]
        total_vendas_str = f"R$ {total_vendas:.2f}" if total_vendas else "R$ 0.00"
        valor_total_vendas.configure(text=total_vendas_str)

        # Calcular Número Total de Vendas Pagas
        cursor.execute(f"SELECT COUNT(*) FROM vendas WHERE pago = 'Sim' {condicao_mes}", parametros)
        num_vendas = cursor.fetchone()[0]
        valor_num_vendas.configure(text=num_vendas)

        # Calcular Ticket Médio (apenas para vendas pagas)
        if num_vendas > 0 and total_vendas is not None:
            ticket_medio = total_vendas / num_vendas
            ticket_medio_str = f"R$ {ticket_medio:.2f}"
        else:
            ticket_medio_str = "R$ 0.00"
        valor_ticket_medio.configure(text=ticket_medio_str)

        desconectar_banco_dados(conexao)

    dropdown_meses.bind("<<ComboboxSelected>>", atualizar_visao_geral)
    atualizar_visao_geral(None)

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