import tkinter as tk
from tkinter import ttk, Toplevel
from datetime import datetime, timedelta
from utils import conectar_banco_dados, desconectar_banco_dados, salvar_configuracoes_janela, carregar_configuracoes

def criar_tela_mensagens(root):
    nova_janela = Toplevel(root)
    nova_janela.title("Mensagens")
    nova_janela.geometry("800x600")

    frame_principal = ttk.Frame(nova_janela)
    frame_principal.pack(fill=tk.BOTH, expand=True)

    frame_filtros = ttk.Frame(frame_principal)
    frame_filtros.pack(fill=tk.X)

    btn_15_30_dias = tk.Button(frame_filtros, text="Compras 15-30 dias", command=lambda: filtrar_vendas(tree_mensagens, 15, 30))
    btn_15_30_dias.pack(side=tk.LEFT, padx=5, pady=5)

    btn_mais_30_dias = tk.Button(frame_filtros, text="Compras +30 dias", command=lambda: filtrar_vendas(tree_mensagens, 30))
    btn_mais_30_dias.pack(side=tk.LEFT, padx=5, pady=5)

    btn_mais_90_dias = tk.Button(frame_filtros, text="Compras +90 dias", command=lambda: filtrar_vendas(tree_mensagens, 90))
    btn_mais_90_dias.pack(side=tk.LEFT, padx=5, pady=5)

    tree_mensagens = ttk.Treeview(frame_principal, columns=("Detalhes", "Data", "Nome", "Peca", "Valor"))
    tree_mensagens.heading("#0", text="Detalhes")
    tree_mensagens.heading("Data", text="Data")
    tree_mensagens.heading("Nome", text="Nome")
    tree_mensagens.heading("Peca", text="Peca")
    tree_mensagens.heading("Valor", text="Valor")

    tree_mensagens.pack(fill=tk.BOTH, expand=True)

    tree_mensagens.bind("<ButtonRelease-1>", lambda event: clique_treeview(event, tree_mensagens))

    nova_janela.protocol("WM_DELETE_WINDOW", nova_janela.destroy)

def filtrar_vendas(tree, dias, dias_fim=None):
    hoje = datetime.now().date()
    data_inicio = hoje - timedelta(days=dias)
    data_fim = hoje - timedelta(days=dias_fim) if dias_fim else None

    conexao = conectar_banco_dados()
    if conexao:
        cursor = conexao.cursor()
        try:
            if data_fim:
                cursor.execute("SELECT rowid, data, nome, peca, valor FROM vendas WHERE data BETWEEN ? AND ? AND pago = 'Sim' AND frete IN ('Espera', 'Embalar')",
                               (data_fim.strftime('%Y-%m-%d'), data_inicio.strftime('%Y-%m-%d')))
            else:
                cursor.execute("SELECT rowid, data, nome, peca, valor FROM vendas WHERE data <= ? AND pago = 'Sim' AND frete IN ('Espera', 'Embalar')",
                               (data_inicio.strftime('%Y-%m-%d'),))
            vendas = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")
            return
        finally:
            desconectar_banco_dados(conexao)

    for item in tree.get_children():
        tree.delete(item)

    for venda in vendas:
        try:
            data_formatada = datetime.strptime(venda[1], '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            print(f"Erro ao converter data: {venda[1]}")
            data_formatada = venda[1]  # Mantém a data original se a conversão falhar
        tree.insert("", tk.END, values=("[Detalhes]", data_formatada, venda[2], venda[3], venda[4]))

    ajustar_colunas(tree)  # Chama a função para ajustar as colunas

def clique_treeview(event, tree):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if item and column == "#1":
        detalhes = tree.item(item, "values")
        id_venda = tree.item(item, "text")
        print(f"Detalhes da venda (ID: {id_venda}): {detalhes}")

def main(root):
    criar_tela_mensagens(root)

def ajustar_colunas(tree):
    tree.update_idletasks()  # Atualiza a interface
    for col in tree["columns"]:
        max_width = 0
        for item in tree.get_children(""):
            try:
                width = tree.set(item, col).encode().decode('UTF-8')
                # width = tree.set(item, col) #Original
                width = tk.font.Font().measure(width)
                if width > max_width:
                    max_width = width
            except:
                pass
        if max_width < tree.column(col, 'width'):
           pass
        else:
           tree.column(col, width=max_width)

if __name__ == "__main__":
    root = tk.Tk()
    main(root)
    root.mainloop()