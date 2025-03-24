import customtkinter as ctk
import dashboard
import vendas
import fretes
import clientes
import mensagens

def abrir_dashboard():
    dashboard.main(dark_mode)  # Passa dark_mode como argumento

def abrir_compras():
    vendas.main(dark_mode)

def abrir_fretes():
    fretes.main(dark_mode)

def abrir_clientes():
    clientes.main(dark_mode)

def abrir_mensagens():
    mensagens.main(root, dark_mode)

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    atualizar_estilo()
    # Atualizar o modo escuro nas telas abertas (se houver)
    try:
        dashboard.root.destroy()
        dashboard.main(dark_mode)
    except AttributeError:
        pass
    try:
        vendas.root.destroy()
        vendas.main(dark_mode)
    except AttributeError:
        pass
    try:
        fretes.root.destroy()
        fretes.main(dark_mode)
    except AttributeError:
        pass
    try:
        clientes.root.destroy()
        clientes.main(dark_mode)
    except AttributeError:
        pass
    try:
        mensagens.root.destroy()
        mensagens.main(root, dark_mode)
    except AttributeError:
        pass

def atualizar_estilo():
    global dark_mode
    if dark_mode:
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")

root = ctk.CTk()
root.title("Menu Principal")
root.geometry("400x300")

# Inicialização do modo escuro
dark_mode = False
atualizar_estilo()

# Exibe a tela de notificações junto com a tela principal
mensagens.criar_tela_notificacoes(root)

btn_dashboard = ctk.CTkButton(root, text="Dashboard", command=abrir_dashboard)
btn_dashboard.pack(pady=10)

btn_vendas = ctk.CTkButton(root, text="Vendas", command=abrir_compras)
btn_vendas.pack(pady=10)

btn_fretes = ctk.CTkButton(root, text="Fretes", command=abrir_fretes)
btn_fretes.pack(pady=10)

btn_clientes = ctk.CTkButton(root, text="Clientes", command=abrir_clientes)
btn_clientes.pack(pady=10)

btn_mensagens = ctk.CTkButton(root, text="Mensagens", command=abrir_mensagens)
btn_mensagens.pack(pady=10)

# Switch button para alternar o modo escuro
switch_btn = ctk.CTkSwitch(root, text="", command=toggle_dark_mode)
switch_btn.place(x=300, y=10)

root.mainloop()