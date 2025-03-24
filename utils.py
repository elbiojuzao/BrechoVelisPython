import sqlite3
import json
import customtkinter as ctk 

def conectar_banco_dados():
    try:
        conexao = sqlite3.connect('brechoVelis.db')
        return conexao
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def desconectar_banco_dados(conexao):
    if conexao:
        conexao.close()

def salvar_configuracoes_janela(janela, nome_secao):
    try:
        configuracoes = carregar_configuracoes()
        configuracoes[nome_secao] = {
            "x": janela.winfo_x(),
            "y": janela.winfo_y(),
            "width": janela.winfo_width(),
            "height": janela.winfo_height()
        }
        salvar_configuracoes(configuracoes)
    except Exception as e:
        print(f"Erro ao salvar configurações da janela: {e}")

def salvar_configuracoes(configuracoes):
    try:
        with open("configuracoes.json", "w") as arquivo:
            json.dump(configuracoes, arquivo)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")

def carregar_configuracoes():
    try:
        with open("configuracoes.json", "r") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return {}

def ajustar_colunas(tree):
    for coluna in tree["columns"]:
        tree.column(coluna, anchor="w", stretch=False)
        tree.heading(coluna, anchor="w")

def formatar_valor_monetario(valor):
    if valor is None:
        return "R$ 0.00"
    try:
        valor_float = float(str(valor).replace(",", "."))
        return f"R$ {valor_float:.2f}"
    except ValueError:
        print(f"Valor inválido encontrado: {valor}")
        return "R$ 0.00"