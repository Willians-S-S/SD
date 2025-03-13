import tkinter as tk
from tkinter import messagebox
from login import LoginScreen  # Certifique-se de que o caminho está correto

def logout(root):
    """Função para deslogar o usuário e redirecionar para a tela de login."""
    resposta = messagebox.askyesno("Sair", "Tem certeza que deseja sair?")
    if resposta:
        for widget in root.winfo_children():
            widget.destroy()  # Remove todos os widgets da janela
        LoginScreen(root, on_success=lambda: print("Usuário logado novamente"))  # Retorna para a tela de login

# Exemplo de uso em um botão:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Teste de Logout")
    

    btn_sair = tk.Button(root, text="Sair", command=lambda: logout(root))
    btn_sair.pack(pady=20)

    root.mainloop()
