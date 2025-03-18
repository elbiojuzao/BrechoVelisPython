import tkinter as tk
from tkinter import Toplevel
from utils import salvar_configuracoes_janela, carregar_configuracoes

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
    nova_janela.protocol("WM_DELETE_WINDOW", lambda: (salvar_configuracoes_janela(nova_janela, "mensagens"), nova_janela.destroy()))

if __name__ == "__main__":
    main()