import customtkinter as ctk
import psycopg2 
import sqlite3
from datetime import datetime
from utils import conectar_banco_dados, desconectar_banco_dados, salvar_configuracoes_janela, carregar_configuracoes
from tkinter import ttk

def main(dark_mode=False):
    nova_janela = ctk.CTkToplevel()
    nova_janela.title("Clientes")

    if dark_mode:
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")

    # Carregar configurações ou definir padrão para a janela de Clientes
    configuracoes = carregar_configuracoes()
    if configuracoes and "clientes" in configuracoes:
        try:
            nova_janela.geometry(f"{configuracoes['clientes']['largura']}x{configuracoes['clientes']['altura']}+{configuracoes['clientes']['x']}+{configuracoes['clientes']['y']}")
        except KeyError:
            nova_janela.geometry("1250x600")
    else:
        nova_janela.geometry("1250x600")

    nova_janela.grid_rowconfigure(1, weight=1)
    nova_janela.grid_columnconfigure(0, weight=1)

    tabview = ctk.CTkTabview(nova_janela)
    tabview.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

    tabview.add("Clientes")

    tree_clientes = ttk.Treeview(tabview.tab("Clientes"), columns=("Nome", "CEP", "Nome Completo", "Celular", "Email", "CPF", "Rua", "Número", "Complemento", "Bairro", "Cidade"), show="headings")
    tree_clientes.pack(fill="both", expand=True)

    for coluna in ("Nome", "CEP", "Nome Completo", "Celular", "Email", "CPF", "Rua", "Número", "Complemento", "Bairro", "Cidade"):
        tree_clientes.heading(coluna, text=coluna)
        tree_clientes.column(coluna, width=100) # Ajuste a largura das colunas conforme necessário

    def carregar_dados_clientes():
        conexao = conectar_banco_dados()
        if not conexao:
            return []
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, nome, cep, nome_completo, celular, email, cpf, rua, num, complemento, bairro, cidade FROM clientes")  # Adapte a consulta se necessário
            dados_clientes = cursor.fetchall()
            desconectar_banco_dados(conexao)
            return dados_clientes
        except psycopg2.Error as erro:
            print("Erro na consulta SQL (PostgreSQL):", erro)
            return []

    def exibir_dados_clientes(dados_clientes):
        tree_clientes.delete(*tree_clientes.get_children()) # Limpa os dados existentes
        for cliente in dados_clientes:
            if len(cliente) >= 12:
                linha = [str(cliente[i]) if cliente[i] is not None else "" for i in range(1, 12)]
                tree_clientes.insert("", "end", values=linha)
            else:
                print(f"Aviso: Registro de cliente com número incorreto de colunas: {cliente}")

    dados_iniciais = carregar_dados_clientes()
    exibir_dados_clientes(dados_iniciais)

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
        # Obter a linha clicada
        linha_clicada = tree_clientes.focus()
        if not linha_clicada:
            return # Nenhuma linha selecionada

        # Obter os valores da linha clicada
        dados_cliente = tree_clientes.item(linha_clicada, "values")

        # Criar janela de edição
        popup = ctk.CTkToplevel(nova_janela)
        popup.title("Editar Cliente")

        # Obter coordenadas do cursor
        x = event.x_root
        y = event.y_root

        # Posicionar o popup nas coordenadas do cursor
        popup.geometry(f"+{x}+{y}")

        # Campos editáveis
        ctk.CTkLabel(popup, text="Nome:").grid(row=0, column=0)
        entry_nome = ctk.CTkEntry(popup)
        entry_nome.grid(row=0, column=1)
        entry_nome.insert(0, dados_cliente[0]) # Nome

        ctk.CTkLabel(popup, text="CEP:").grid(row=1, column=0)
        entry_cep = ctk.CTkEntry(popup)
        entry_cep.grid(row=1, column=1)
        entry_cep.insert(0, dados_cliente[1]) # CEP

        ctk.CTkLabel(popup, text="Nome Completo:").grid(row=2, column=0)
        entry_nome_completo = ctk.CTkEntry(popup)
        entry_nome_completo.grid(row=2, column=1)
        entry_nome_completo.insert(0, dados_cliente[2])  # Nome Completo

        ctk.CTkLabel(popup, text="Telefone:").grid(row=3, column=0)
        entry_celular = ctk.CTkEntry(popup)
        entry_celular.grid(row=3, column=1)
        entry_celular.insert(0, dados_cliente[3])  # Telefone

        ctk.CTkLabel(popup, text="Email:").grid(row=4, column=0)
        entry_email = ctk.CTkEntry(popup)
        entry_email.grid(row=4, column=1)
        entry_email.insert(0, dados_cliente[4])  # Email

        ctk.CTkLabel(popup, text="CPF:").grid(row=5, column=0)
        entry_cpf = ctk.CTkEntry(popup)
        entry_cpf.grid(row=5, column=1)
        entry_cpf.insert(0, dados_cliente[5])  # CPF

        ctk.CTkLabel(popup, text="Rua:").grid(row=6, column=0)
        entry_rua = ctk.CTkEntry(popup)
        entry_rua.grid(row=6, column=1)
        entry_rua.insert(0, dados_cliente[6])  # Rua

        ctk.CTkLabel(popup, text="Número:").grid(row=7, column=0)
        entry_numero = ctk.CTkEntry(popup)
        entry_numero.grid(row=7, column=1)
        entry_numero.insert(0, dados_cliente[7])  # Número

        ctk.CTkLabel(popup, text="Complemento:").grid(row=8, column=0)
        entry_complemento = ctk.CTkEntry(popup)
        entry_complemento.grid(row=8, column=1)
        entry_complemento.insert(0, dados_cliente[8])  # Complemento

        ctk.CTkLabel(popup, text="Bairro:").grid(row=9, column=0)
        entry_bairro = ctk.CTkEntry(popup)
        entry_bairro.grid(row=9, column=1)
        entry_bairro.insert(0, dados_cliente[9])  # Bairro

        ctk.CTkLabel(popup, text="Cidade:").grid(row=10, column=0)
        entry_cidade = ctk.CTkEntry(popup)
        entry_cidade.grid(row=10, column=1)
        entry_cidade.insert(0, dados_cliente[10])  # Cidade

        def salvar_alteracoes_cliente():
            conexao = conectar_banco_dados()
            if not conexao:
                ctk.CTkMessagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")

            try:
                cursor = conexao.cursor()
                data_hora_modificacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                # Recupera o id do cliente pelo nome
                cursor.execute("SELECT id FROM clientes WHERE nome=?", (dados_cliente[0],))
                id_cliente = cursor.fetchone()[0]
                cursor.execute("UPDATE clientes SET nome=?, cep=?, nome_completo=?, Celular=?, Email=?, CPF=?, Rua=?, num=?, Complemento=?, Bairro=?, Cidade=?, data_hora_modificacao=? WHERE id=?",
                               (entry_nome.get(), entry_cep.get(), entry_nome_completo.get(), entry_celular.get(), entry_email.get(), entry_cpf.get(), entry_rua.get(), entry_numero.get(), entry_complemento.get(), entry_bairro.get(), entry_cidade.get(), data_hora_modificacao, id_cliente))
                conexao.commit()
                desconectar_banco_dados(conexao)
                dados_atualizados = carregar_dados_clientes()
                exibir_dados_clientes(dados_atualizados)
                popup.destroy()
            except sqlite3.Error as erro:
                ctk.CTkMessagebox.showerror("Erro", f"Erro ao atualizar cliente: {erro}")

        ctk.CTkButton(popup, text="Salvar", command=salvar_alteracoes_cliente).grid(row=11, column=0, columnspan=2)

    # Filtros
    filtro_frame = ctk.CTkFrame(nova_janela)
    filtro_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Campos de entrada para cada filtro em linha
    ctk.CTkLabel(filtro_frame, text="Nome:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
    nome_entry = ctk.CTkEntry(filtro_frame, font=("Arial", 12))
    nome_entry.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(filtro_frame, text="Nome Completo:", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5)
    nome_completo_entry = ctk.CTkEntry(filtro_frame, font=("Arial", 12))
    nome_completo_entry.grid(row=0, column=3, padx=5, pady=5)

    ctk.CTkLabel(filtro_frame, text="Celular:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
    celular_entry = ctk.CTkEntry(filtro_frame, font=("Arial", 12))
    celular_entry.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(filtro_frame, text="CEP:", font=("Arial", 12)).grid(row=1, column=2, padx=5, pady=5)
    cep_entry = ctk.CTkEntry(filtro_frame, font=("Arial", 12))
    cep_entry.grid(row=1, column=3, padx=5, pady=5)

    btn_filtrar = ctk.CTkButton(filtro_frame, text="Filtrar", command=filtrar_clientes, font=("Arial", 12))
    btn_filtrar.grid(row=2, column=0, columnspan=4, pady=10)

    # Botão "Novo Cliente"
    btn_novo_cliente = ctk.CTkButton(filtro_frame, text="Novo Cliente", command=lambda: criar_janela_cadastro_cliente(tree_clientes), font=("Arial", 12))
    btn_novo_cliente.grid(row=1, column=4, padx=2, pady=2)

    # Carregar e exibir dados iniciais
    dados_iniciais = carregar_dados_clientes()
    exibir_dados_clientes(dados_iniciais)

    # Salvar configurações ao fechar a janela de Clientes
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_janela(nova_janela, "clientes"), nova_janela.destroy()))

    def criar_janela_cadastro_cliente(tree_clientes):
        janela_cadastro = ctk.CTkToplevel()
        janela_cadastro.title("Cadastro de Cliente")

        # Campos de cadastro
        ctk.CTkLabel(janela_cadastro, text="Nome:").grid(row=0, column=0)
        entry_nome = ctk.CTkEntry(janela_cadastro)
        entry_nome.grid(row=0, column=1)

        ctk.CTkLabel(janela_cadastro, text="CEP:").grid(row=1, column=0)
        entry_cep = ctk.CTkEntry(janela_cadastro)
        entry_cep.grid(row=1, column=1)

        ctk.CTkLabel(janela_cadastro, text="Nome Completo:").grid(row=2, column=0)
        entry_nome_completo = ctk.CTkEntry(janela_cadastro)
        entry_nome_completo.grid(row=2, column=1)

        ctk.CTkLabel(janela_cadastro, text="Telefone:").grid(row=3, column=0)
        entry_celular = ctk.CTkEntry(janela_cadastro)
        entry_celular.grid(row=3, column=1)

        ctk.CTkLabel(janela_cadastro, text="Email:").grid(row=4, column=0)
        entry_email = ctk.CTkEntry(janela_cadastro)
        entry_email.grid(row=4, column=1)

        ctk.CTkLabel(janela_cadastro, text="CPF:").grid(row=5, column=0)
        entry_cpf = ctk.CTkEntry(janela_cadastro)
        entry_cpf.grid(row=5, column=1)

        ctk.CTkLabel(janela_cadastro, text="Rua:").grid(row=6, column=0)
        entry_rua = ctk.CTkEntry(janela_cadastro)
        entry_rua.grid(row=6, column=1)

        ctk.CTkLabel(janela_cadastro, text="Número:").grid(row=7, column=0)
        entry_numero = ctk.CTkEntry(janela_cadastro)
        entry_numero.grid(row=7, column=1)

        ctk.CTkLabel(janela_cadastro, text="Complemento:").grid(row=8, column=0)
        entry_complemento = ctk.CTkEntry(janela_cadastro)
        entry_complemento.grid(row=8, column=1)

        ctk.CTkLabel(janela_cadastro, text="Bairro:").grid(row=9, column=0)
        entry_bairro = ctk.CTkEntry(janela_cadastro)
        entry_bairro.grid(row=9, column=1)

        ctk.CTkLabel(janela_cadastro, text="Cidade:").grid(row=10, column=0)
        entry_cidade = ctk.CTkEntry(janela_cadastro)
        entry_cidade.grid(row=10, column=1)

        def salvar_novo_cliente():
            conexao = conectar_banco_dados()
            if not conexao:
                ctk.CTkMessagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")

            try:
                cursor = conexao.cursor()
                data_hora_modificacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cursor.execute("INSERT INTO clientes (nome, cep, nome_completo, Celular, Email, CPF, Rua, num, Complemento, Bairro, Cidade, data_hora_modificacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (entry_nome.get(), entry_cep.get(), entry_nome_completo.get(), entry_celular.get(), entry_email.get(), entry_cpf.get(), entry_rua.get(), entry_numero.get(), entry_complemento.get(), entry_bairro.get(), entry_cidade.get(), data_hora_modificacao))
                conexao.commit()
                desconectar_banco_dados(conexao)
                dados_atualizados = carregar_dados_clientes()
                exibir_dados_clientes(dados_atualizados)
                janela_cadastro.destroy()
            except sqlite3.Error as erro:
                ctk.CTkMessagebox.showerror("Erro", f"Erro ao cadastrar cliente: {erro}")

        ctk.CTkButton(janela_cadastro, text="Salvar", command=salvar_novo_cliente).grid(row=11, column=0, columnspan=2)