import tkinter as tk
from tkinter import ttk, Toplevel
from utils import salvar_configuracoes_janela, carregar_configuracoes, conectar_banco_dados, desconectar_banco_dados
from datetime import datetime, timedelta

def criar_tela_mensagens(root):
    nova_janela = Toplevel(root)
    nova_janela.title("Mensagens")

    # Carregar configurações ou definir padrão para a janela de Mensagens
    configuracoes = carregar_configuracoes()
    if configuracoes and "mensagens" in configuracoes:
        nova_janela.geometry(f"{configuracoes['mensagens']['largura']}x{configuracoes['mensagens']['altura']}+{configuracoes['mensagens']['x']}+{configuracoes['mensagens']['y']}")
    else:
        nova_janela.geometry("800x600")

    # Frame principal
    frame_principal = ttk.Frame(nova_janela)
    frame_principal.pack(fill=tk.BOTH, expand=True)

    # Frame para os botões de filtro
    frame_filtros = ttk.Frame(frame_principal)
    frame_filtros.pack(fill=tk.X)

    # Botões de filtro na horizontal
    btn_15_30_dias = tk.Button(frame_filtros, text="Compras 15-30 dias", command=lambda: filtrar_vendas(15, 30, tree_mensagens))
    btn_15_30_dias.pack(side=tk.LEFT, padx=5, pady=5)

    btn_mais_30_dias = tk.Button(frame_filtros, text="Compras +30 dias", command=lambda: filtrar_vendas(None, 30, tree_mensagens))
    btn_mais_30_dias.pack(side=tk.LEFT, padx=5, pady=5)

    btn_mais_90_dias = tk.Button(frame_filtros, text="Compras +90 dias", command=lambda: filtrar_vendas(None, 90, tree_mensagens))
    btn_mais_90_dias.pack(side=tk.LEFT, padx=5, pady=5)

    # Treeview para exibir mensagens
    tree_mensagens = ttk.Treeview(frame_principal, columns=("Detalhes", "Data", "Nome", "Peca", "Valor")) 
    tree_mensagens.heading("Detalhes", text="Detalhes")
    tree_mensagens.heading("Data", text="Data")
    tree_mensagens.heading("Nome", text="Nome")
    tree_mensagens.heading("Peca", text="Peca")  
    tree_mensagens.heading("Valor", text="Valor")
    tree_mensagens.pack(fill=tk.BOTH, expand=True)

    # Evento de clique na Treeview
    tree_mensagens.bind("<ButtonRelease-1>", lambda event: clique_treeview(event, tree_mensagens))

    # Salvar configurações ao fechar a janela de Mensagens
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_janela(nova_janela, "mensagens"), nova_janela.destroy()))

def filtrar_vendas(dias_min, dias_max, tree):
    hoje = datetime.now().date()
    data_inicio = hoje - timedelta(days=dias_min) if dias_min else None
    data_fim = hoje - timedelta(days=dias_max) if dias_max else None

    conexao = conectar_banco_dados()
    if conexao:
        cursor = conexao.cursor()
        if dias_max:
            cursor.execute("SELECT rowid, data, nome, peca, valor FROM vendas WHERE data BETWEEN ? AND ?",
                           (data_fim, data_inicio))  
        else:
            cursor.execute("SELECT rowid, data, nome, peca, valor FROM vendas WHERE data <= ?",
                           (data_inicio,)) 
        vendas = cursor.fetchall()
        desconectar_banco_dados(conexao)

        # Limpar a Treeview
        for item in tree.get_children():
            tree.delete(item)

        # Inserir as vendas na Treeview
        for venda in vendas:
            tree.insert("", tk.END, values=("[Detalhes]", venda[1], venda[2], venda[3], venda[4]))

def clique_treeview(event, tree):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if item and column == "#1":  # Coluna "Detalhes"
        detalhes = tree.item(item, "values")
        id_venda = tree.item(item, "text")  # Recupera o ID da venda
        print(f"Detalhes da venda (ID: {id_venda}): {detalhes}")

def main(root):
    criar_tela_mensagens(root)

if __name__ == "__main__":
    root = tk.Tk()
    main(root)
    root.mainloop()