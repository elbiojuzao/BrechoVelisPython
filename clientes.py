import tkinter as tk
from tkinter import ttk
from tkinter import Toplevel
import sqlite3
import json
import os

def main():
    nova_janela = tk.Toplevel()
    nova_janela.title("Clientes") #alterado

    # Carregar configurações ou definir padrão para a janela de Clientes
    configuracoes = carregar_configuracoes()
    if configuracoes and "clientes" in configuracoes: #alterado
        nova_janela.geometry(f"{configuracoes['clientes']['largura']}x{configuracoes['clientes']['altura']}+{configuracoes['clientes']['x']}+{configuracoes['clientes']['y']}") #alterado
    else:
        nova_janela.geometry("1250x600")

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

    def carregar_dados_clientes():
        conexao = conectar_banco_dados()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT * FROM clientes")
                dados_clientes = cursor.fetchall()
                desconectar_banco_dados(conexao)
                return dados_clientes
            except sqlite3.Error as erro:
                print("Erro na consulta SQL:", erro)
                return []
        else:
            return []

    def exibir_dados_clientes(dados_clientes):
        for item in treeview_clientes.get_children():
            treeview_clientes.delete(item)
        for cliente in dados_clientes:
            cliente_sem_id = []
            for valor in cliente[1:]:  # Ignora o ID
                if valor is None:
                    cliente_sem_id.append("")  # Substitui None por ""
                else:
                    cliente_sem_id.append(valor)
            treeview_clientes.insert("", tk.END, values=cliente_sem_id)

    def filtrar_clientes():
        nome_filtro = nome_entry.get().lower()
        nome_completo_filtro = nome_completo_entry.get().lower()
        celular_filtro = celular_entry.get()
        cep_filtro = cep_entry.get()

        dados_filtrados = []
        for cliente in dados_iniciais:
            nome = cliente[1]
            nome_completo = cliente[3]
            celular = cliente[4]
            cep = cliente[2]

            # Tratamento para valores None
            nome = nome.lower() if nome else ""
            nome_completo = nome_completo.lower() if nome_completo else ""
            celular = str(celular) if celular else ""
            cep = str(cep) if cep else ""

            if (nome_filtro in nome and
                nome_completo_filtro in nome_completo and
                celular_filtro in celular and
                cep_filtro in cep):
                dados_filtrados.append(cliente)

        exibir_dados_clientes(dados_filtrados)

    # Filtros
    filtro_frame = tk.Frame(nova_janela)
    filtro_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Campos de entrada para cada filtro em linha
    tk.Label(filtro_frame, text="Nome:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
    nome_entry = tk.Entry(filtro_frame, font=("Arial", 12))
    nome_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filtro_frame, text="Nome Completo:", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5)
    nome_completo_entry = tk.Entry(filtro_frame, font=("Arial", 12))
    nome_completo_entry.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(filtro_frame, text="Celular:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
    celular_entry = tk.Entry(filtro_frame, font=("Arial", 12))
    celular_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(filtro_frame, text="CEP:", font=("Arial", 12)).grid(row=1, column=2, padx=5, pady=5)
    cep_entry = tk.Entry(filtro_frame, font=("Arial", 12))
    cep_entry.grid(row=1, column=3, padx=5, pady=5)

    btn_filtrar = tk.Button(filtro_frame, text="Filtrar", command=filtrar_clientes, font=("Arial", 12))
    btn_filtrar.grid(row=2, column=0, columnspan=4, pady=10)

    # Relatório de Clientes (Treeview)
    colunas_clientes = ("nome", "cep", "nome_completo", "celular", "email", "cpf", "rua", "numero", "complemento", "bairro", "cidade")
    treeview_clientes = ttk.Treeview(nova_janela, columns=colunas_clientes, show="headings")
    for coluna in colunas_clientes:
        treeview_clientes.heading(coluna, text=coluna)
        treeview_clientes.column(coluna, width=100)
    treeview_clientes.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    # Carregar e exibir dados iniciais
    dados_iniciais = carregar_dados_clientes()
    exibir_dados_clientes(dados_iniciais)

    # Salvar configurações ao fechar a janela de Clientes
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_clientes(nova_janela), nova_janela.destroy())) #alterado

def salvar_configuracoes_clientes(janela): #alterado
    configuracoes = carregar_configuracoes() or {}
    configuracoes["clientes"] = { #alterado
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