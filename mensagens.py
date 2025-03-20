import tkinter as tk
from tkinter import ttk, Toplevel
from datetime import datetime, timedelta
import webbrowser
from utils import conectar_banco_dados, desconectar_banco_dados, salvar_configuracoes_janela, carregar_configuracoes


def main(root):
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

    tree_mensagens = ttk.Treeview(frame_principal, columns=("ID", "Enviar", "Data", "Nome", "Peca", "Valor"))
    tree_mensagens.heading("ID", text="ID")
    tree_mensagens.heading("Enviar", text="Enviar")
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
                cursor.execute("""
                    SELECT
                        v.cliente_id,
                        c.nome,
                        MAX(v.data) AS ultima_data,
                        SUM(v.peca) AS total_pecas,
                        SUM(v.valor) AS total_valor
                    FROM vendas v
                    JOIN clientes c ON v.cliente_id = c.id
                    WHERE v.data BETWEEN ? AND ? AND v.pago = 'Sim' AND v.frete IN ('Espera', 'Embalar')
                    GROUP BY v.cliente_id
                """, (data_fim.strftime('%Y-%m-%d'), data_inicio.strftime('%Y-%m-%d')))
            else:
                cursor.execute("""
                    SELECT
                        v.cliente_id,
                        c.nome,
                        MAX(v.data) AS ultima_data,
                        SUM(v.peca) AS total_pecas,
                        SUM(v.valor) AS total_valor
                    FROM vendas v
                    JOIN clientes c ON v.cliente_id = c.id
                    WHERE v.data <= ? AND v.pago = 'Sim' AND v.frete IN ('Espera', 'Embalar')
                    GROUP BY v.cliente_id
                """, (data_inicio.strftime('%Y-%m-%d'),))
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
            data_formatada = datetime.strptime(venda[2], '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            print(f"Erro ao converter data: {venda[2]}")
            data_formatada = venda[2]  # Mantém a data original se a conversão falhar
        tree.insert("", tk.END, values=(venda[0], "[Enviar]", data_formatada, venda[1], venda[3], venda[4])) 

    tree.dias = dias 
    tree.dias_fim = dias_fim

    ajustar_colunas(tree)  

def clique_treeview(event, tree):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if item and column == "#2":
        cliente_id = tree.item(item, "values")[0]  # Obtém o cliente_id
        enviar_mensagem_whatsapp(cliente_id, tree.dias, tree.dias_fim)

def enviar_mensagem_whatsapp(cliente_id, dias, dias_fim):
    conexao = conectar_banco_dados()
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT nome, Celular FROM clientes WHERE id = ?", (cliente_id,))
            resultado = cursor.fetchone()
            if resultado:
                nome, telefone = resultado
                if dias_fim:
                    mensagem = f"Olá {nome}, tudo bem?\nEstamos passando para lembrar que você possui sacolinhas próximo dos 30 dias conosco, antes de fazer o envio venha aproveitar nossa live, assim pode levar mais peças e seu frete pode ficar um pouco mais em conta ;D"
                    url = f"https://api.whatsapp.com/send?phone=55{telefone}&text={mensagem}"
                    webbrowser.open(url)
                elif dias == 30:
                    mensagem = f"Olá {nome}, tudo bem?\nEstamos passando para lembrar que você possui sacolinhas com mais de 30 dias conosco, podemos contar com o seu envio para o próximo envio?"
                    url = f"https://api.whatsapp.com/send?phone=55{telefone}&text={mensagem}"
                    webbrowser.open(url)
                elif dias == 90:  
                    mensagem = f"Olá {nome}, tudo bem? precisamos agendar o envio da sua sacolinha! podemos contar contigo ?\nTemos sacolinha há mais de 90 dias.\n(Caso não tenhamos resposta em 30 dias as peças serão doadas sem possibilidade de reembolso)"
                    url = f"https://api.whatsapp.com/send?phone=55{telefone}&text={mensagem}"
                    webbrowser.open(url)
                    data_notificacao = datetime.now().strftime('%Y-%m-%d')
                    cursor.execute("UPDATE vendas SET notificacao = ? WHERE cliente_id = ?", (data_notificacao, cliente_id))
                    conexao.commit()
                else:
                    print(f"Cliente com ID '{cliente_id}' não encontrado.")
        except Exception as e:
            print(f"Erro ao obter dados do cliente: {e}")
        finally:
            desconectar_banco_dados(conexao)

def ajustar_colunas(tree):
    tree.update_idletasks()
    for col in tree["columns"]:
        max_width = 0
        for item in tree.get_children(""):
            try:
                width = tree.set(item, col).encode().decode('UTF-8')
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