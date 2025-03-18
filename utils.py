import sqlite3
import json

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