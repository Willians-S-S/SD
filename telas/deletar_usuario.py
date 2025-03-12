import tkinter as tk
from tkinter import messagebox

class DeletarUsuarioScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Label e Entry para confirmação do nome de usuário
        self.label_username = tk.Label(self.frame, text="Digite seu nome de usuário para deletar a conta:")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.pack()

        self.button_deletar = tk.Button(self.frame, text="Deletar Conta", command=self.deletar)
        self.button_deletar.pack()

    def deletar(self):
        username = self.entry_username.get().strip()
        
        if not username:
            messagebox.showerror("Erro", "Digite seu nome de usuário.")
            return
        
        confirmar = messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar a conta '{username}'?")
        if confirmar:
            # Aqui futuramente será chamada a função do Firebase para deletar
            # deletar_usuario_firebase(username)
            messagebox.showinfo("Sucesso", "Conta deletada com sucesso!")
            self.frame.destroy()

# Teste da tela
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Deletar Usuário")
    DeletarUsuarioScreen(root)
    root.mainloop()
