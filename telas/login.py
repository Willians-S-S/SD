import tkinter as tk
from tkinter import messagebox
# from database import validar_credenciais  # Se usar banco de dados


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
        username = self.entry_username.get()
        password = self.entry_password.get()

        # if validar_credenciais(username, password):   # Exemplo com banco de dados
        if username == "admin" and password == "123":  # Exemplo SIMPLES
            self.on_success()  # Chama a função de sucesso do main.py
            self.frame.destroy() # Fecha janela login
        else:
            messagebox.showerror("Erro", "Credenciais inválidas.")

    def register(self):
        from telas.criar_usuario import CriarUsuarioScreen  # Importe aqui para evitar dependência circular
        self.frame.destroy()
        CriarUsuarioScreen(self.root)