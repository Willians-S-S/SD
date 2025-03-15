import tkinter as tk
from tkinter import messagebox
from crud import delete_user
class DeletarUsuarioScreen:
    def __init__(self, root, usuario_atual, tela_anterior):
        self.root = root
        self.usuario_atual = usuario_atual
        self.tela_anterior = tela_anterior
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.button_deletar = tk.Button(self.frame, text="Deletar Conta", command=self.deletar)
        self.button_deletar.pack()

        self.button_voltar = tk.Button(
            self.frame, text="Cancelar", command=self.voltar)
        self.button_voltar.pack()

    def deletar(self):   
        confirmar = messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar sua conta?")
        if confirmar:
            delete_user(self.usuario_atual)
            messagebox.showinfo("Sucesso", "Conta deletada com sucesso!")
            self.frame.destroy()
            from telas.login import LoginScreen
            LoginScreen(self.root, lambda: print(
                f"Login após deletar"))

    def voltar(self):
        self.frame.destroy()
        self.tela_anterior.frame.pack()

# Teste da tela
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Deletar Usuário")
    DeletarUsuarioScreen(root)
    root.mainloop()
