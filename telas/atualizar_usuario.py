import tkinter as tk
from tkinter import messagebox

class AtualizarUsuarioScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Labels e Entrys para atualizar usuário e/ou senha
        self.label_username = tk.Label(self.frame, text="Novo nome de Usuário (opcional):")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.pack()

        self.label_password = tk.Label(self.frame, text="Nova Senha (opcional):")
        self.label_password.pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()
        
        self.label_conf_password = tk.Label(self.frame, text="Confirmar Nova Senha:")
        self.label_conf_password.pack()
        self.entry_conf_password = tk.Entry(self.frame, show="*")
        self.entry_conf_password.pack()

        self.button_atualizar = tk.Button(self.frame, text="Atualizar", command=self.atualizar)
        self.button_atualizar.pack()

    def atualizar(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        conf_password = self.entry_conf_password.get().strip()

        if not username and not password:
            messagebox.showerror("Erro", "Preencha pelo menos um campo para atualizar.")
            return

        if password and len(password) < 4:
            messagebox.showerror("Erro", "Senha muito curta, mínimo 4 caracteres.")
            return

        if password and password != conf_password:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        # Aqui você pode chamar a função de atualização no banco de dados
        # atualizar_usuario(novo_username, nova_senha)
        messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
        self.frame.destroy()

# Teste da tela
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Atualizar Usuário")
    AtualizarUsuarioScreen(root)
    root.mainloop()
