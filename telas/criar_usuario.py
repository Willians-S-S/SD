import tkinter as tk
from tkinter import messagebox
#from database import criar_usuario  # Se usar banco de dados

class CriarUsuarioScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Labels e Entrys para nome, usuário, senha, confirmação de senha
        self.label_nome = tk.Label(self.frame, text="Nome Completo:")
        self.label_nome.pack()
        self.entry_nome = tk.Entry(self.frame)
        self.entry_nome.pack()

        self.label_username = tk.Label(self.frame, text="nome de Usuário:")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.pack()

        self.label_password = tk.Label(self.frame, text="Senha:")
        self.label_password.pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()
        
        self.label_conf_password = tk.Label(self.frame, text="Confirmar Senha:")
        self.label_conf_password.pack()
        self.entry_conf_password = tk.Entry(self.frame, show="*")
        self.entry_conf_password.pack()


        self.button_criar = tk.Button(self.frame, text="Criar Usuário", command=self.criar)
        self.button_criar.pack()

    def criar(self):
        nome = self.entry_nome.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        conf_password = self.entry_conf_password.get()

        if password != conf_password:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
        
        if len(password) < 4:
            messagebox.showerror("Erro", "Senha muito curta, minimo 4 caracteres.")
            return

        #criar_usuario(nome, username, password)  # Exemplo com banco de dados
        messagebox.showinfo("Sucesso", f"Usuário '{username}' criado!")
        self.frame.destroy()
        from telas.login import LoginScreen
        LoginScreen(self.root, lambda: print("Login após cadastro")) # volta para login