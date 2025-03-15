import tkinter as tk
from tkinter import messagebox
from crud import create_user

class CriarUsuarioScreen:
    def __init__(self, root, on_success):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.on_success = on_success

        tk.Label(self.frame, text="Nome Completo:").pack()
        self.entry_name = tk.Entry(self.frame)
        self.entry_name.pack()

        tk.Label(self.frame, text="Email:").pack()
        self.entry_email = tk.Entry(self.frame)
        self.entry_email.pack()

        tk.Label(self.frame, text="Senha:").pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()

        tk.Label(self.frame, text="Confirmar Senha:").pack()
        self.entry_conf_password = tk.Entry(self.frame, show="*")
        self.entry_conf_password.pack()

        tk.Button(self.frame, text="Criar Usuário", command=self.create).pack()

    def create(self):
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        conf_password = self.entry_conf_password.get().strip()

        if not name or not email or not password or not conf_password:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if password != conf_password:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        if len(password) < 4:
            messagebox.showerror("Erro", "Senha muito curta (mínimo 4 caracteres).")
            return

        try:
            create_user(name, email, password)
            messagebox.showinfo("Sucesso", f"Usuário '{name}' criado com sucesso!")
            self.frame.destroy()
            from telas.login import LoginScreen
            LoginScreen(self.root, self.on_success)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário: {e}")