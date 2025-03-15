from crud import login_user
from tkinter import messagebox
import tkinter as tk
import time
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
        tk.Button(self.frame, text="Cadastrar Usuário",
                  command=self.register).pack()

    def login(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()

        if not email or not password:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        inicio = time.time()
        response = login_user(email, password)
        fim = time.time()

        print(f"Tempo de execução: {fim - inicio:.4f} segundos")

        if response:
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            # Chama a função de sucesso após o login
            self.on_success(response[0])
            self.frame.destroy()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas.")

    def register(self):
        from telas.criar_usuario import CriarUsuarioScreen
        self.frame.destroy()
        CriarUsuarioScreen(self.root, self.on_success)
