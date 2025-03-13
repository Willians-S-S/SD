import tkinter as tk
from tkinter import messagebox
from crud import update_book, read_books
# from telas.listar_livros import ListarLivrosScreen  # Importa a tela de listagem de livros

class AtualizarLivroScreen:
    def __init__(self, root, book_id):
        self.root = root
        self.book_id = book_id  # ID do livro a ser atualizado
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.entries = {}  # Armazena os campos de entrada dinamicamente
        self.carregar_campos()

    def carregar_campos(self):
        """Carrega os campos de entrada com base nos dados atuais do livro."""
        try:
            # Busca os dados do livro no Firestore
            livros = read_books()
            livro = next((livro for livro in livros if livro["id"] == self.book_id), None)

            if not livro:
                messagebox.showerror("Erro", "Livro n�o encontrado.")
                self.frame.destroy()
                return

            # Cria dinamicamente os campos de entrada com base nos dados do livro
            row = 0
            for field, value in livro.items():
                if field == "id":  # Ignora o campo 'id', pois n�o � edit�vel
                    continue

                label = tk.Label(self.frame, text=f"{field.capitalize()}:")
                label.grid(row=row, column=0, sticky="w")

                entry = tk.Entry(self.frame)
                entry.insert(0, value)  # Preenche o campo com o valor atual
                entry.grid(row=row, column=1, sticky="ew")

                self.entries[field] = entry  # Armazena o campo no dicion�rio
                row += 1

            # Bot�o para atualizar
            btn_atualizar = tk.Button(self.frame, text="Atualizar", command=self.atualizar)
            btn_atualizar.grid(row=row, column=0, columnspan=2, pady=10)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do livro: {e}")

    def atualizar(self):
        """Coleta os campos preenchidos e atualiza o livro no Firestore."""
        updates = {}  # Dicionário para armazenar os campos a serem atualizados

        # Coleta os campos que foram modificados
        for field, entry in self.entries.items():
            new_value = entry.get().strip()
            if new_value:  # Apenas campos preenchidos são considerados
                updates[field] = new_value

        if not updates:
            messagebox.showerror("Erro", "Nenhum campo foi preenchido para atualização.")
            return

        try:
            # Atualiza o livro no Firestore
            for field, new_value in updates.items():
                update_book(self.book_id, field, new_value)

            messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")

            self.frame.destroy()
            
            # Redireciona para a tela de listagem de livros usando a navegação centralizada
            from main import App  # Importe a classe principal
            app = App(self.root)
            app.show_books()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar livro: {e}")