import tkinter as tk
from tkinter import messagebox

from telas.listar_livros import ListarLivrosScreen

from crud import login_user

class LoginScreen:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.label_username = tk.Label(self.frame, text="Usuário:")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.pack()

        self.label_password = tk.Label(self.frame, text="Senha:")
        self.label_password.pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()

        self.button_login = tk.Button(self.frame, text="Entrar", command=self.login)
        self.button_login.pack()
        
        self.button_register = tk.Button(self.frame, text="Cadastrar Usuário", command=self.register)
        self.button_register.pack()


    def login(self):
        email = self.entry_username.get()
        password = self.entry_password.get()

        if email == "" or email == " " or password == "" or password ==" ":
             messagebox.showerror("Erro", "Credenciais inválidas.")
             return 
       
        response = login_user(email=email, password=password)
        if response:
            self.on_success()  # Chama a função de sucesso do main.py
            self.frame.destroy() #
            return
            ListarLivrosScreen(self.root)
            self.frame.destroy()  # Remove a tela atual
        
        messagebox.showerror("Erro", "Credenciais inválidas.")

    def register(self):
        from telas.criar_usuario import CriarUsuarioScreen  # Importe aqui para evitar dependência circular
        self.frame.destroy()
        CriarUsuarioScreen(self.root)