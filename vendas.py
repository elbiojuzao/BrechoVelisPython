import tkinter as tk
from tkinter import ttk
import sqlite3
import json
import csv
from tkinter import filedialog, messagebox, Toplevel, Button
from tkcalendar import Calendar
from datetime import datetime

def main():
    nova_janela = tk.Toplevel()
    nova_janela.title("Vendas")

    # Carregar configurações ou definir padrão para a janela de Vendas
    configuracoes = carregar_configuracoes()
    if configuracoes and "vendas" in configuracoes:
        nova_janela.geometry(f"{configuracoes['vendas']['largura']}x{configuracoes['vendas']['altura']}+{configuracoes['vendas']['x']}+{configuracoes['vendas']['y']}")
    else:
        nova_janela.geometry("1100x600")

    def conectar_banco_dados():
        try:
            conexao = sqlite3.connect("brechoVelis.db")
            return conexao
        except sqlite3.Error as erro:
            print("Erro ao conectar ao banco de dados:", erro)
            return None

    def desconectar_banco_dados(conexao):
        if conexao:
            conexao.close()

    def carregar_dados_vendas():
        conexao = conectar_banco_dados()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT * FROM vendas")
                dados_vendas = cursor.fetchall()
                desconectar_banco_dados(conexao)
                return dados_vendas
            except sqlite3.Error as erro:
                print("Erro na consulta SQL:", erro)
                return []
        else:
            return []

    def exibir_dados_vendas(dados_vendas):
        for item in treeview_vendas.get_children():
            treeview_vendas.delete(item)
        for venda in dados_vendas:
            venda_tratada = []
            for valor in (venda[1], venda[2], venda[3], venda[4], venda[5], venda[6], venda[7], venda[8], venda[9], venda[10], venda[11]):
                if valor is None:
                    venda_tratada.append("")  # Substitui None por ""
                else:
                    venda_tratada.append(valor)
            if venda_tratada[7] == "Não":  # Vermelho (prioridade máxima)
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("pago_nao",))
            elif venda_tratada[9] == "Enviado" or venda_tratada[9] == "Em mãos" or venda_tratada[9] == "DOAÇÃO":  # Roxo
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("roxo_claro",))
            elif venda_tratada[9] == "Embalar":  # Amarelo
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("amarelo_claro",))
            elif venda_tratada[7] == "Sim":  # Verde
                treeview_vendas.insert("", tk.END, values=venda_tratada, tags=("pago_sim",))

    def importar_compras():
        arquivo_csv = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if arquivo_csv:
            conexao = conectar_banco_dados()
            if conexao:
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
            else:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
        else:
            messagebox.showerror("Erro", "Nenhum arquivo CSV selecionado.")

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
        cal = Calendar(popup, date_pattern="yyyy-mm-dd")
        cal.pack()
        Button(popup, text="Selecionar", command=lambda: selecionar_data(cal.get_date(), entry_data_inicio, popup)).pack()

    def abrir_calendario_fim(event=None):
        x = entry_data_fim.winfo_rootx() + entry_data_fim.winfo_width()
        y = entry_data_fim.winfo_rooty()
        popup = Toplevel(frame_filtros)
        popup.geometry(f"+{x}+{y}")
        cal = Calendar(popup, date_pattern="yyyy-mm-dd")
        cal.pack()
        Button(popup, text="Selecionar", command=lambda: selecionar_data(cal.get_date(), entry_data_fim, popup)).pack()

    def selecionar_data(data, entry, popup):
        entry.delete(0, tk.END)
        entry.insert(0, data)
        popup.destroy()

    tk.Label(frame_filtros, text="Data Início:").grid(row=0, column=2)
    entry_data_inicio = tk.Entry(frame_filtros)
    entry_data_inicio.grid(row=0, column=3)
    entry_data_inicio.bind("<Button-1>", abrir_calendario_inicio)  # Adiciona evento de clique

    tk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=5)
    entry_data_fim = tk.Entry(frame_filtros)
    entry_data_fim.grid(row=0, column=6)
    entry_data_fim.bind("<Button-1>", abrir_calendario_fim)  # Adiciona evento de clique

    # Filtro Frete
    tk.Label(frame_filtros, text="Frete:").grid(row=1, column=0)
    opcoes_frete = ["Todos"] + list(set([venda[9] for venda in carregar_dados_vendas() if venda[9]]))
    combo_frete = ttk.Combobox(frame_filtros, values=opcoes_frete)
    combo_frete.grid(row=1, column=1)
    combo_frete.current(0)  # Seleciona "Todos" por padrão

    # Filtro Pago
    tk.Label(frame_filtros, text="Pago:").grid(row=1, column=2)
    check_pago_sim = tk.Checkbutton(frame_filtros, text="Sim")
    check_pago_sim.grid(row=1, column=3)
    check_pago_nao = tk.Checkbutton(frame_filtros, text="Não")
    check_pago_nao.grid(row=1, column=4)

    # Relatório de Vendas (Treeview)
    colunas_vendas = ("Data", "Nome", "Peças", "Valor", "1ª Peça", "Haver", "Total Sacolinha", "Pago", "Tipo de pagamento", "Frete", "Adendo")
    treeview_vendas = ttk.Treeview(nova_janela, columns=colunas_vendas, show="headings")
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

    # Salvar configurações ao fechar a janela de Vendas
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_vendas(nova_janela), nova_janela.destroy()))

def salvar_configuracoes_vendas(janela):
    configuracoes = carregar_configuracoes() or {}
    configuracoes["vendas"] = {
        "x": janela.winfo_x(),
        "y": janela.winfo_y(),
        "largura": janela.winfo_width(),
        "altura": janela.winfo_height()
    }
    with open("configuracoes.json", "w") as arquivo:
        json.dump(configuracoes, arquivo)

def carregar_configuracoes():
    try:
        with open("configuracoes.json", "r") as arquivo:
            configuracoes = json.load(arquivo)
            return configuracoes
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    main()