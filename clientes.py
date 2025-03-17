import tkinter as tk
from tkinter import ttk
from tkinter import Toplevel, messagebox, Button 
import sqlite3
import json
from datetime import datetime

def main():
    nova_janela = tk.Toplevel()
    nova_janela.title("Clientes") 

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

    def editar_cliente(event):
        item = treeview_clientes.selection()[0]
        cliente = treeview_clientes.item(item, 'values')

        popup = Toplevel(nova_janela)
        popup.title("Editar Cliente")

        # Obter coordenadas do cursor
        x = event.x_root
        y = event.y_root

        # Posicionar o popup nas coordenadas do cursor
        popup.geometry(f"+{x}+{y}")

        # Campos editáveis
        tk.Label(popup, text="Nome:").grid(row=0, column=0)
        entry_nome = tk.Entry(popup)
        entry_nome.grid(row=0, column=1)
        entry_nome.insert(0, cliente[0])

        tk.Label(popup, text="CEP:").grid(row=1, column=0)
        entry_cep = tk.Entry(popup)
        entry_cep.grid(row=1, column=1)
        entry_cep.insert(0, cliente[1])

        tk.Label(popup, text="Nome Completo:").grid(row=2, column=0)
        entry_nome_completo = tk.Entry(popup)
        entry_nome_completo.grid(row=2, column=1)
        entry_nome_completo.insert(0, cliente[2])

        tk.Label(popup, text="Telefone:").grid(row=3, column=0)
        entry_celular = tk.Entry(popup)
        entry_celular.grid(row=3, column=1)
        entry_celular.insert(0, cliente[3])

        tk.Label(popup, text="Email:").grid(row=4, column=0)
        entry_email = tk.Entry(popup)
        entry_email.grid(row=4, column=1)
        entry_email.insert(0, cliente[4])

        tk.Label(popup, text="CPF:").grid(row=5, column=0)
        entry_cpf = tk.Entry(popup)
        entry_cpf.grid(row=5, column=1)
        entry_cpf.insert(0, cliente[5])

        tk.Label(popup, text="Rua:").grid(row=6, column=0)
        entry_rua = tk.Entry(popup)
        entry_rua.grid(row=6, column=1)
        entry_rua.insert(0, cliente[6])

        tk.Label(popup, text="Número:").grid(row=7, column=0)
        entry_numero = tk.Entry(popup)
        entry_numero.grid(row=7, column=1)
        entry_numero.insert(0, cliente[7])

        tk.Label(popup, text="Complemento:").grid(row=8, column=0)
        entry_complemento = tk.Entry(popup)
        entry_complemento.grid(row=8, column=1)
        entry_complemento.insert(0, cliente[8])

        tk.Label(popup, text="Bairro:").grid(row=9, column=0)
        entry_bairro = tk.Entry(popup)
        entry_bairro.grid(row=9, column=1)
        entry_bairro.insert(0, cliente[9])

        tk.Label(popup, text="Cidade:").grid(row=10, column=0)
        entry_cidade = tk.Entry(popup)
        entry_cidade.grid(row=10, column=1)
        entry_cidade.insert(0, cliente[10])

        def salvar_alteracoes_cliente():
            conexao = conectar_banco_dados()
            if conexao:
                try:
                        cursor = conexao.cursor()
                        data_hora_modificacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        # Recupera o id do cliente pelo nome
                        cursor.execute("SELECT id FROM clientes WHERE nome=?", (cliente[0],))
                        id_cliente = cursor.fetchone()[0]
                        cursor.execute("UPDATE clientes SET nome=?, cep=?, nome_completo=?, Celular=?, Email=?, CPF=?, Rua=?, num=?, Complemento=?, Bairro=?, Cidade=?, data_hora_modificacao=? WHERE id=?",
                            (entry_nome.get(), entry_cep.get(), entry_nome_completo.get(), entry_celular.get(), entry_email.get(), entry_cpf.get(), entry_rua.get(), entry_numero.get(), entry_complemento.get(), entry_bairro.get(), entry_cidade.get(), data_hora_modificacao, id_cliente))
                        conexao.commit()
                        desconectar_banco_dados(conexao)
                        dados_atualizados = carregar_dados_clientes()
                        exibir_dados_clientes(dados_atualizados)
                        popup.destroy()
                except sqlite3.Error as erro:
                    messagebox.showerror("Erro", f"Erro ao atualizar cliente: {erro}")
            else:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")

        Button(popup, text="Salvar", command=salvar_alteracoes_cliente).grid(row=11, column=0, columnspan=2)

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
    treeview_clientes.bind("<Button-3>", editar_cliente) 
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