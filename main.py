import tkinter as tk
from telas.login import LoginScreen
from telas.cadastrar_livros import CadastrarLivroScreen
from telas.atualizar_livros import AtualizarLivroScreen
from telas.listar_livros import ListarLivrosScreen

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Livraria")
        self.root.geometry("800x600")
        self.current_screen = None  # Para rastrear a tela atual
        self.show_login_screen()

    def show_screen(self, screen_class, *args):
        """Método genérico para trocar telas."""
        if self.current_screen:
            self.current_screen.frame.destroy()  # Remove a tela atual
        self.current_screen = screen_class(self.root, *args)  # Instancia a nova tela

    def show_login_screen(self):
        self.show_screen(LoginScreen, self.on_login_success)

    def show_add_books(self):
        self.show_screen(CadastrarLivroScreen)

    def show_update_books(self, book_id=None):
        self.show_screen(AtualizarLivroScreen, book_id)

    def show_books(self):
        self.show_screen(ListarLivrosScreen)

    def on_login_success(self):
        print("Login bem-sucedido!")
        self.show_books()  # Após login, mostra a tela de listagem de livros


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()