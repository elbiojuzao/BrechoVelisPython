import tkinter as tk
from tkinter import ttk
import sqlite3
import json
import csv
from tkinter import filedialog, messagebox, Toplevel, Button
from tkcalendar import Calendar
from datetime import datetime
from utils import conectar_banco_dados, desconectar_banco_dados, carregar_configuracoes, salvar_configuracoes_janela, ajustar_colunas

popup_edicao_aberto = None

def main():
    global popup_edicao_aberto 
    nova_janela = tk.Toplevel()
    nova_janela.title("Vendas")

    # Carregar configurações ou definir padrão para a janela de Vendas
    configuracoes = carregar_configuracoes()
    if configuracoes and "vendas" in configuracoes:
        nova_janela.geometry(f"{configuracoes['vendas']['largura']}x{configuracoes['vendas']['altura']}+{configuracoes['vendas']['x']}+{configuracoes['vendas']['y']}")
    else:
        nova_janela.geometry("1100x600")

    def carregar_dados_vendas():
        conexao = conectar_banco_dados()
        if not conexao:
            return []
        
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM vendas")
            dados_vendas = cursor.fetchall()
            desconectar_banco_dados(conexao)
            return dados_vendas
        except sqlite3.Error as erro:
            print("Erro na consulta SQL:", erro)
            return []

    def exibir_dados_vendas(dados_vendas):
        for item in treeview_vendas.get_children():
            treeview_vendas.delete(item)
        for venda in dados_vendas:
            data = venda[1] if venda[1] else ""
            nome = venda[2] if venda[2] else ""
            pecas = venda[3] if venda[3] is not None else ""
            valor = "R$ " + str(venda[4]) if venda[4] is not None else ""
            primeira_peca = venda[5] if venda[5] is not None else ""
            haver = "R$ " + str(venda[6]) if venda[6] is not None else ""
            total_sacolinha = "R$ " + str(venda[7]) if venda[7] is not None else ""
            pago = venda[8] if venda[8] else ""
            tipo_pagamento = venda[9] if venda[9] else ""
            frete = venda[10] if venda[10] else ""
            adendo = venda[11] if venda[11] else ""

            venda_tratada = [data, nome, pecas, valor, primeira_peca, haver, total_sacolinha, pago, tipo_pagamento, frete, adendo]

            if pago == "Não":
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("pago_nao",))  # Vermelho
            elif frete in ("Enviado", "Em mãos", "DOAÇÃO"):
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("roxo_claro",))  # Roxo
            elif frete == "Embalar":
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("amarelo_claro",))  # Amarelo
            elif pago == "Sim":
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("pago_sim",))  # Verde

    def importar_compras():
        arquivo_csv = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if not arquivo_csv:
            messagebox.showerror("Erro", "Nenhum arquivo CSV selecionado.")

        conexao = conectar_banco_dados()
        if not conexao:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")

        try:
            cursor = conexao.cursor()
            linhas_importadas = 0
            linhas_falhas = 0
            with open(arquivo_csv, "r", newline="", encoding="windows-1252") as arquivo:
                leitor_csv = csv.reader(arquivo, delimiter=";")  # Especifica o separador como ponto e vírgula
                next(leitor_csv)  # Ignora o cabeçalho
                for linha in leitor_csv:
                    if len(linha) < 11:
                        print(f"Linha incompleta: {linha}")
                        linhas_falhas += 1
                        continue

                    data = linha[0] if linha[0] else None
                    nome = linha[1] if linha[1] else None
                    pecas = linha[2] if linha[2] else None
                    valor = linha[3] if linha[3] else None
                    primeira_peca = linha[4] if len(linha) > 4 and linha[4] else None  # Verifica se o índice 4 existe
                    haver = linha[5] if linha[5] else None
                    total_sacolinha = linha[6] if linha[6] else None
                    pago = linha[7] if linha[7] else None
                    tipo_pagamento = linha[8] if linha[8] else None
                    frete = linha[9] if linha[9] else None
                    adendo = linha[10] if linha[10] else None
                    try:
                        cursor.execute("INSERT INTO vendas (data, nome, peca, valor, primeira_peca, haver, total_sacolinha, pago, tipo_pagamento, frete, adendo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data, nome, pecas, valor, primeira_peca, haver, total_sacolinha, pago, tipo_pagamento, frete, adendo))
                        linhas_importadas += 1
                    except sqlite3.Error as erro:
                        print(f"Erro ao inserir linha: {linha}, Erro: {erro}")
                        linhas_falhas += 1
            conexao.commit()
            desconectar_banco_dados(conexao)
            dados_atualizados = carregar_dados_vendas()
            exibir_dados_vendas(dados_atualizados)
            messagebox.showinfo("Sucesso", f"Compras importadas: {linhas_importadas}\nCompras não importadas: {linhas_falhas}")
        except sqlite3.Error as erro:
            messagebox.showerror("Erro", f"Erro ao importar dados: {erro}")
               

    # Botão Importar Compras no topo
    botao_importar = tk.Button(nova_janela, text="Importar Compras", command=importar_compras)
    botao_importar.pack(pady=10)

    # Filtros
    frame_filtros = tk.Frame(nova_janela)
    frame_filtros.pack(pady=10)

    # Filtro Nome
    tk.Label(frame_filtros, text="Nome:").grid(row=0, column=0)
    entry_nome = tk.Entry(frame_filtros)
    entry_nome.grid(row=0, column=1)

    # Filtro Data
    def abrir_calendario_inicio(event=None):
        x = entry_data_inicio.winfo_rootx() + entry_data_inicio.winfo_width()
        y = entry_data_inicio.winfo_rooty()
        popup = Toplevel(frame_filtros)
        popup.geometry(f"+{x}+{y}")
        cal = Calendar(popup, date_pattern="dd/mm/yyyy")
        cal.pack()
        Button(popup, text="Selecionar", command=lambda: selecionar_data(cal.get_date(), entry_data_inicio, popup)).pack()

    def abrir_calendario_fim(event=None):
        x = entry_data_fim.winfo_rootx() + entry_data_fim.winfo_width()
        y = entry_data_fim.winfo_rooty()
        popup = Toplevel(frame_filtros)
        popup.geometry(f"+{x}+{y}")
        cal = Calendar(popup, date_pattern="dd/mm/yyyy")
        cal.pack()
        Button(popup, text="Selecionar", command=lambda: selecionar_data(cal.get_date(), entry_data_fim, popup)).pack()

    def selecionar_data(data, entry, popup):
        entry.delete(0, tk.END)
        entry.insert(0, data)
        popup.destroy()

    def filtrar_vendas():
        nome_filtro = entry_nome.get().lower()
        data_inicio_filtro = entry_data_inicio.get()
        data_fim_filtro = entry_data_fim.get()
        frete_filtro = combo_frete.get()
        pago_sim_filtro = pago_sim_var.get()
        pago_nao_filtro = pago_nao_var.get()

        dados_filtrados = []
        for venda in dados_iniciais:
            data = venda[1] if venda[1] else ""
            nome = venda[2].lower() if venda[2] else ""
            frete = venda[10] if venda[10] else ""
            pago = venda[8] if venda[8] else ""

            # Filtro por nome
            if nome_filtro and nome_filtro not in nome:
                continue

            # Filtro por data
            try:
                if data_inicio_filtro and data_fim_filtro:  # Intervalo de data
                    data_inicio = datetime.strptime(data_inicio_filtro, "%d/%m/%Y").date()
                    data_fim = datetime.strptime(data_fim_filtro, "%d/%m/%Y").date()
                    if data:
                        data_venda = datetime.strptime(data, "%d/%m/%Y").date() #convert to date.
                        if not (data_inicio <= data_venda <= data_fim):
                            continue
                elif data_inicio_filtro:  # Data de início até hoje
                    data_inicio = datetime.strptime(data_inicio_filtro, "%d/%m/%Y").date()
                    data_fim = datetime.today().date()
                    if data:
                        data_venda = datetime.strptime(data, "%d/%m/%Y").date() #convert to date.
                        if not (data_inicio <= data_venda <= data_fim):
                            continue
                elif data_fim_filtro:  # Início até data de fim
                    data_fim = datetime.strptime(data_fim_filtro, "%d/%m/%Y").date()
                    if data:
                        data_venda = datetime.strptime(data, "%d/%m/%Y").date() #convert to date.
                        if data_venda > data_fim:
                            continue
            except ValueError:
                print(f"Erro ao converter data: {data} ou {data_inicio_filtro} ou {data_fim_filtro}")
                continue

            # Filtro por frete
            if frete_filtro != "Todos" and frete_filtro != frete:
                continue

            # Filtro por pago
            if pago_sim_filtro and pago != "Sim":
                continue
            if pago_nao_filtro and pago != "Não":
                continue

            dados_filtrados.append(venda)

        exibir_dados_vendas(dados_filtrados)

    def editar_venda(event):
        global popup_edicao_aberto
        if popup_edicao_aberto is not None and popup_edicao_aberto.winfo_exists():
            messagebox.showerror("Erro", "Você já está editando outra venda. Por favor, finalize ou cancele a edição atual.")
            popup_edicao_aberto.lift()  # Trazer a janela de edição para frente
            return
        item = treeview_vendas.selection()[0]
        venda = treeview_vendas.item(item, 'values')

        popup = Toplevel(nova_janela)
        popup_edicao_aberto = popup
        popup.title("Editar Venda")

        # Obter coordenadas do cursor
        x = event.x_root
        y = event.y_root

        # Posicionar o popup nas coordenadas do cursor
        popup.geometry(f"+{x}+{y}")

        # Nome do cliente (apenas leitura)
        tk.Label(popup, text="Nome do Cliente:").grid(row=0, column=0)
        tk.Label(popup, text=venda[1]).grid(row=0, column=1)

        # Peças (editável)
        tk.Label(popup, text="Peças:").grid(row=1, column=0)
        entry_pecas = tk.Entry(popup)
        entry_pecas.grid(row=1, column=1)
        entry_pecas.insert(0, venda[2])

        # Valor (editável)
        tk.Label(popup, text="Valor:").grid(row=2, column=0)
        entry_valor = tk.Entry(popup)
        entry_valor.grid(row=2, column=1)
        entry_valor.insert(0, venda[3]) # Removido "R$ " para edição numérica
        entry_valor.configure(state="normal") # Permite edição

        # Haver (editável)
        tk.Label(popup, text="Haver:").grid(row=3, column=0)
        entry_haver = tk.Entry(popup)
        entry_haver.grid(row=3, column=1)
        entry_haver.insert(0, venda[5]) # Removido "R$ " para edição numérica
        entry_haver.configure(state="normal")

        # Total Sacolinha (editável)
        tk.Label(popup, text="Total Sacolinha:").grid(row=4, column=0)
        entry_total_sacolinha = tk.Entry(popup)
        entry_total_sacolinha.grid(row=4, column=1)
        entry_total_sacolinha.insert(0, venda[6]) # Removido "R$ " para edição numérica
        entry_total_sacolinha.configure(state="normal")

        # Pago (editável)
        tk.Label(popup, text="Pago:").grid(row=5, column=0)
        combo_pago = ttk.Combobox(popup, values=["Sim", "Não"])
        combo_pago.grid(row=5, column=1)
        combo_pago.set(venda[7])

        # Tipo de pagamento (editável)
        tk.Label(popup, text="Tipo de Pagamento:").grid(row=6, column=0)
        opcoes_pagamento = list(set([venda[9] for venda in carregar_dados_vendas() if venda[9]]))
        combo_tipo_pagamento = ttk.Combobox(popup, values=opcoes_pagamento)
        combo_tipo_pagamento.grid(row=6, column=1)
        combo_tipo_pagamento.set(venda[8])

        # Adendo (editável)
        tk.Label(popup, text="Adendo:").grid(row=7, column=0)
        text_adendo = tk.Text(popup, height=4, width=30)
        text_adendo.grid(row=7, column=1)
        text_adendo.insert(tk.END, venda[10])

        def ao_fechar_popup_edicao():
            global popup_edicao_aberto 
            popup_edicao_aberto = None
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", ao_fechar_popup_edicao)

        def salvar_alteracoes():
            # Validação do campo Peças
            if not entry_pecas.get() or not entry_pecas.get().isdigit() or int(entry_pecas.get()) < 1:
                messagebox.showerror("Erro", "O campo Peças deve conter no mínimo 1 peça (valor numérico).")
                return

            # Obter valores dos campos
            pecas = entry_pecas.get()
            valor = entry_valor.get().replace("R$ ", "")
            haver = entry_haver.get().replace("R$ ", "")
            total_sacolinha = entry_total_sacolinha.get().replace("R$ ", "")
            adendo = text_adendo.get("1.0", tk.END).strip()

            conexao = conectar_banco_dados()
            if not conexao:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
            
            try:
                cursor = conexao.cursor()
                cursor.execute("UPDATE vendas SET peca=?, valor=?, haver=?, total_sacolinha=?, pago=?, tipo_pagamento=?, adendo=? WHERE data=? AND nome=?",
                                (pecas, valor, haver, total_sacolinha, combo_pago.get(), combo_tipo_pagamento.get(), adendo, venda[0], venda[1]))
                conexao.commit()
                desconectar_banco_dados(conexao)
                dados_atualizados = carregar_dados_vendas()
                exibir_dados_vendas(dados_atualizados)
                ao_fechar_popup_edicao()
            except sqlite3.Error as erro:
                messagebox.showerror("Erro", f"Erro ao atualizar venda: {erro}")
            finally:
                ao_fechar_popup_edicao()

        Button(popup, text="Salvar", command=salvar_alteracoes).grid(row=10, column=0, columnspan=2, pady=10)
        Button(popup, text="Cancelar", command=ao_fechar_popup_edicao).grid(row=11, column=0, columnspan=2, pady=5)

    tk.Label(frame_filtros, text="Data Início:").grid(row=0, column=2)
    entry_data_inicio = tk.Entry(frame_filtros)
    entry_data_inicio.grid(row=0, column=3)
    entry_data_inicio.bind("<Button-1>", abrir_calendario_inicio)  

    tk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=5)
    entry_data_fim = tk.Entry(frame_filtros)
    entry_data_fim.grid(row=0, column=6)
    entry_data_fim.bind("<Button-1>", abrir_calendario_fim)

    # Filtro Frete
    tk.Label(frame_filtros, text="Frete:").grid(row=1, column=0)
    opcoes_frete = ["Todos"] + list(set([venda[10] for venda in carregar_dados_vendas() if venda[9]]))
    combo_frete = ttk.Combobox(frame_filtros, values=opcoes_frete)
    combo_frete.grid(row=1, column=1)
    combo_frete.current(0) 

    # Filtro Pago
    tk.Label(frame_filtros, text="Pago:").grid(row=1, column=2)
    pago_sim_var = tk.IntVar()  
    pago_nao_var = tk.IntVar()  
    check_pago_sim = tk.Checkbutton(frame_filtros, text="Sim", variable=pago_sim_var)
    check_pago_sim.grid(row=1, column=3)
    check_pago_nao = tk.Checkbutton(frame_filtros, text="Não", variable=pago_nao_var)
    check_pago_nao.grid(row=1, column=4)

    btn_filtrar = tk.Button(frame_filtros, text="Filtrar", command=filtrar_vendas)
    btn_filtrar.grid(row=0, column=7, rowspan=2, padx=10) 
    btn_filtrar.config(width=10, height=2)  

    # Relatório de Vendas (Treeview)
    colunas_vendas = ("Data", "Nome", "Peças", "Valor", "1ª Peça", "Haver", "Total Sacolinha", "Pago", "Tipo de pagamento", "Frete", "Adendo")
    treeview_vendas = ttk.Treeview(nova_janela, columns=colunas_vendas, show="headings")
    treeview_vendas.bind("<Button-3>", editar_venda)
    for coluna in colunas_vendas:
        treeview_vendas.heading(coluna, text=coluna)
        treeview_vendas.column(coluna, width=100)
    treeview_vendas.tag_configure("pago_sim", background="#c8e6c9")  # Verde claro
    treeview_vendas.tag_configure("pago_nao", background="#ffcdd2")  # Vermelho claro
    treeview_vendas.tag_configure("roxo_claro", background="#e0b0ff")  # Roxo claro
    treeview_vendas.tag_configure("amarelo_claro", background="#fffacd")  # Amarelo claro
    treeview_vendas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Carregar e exibir dados iniciais
    dados_iniciais = carregar_dados_vendas()
    exibir_dados_vendas(dados_iniciais)
    ajustar_colunas(treeview_vendas)
    
    # Salvar configurações ao fechar a janela de Vendas
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_janela(nova_janela, "vendas"), nova_janela.destroy()))

if __name__ == "__main__":
    main()