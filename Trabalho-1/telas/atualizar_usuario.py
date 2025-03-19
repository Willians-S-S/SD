from crud import update_user  # Importa a função para atualizar o usuário
from tkinter import messagebox
import tkinter as tk
class AtualizarUsuarioScreen:
    def __init__(self, root, usuario_atual, tela_anterior):
        self.root = root
        self.usuario_atual = usuario_atual  # ID do usuário logado
        self.tela_anterior = tela_anterior
        self.frame = tk.Frame(root)
        self.frame.pack(padx=20, pady=20)

        # Labels e Entrys para atualizar usuário e/ou senha
        self.label_username = tk.Label(
            self.frame, text="Novo nome de Usuário (opcional):")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.pack()

        self.label_password = tk.Label(
            self.frame, text="Nova Senha (opcional):")
        self.label_password.pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()

        self.label_conf_password = tk.Label(
            self.frame, text="Confirmar Nova Senha:")
        self.label_conf_password.pack()
        self.entry_conf_password = tk.Entry(self.frame, show="*")
        self.entry_conf_password.pack()

        self.button_atualizar = tk.Button(
            self.frame, text="Atualizar", command=self.atualizar)
        self.button_atualizar.pack(pady=10)

        self.button_cancelar = tk.Button(
            self.frame, text="Cancelar", command=self.voltar)
        self.button_cancelar.pack()

    def atualizar(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        conf_password = self.entry_conf_password.get().strip()

        if not username and not password:
            messagebox.showerror(
                "Erro", "Preencha pelo menos um campo para atualizar.")
            return

        if password and len(password) < 4:
            messagebox.showerror(
                "Erro", "Senha muito curta, mínimo 4 caracteres.")
            return

        if password and password != conf_password:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        try:
            # Atualiza apenas os campos preenchidos
            if username:
                update_user(self.usuario_atual, "display_name", username)

            if password:
                # OBS: Senha em Firestore não é recomendado
                update_user(self.usuario_atual, "password", password)

            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            self.voltar()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {e}")

    def voltar(self):
        self.frame.destroy()
        if self.tela_anterior:
            self.tela_anterior.frame.pack()
