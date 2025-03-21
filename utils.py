import sqlite3
import json
import tkinter as tk

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

def salvar_configuracoes_janela(janela, nome_secao):
    configuracoes = carregar_configuracoes() or {}
    configuracoes[nome_secao] = {
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
    
def ajustar_colunas(tree):
    tree.update_idletasks()
    for col in tree["columns"]:
        max_width = 0
        for item in tree.get_children(""):
            width = tree.set(item, col)
            if isinstance(width, str):
                width = tk.font.Font().measure(width)
                if width > max_width:
                    max_width = width
        if max_width < tree.column(col, 'width'):
            pass
        else:
            tree.column(col, width=max_width)

def formatar_valor_monetario(valor):
    if valor is None:
        return ""
    try:
        valor_float = float(str(valor).replace(",", "."))
        return f"R$ {valor_float:.2f}"
    except ValueError:
        print(f"Valor inválido encontrado: {valor}")
        return "R$ 0.00" 
    
