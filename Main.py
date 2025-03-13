import tkinter as tk
import dashboard
import vendas
import fretes
import clientes 
import mensagens

def abrir_dashboard():
    dashboard.main()

def abrir_compras():
    vendas.main()

def abrir_fretes():
    fretes.main()

def abrir_clientes():
    clientes.main()

def abrir_mensagens():
    mensagens.main()

# Configuração da janela principal
root = tk.Tk()
root.title("Menu Principal")
root.geometry("400x300")

# Botões
btn_dashboard = tk.Button(root, text="Dashboard", command=abrir_dashboard, width=20, height=2)
btn_dashboard.pack(pady=10)

btn_vendas = tk.Button(root, text="Vendas", command=abrir_compras, width=20, height=2)
btn_vendas.pack(pady=10)

btn_fretes = tk.Button(root, text="Fretes", command=abrir_fretes, width=20, height=2)
btn_fretes.pack(pady=10)

btn_clientes = tk.Button(root, text="Clientes", command=abrir_clientes, width=20, height=2)
btn_clientes.pack(pady=10)

btn_mensagens = tk.Button(root, text="Mensagens", command=abrir_mensagens, width=20, height=2)
btn_mensagens.pack(pady=10)

# Iniciar o loop da interface gráfica
root.mainloop()