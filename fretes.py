import tkinter as tk
from tkinter import ttk
from tkinter import Toplevel
import json
import os
from utils import salvar_configuracoes_janela, carregar_configuracoes

def main():
    nova_janela = tk.Toplevel()
    nova_janela.title("Fretes")

    # Carregar configurações ou definir padrão para a janela de Fretes
    configuracoes = carregar_configuracoes()
    if configuracoes and "fretes" in configuracoes:
        nova_janela.geometry(f"{configuracoes['fretes']['largura']}x{configuracoes['fretes']['altura']}+{configuracoes['fretes']['x']}+{configuracoes['fretes']['y']}")
    else:
        nova_janela.geometry("950x600")

    # Seleção de Cliente (Combobox)
    clientes_combobox = ttk.Combobox(nova_janela, values=[], state="readonly")  # Lista vazia por enquanto
    clientes_combobox.grid(row=0, column=0, padx=10, pady=10)

    # Campos de Dimensões
    tk.Label(nova_janela, text="Peso:").grid(row=0, column=1, padx=5, pady=5)
    peso_entry = tk.Entry(nova_janela)
    peso_entry.grid(row=0, column=2, padx=5, pady=5)

    tk.Label(nova_janela, text="Altura:").grid(row=1, column=1, padx=5, pady=5)
    altura_entry = tk.Entry(nova_janela)
    altura_entry.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(nova_janela, text="Largura:").grid(row=2, column=1, padx=5, pady=5)
    largura_entry = tk.Entry(nova_janela)
    largura_entry.grid(row=2, column=2, padx=5, pady=5)

    tk.Label(nova_janela, text="Comprimento:").grid(row=3, column=1, padx=5, pady=5)
    comprimento_entry = tk.Entry(nova_janela)
    comprimento_entry.grid(row=3, column=2, padx=5, pady=5)

    # Botão Criar Envio
    btn_criar_envio = tk.Button(nova_janela, text="Criar Envio")  # Sem comando por enquanto
    btn_criar_envio.grid(row=3, column=0, pady=10)

    # Relatório de Fretes (Treeview)
    colunas_fretes = ("ID", "Cliente", "CEP", "Peso", "Altura", "Largura", "Comprimento", "Seguro", "Pago")
    treeview_fretes = ttk.Treeview(nova_janela, columns=colunas_fretes, show="headings")
    for coluna in colunas_fretes:
        treeview_fretes.heading(coluna, text=coluna)
        treeview_fretes.column(coluna, width=100)
    treeview_fretes.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    # Salvar configurações ao fechar a janela de Fretes
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_janela(nova_janela, "fretes"), nova_janela.destroy()))

if __name__ == "__main__":
    main()