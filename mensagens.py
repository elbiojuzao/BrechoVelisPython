import tkinter as tk
from tkinter import Toplevel
import json
import os

def main():
    nova_janela = tk.Toplevel()
    nova_janela.title("Mensagens")

    # Carregar configurações ou definir padrão para a janela de Mensagens
    configuracoes = carregar_configuracoes()
    if configuracoes and "mensagens" in configuracoes:
        nova_janela.geometry(f"{configuracoes['mensagens']['largura']}x{configuracoes['mensagens']['altura']}+{configuracoes['mensagens']['x']}+{configuracoes['mensagens']['y']}")
    else:
        nova_janela.geometry("300x200")  # Tamanho padrão menor

    # Botões
    btn_15_30_dias = tk.Button(nova_janela, text="Compras de 15 a 30 dias")
    btn_15_30_dias.pack(pady=10)

    btn_mais_30_dias = tk.Button(nova_janela, text="Compras com +30 dias")
    btn_mais_30_dias.pack(pady=10)

    btn_mais_90_dias = tk.Button(nova_janela, text="Compras com +90 dias")
    btn_mais_90_dias.pack(pady=10)

    # Salvar configurações ao fechar a janela de Mensagens
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_mensagens(nova_janela), nova_janela.destroy()))

def salvar_configuracoes_mensagens(janela):
    configuracoes = carregar_configuracoes() or {}
    configuracoes["mensagens"] = {
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