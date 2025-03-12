import tkinter as tk
from login import LoginScreen

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Livraria")
        self.show_login_screen()

    def show_login_screen(self):
        LoginScreen(self.root, self.on_login_success)

    def on_login_success(self):
        # Aqui você pode, por exemplo, destruir a tela de login
        # e carregar a tela principal da livraria (menu, etc.)
        print("Login bem-sucedido!")
        # Exemplo:  self.show_main_menu()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()