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
        self.user_data = None
        # self.show_books()

    def show_screen(self, screen_class, *args):
        """Método genérico para trocar telas."""
        if self.current_screen:
            self.current_screen.frame.destroy()  # Agora funciona para todas as telas
        self.current_screen = screen_class(self.root, *args)

    def show_login_screen(self):
        self.show_screen(LoginScreen, self.on_login_success)

    def show_add_books(self):
        self.show_screen(CadastrarLivroScreen)

    def show_update_books(self, book_id=None):
        self.show_screen(AtualizarLivroScreen, book_id)

    def show_books(self):
        """
        Passa o ID e os dados do usuário para a tela de livros.
        """
        self.show_screen(ListarLivrosScreen, self.on_logout, self.user_id, self.user_data)

    def on_login_success(self, user_data_tuple):
        """
        Atualizado para receber uma tupla (user_id, user_data) do login.
        """
        self.user_id, self.user_data = user_data_tuple
        print(f"User ID: {self.user_id}, User Data: {self.user_data}")
        self.show_books()
    def on_logout(self):
        """Retorna à tela de login ao clicar em 'Sair'."""
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()