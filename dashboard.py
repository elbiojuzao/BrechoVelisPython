import tkinter as tk
from tkinter import Toplevel

def main():
    nova_janela = Toplevel()
    nova_janela.title("Dashboard")
    nova_janela.geometry("300x200")
    label = tk.Label(nova_janela, text="Bem-vindo ao Dashboard!", font=("Arial", 14))
    label.pack(pady=20)

if __name__ == "__main__":
    main()