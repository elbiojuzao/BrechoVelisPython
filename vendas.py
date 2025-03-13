import tkinter as tk
from tkinter import ttk
import sqlite3
import json

def main():
    nova_janela = tk.Toplevel()
    nova_janela.title("Vendas")

    # Carregar configurações ou definir padrão para a janela de Vendas
    configuracoes = carregar_configuracoes()
    if configuracoes and "vendas" in configuracoes:
        nova_janela.geometry(f"{configuracoes['vendas']['largura']}x{configuracoes['vendas']['altura']}+{configuracoes['vendas']['x']}+{configuracoes['vendas']['y']}")
    else:
        nova_janela.geometry("800x600")

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
            treeview_vendas.insert("", tk.END, values=venda)

    # Relatório de Vendas (Treeview)
    colunas_vendas = ("id", "data", "nome", "quantidade", "valor da sacolinha")  # Adapte as colunas conforme sua tabela
    treeview_vendas = ttk.Treeview(nova_janela, columns=colunas_vendas, show="headings")
    for coluna in colunas_vendas:
        treeview_vendas.heading(coluna, text=coluna)
        treeview_vendas.column(coluna, width=100)
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