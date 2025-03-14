import time
import tkinter as tk
from tkinter import messagebox
from crud import login_user

class LoginScreen:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.frame = tk.Frame(root)
        self.frame.pack()

        tk.Label(self.frame, text="Email:").pack()
        self.entry_email = tk.Entry(self.frame)
        self.entry_email.pack()

        tk.Label(self.frame, text="Senha:").pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()

        tk.Button(self.frame, text="Entrar", command=self.login).pack()
        tk.Button(self.frame, text="Cadastrar Usuário", command=self.register).pack()

    def login(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        
        if not email or not password:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        
        response = login_user(email, password)
        
        if response:
            user_id, user_data = response  # Desempacota a tupla
            self.on_success((user_id, user_data))  # Passa como tupla
            self.frame.destroy()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas.")
    def register(self):
        from telas.criar_usuario import CriarUsuarioScreen
        self.frame.destroy()
        CriarUsuarioScreen(self.root)