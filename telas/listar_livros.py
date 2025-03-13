import tkinter as tk
from tkinter import messagebox
from telas.atualizar_livros import AtualizarLivroScreen
from telas.cadastrar_livros import CadastrarLivroScreen
from crud import read_books, delete_book


class ListarLivrosScreen:
    def __init__(self, root, on_logout):
        self.root = root
        self.on_logout = on_logout
        self.frame = tk.Frame(root, borderwidth=2, relief="solid")
        self.frame.pack(padx=10, pady=10)
        self.current_page = 0  # Página atual começa em 0 (primeira página)
        self.items_per_page = 10  # Itens por página
        self.carregar_livros()

    def carregar_livros(self):
        """Carrega a lista de livros do Firebase e exibe na tela com paginação."""
        try:
            livros = read_books()
            if not livros:
                messagebox.showinfo("Aviso", "Nenhum livro encontrado.")
                return

            # Limpa o frame antes de recarregar
            for widget in self.frame.winfo_children():
                widget.destroy()

            # Cabeçalhos
            tk.Label(self.frame, text="Título", font=("Arial", 12, "bold")).grid(
                row=0, column=0, padx=5, pady=5)
            tk.Label(self.frame, text="Autor", font=("Arial", 12, "bold")).grid(
                row=0, column=1, padx=5, pady=5)
            tk.Label(self.frame, text="Páginas", font=("Arial", 12, "bold")).grid(
                row=0, column=2, padx=5, pady=5)
            tk.Label(self.frame, text="Ano", font=("Arial", 12, "bold")).grid(
                row=0, column=3, padx=5, pady=5)

            # Calcula a página atual
            total_livros = len(livros)
            total_paginas = (
                total_livros + self.items_per_page - 1) // self.items_per_page

            # Ajusta a página atual se necessário
            if self.current_page >= total_paginas:
                self.current_page = max(0, total_paginas - 1)

            inicio = self.current_page * self.items_per_page
            fim = inicio + self.items_per_page
            livros_pagina = livros[inicio:fim]

            # Exibe os livros da página atual
            for i, livro in enumerate(livros_pagina, start=1):
                linha_dados = (i - 1) * 2 + 1  # Linhas 1, 3, 5, etc.
                tk.Label(self.frame, text=livro['title']).grid(
                    row=linha_dados, column=0, padx=5, pady=2)
                tk.Label(self.frame, text=livro['author']).grid(
                    row=linha_dados, column=1, padx=5, pady=2)
                tk.Label(self.frame, text=livro['pages']).grid(
                    row=linha_dados, column=2, padx=5, pady=2)
                tk.Label(self.frame, text=livro['year']).grid(
                    row=linha_dados, column=3, padx=5, pady=2)
                tk.Button(self.frame, text="Editar", command=lambda id=livro['id']: self.editar_livro(
                    id)).grid(row=linha_dados, column=4, padx=5, pady=2)
                tk.Button(self.frame, text="Deletar", command=lambda id=livro['id']: self.deletar_livro(
                    id)).grid(row=linha_dados, column=5, padx=5, pady=2)

                # Linha separadora
                tk.Frame(self.frame, height=1, width=500, bg="black").grid(
                    row=linha_dados + 1, column=0, columnspan=6, pady=2, sticky='ew')

            # Botões de navegação
            linha_navegacao = (len(livros_pagina) * 2) + \
                1  # Após os livros e separadores
            if total_paginas > 0:
                # Botão Anterior
                btn_anterior = tk.Button(
                    self.frame, text="Anterior", command=self.pagina_anterior)
                btn_anterior.grid(row=linha_navegacao,
                                  column=0, columnspan=1, pady=10)

                # Indicador de página
                lbl_pagina = tk.Label(
                    self.frame, text=f"Página {self.current_page + 1} de {total_paginas}")
                lbl_pagina.grid(row=linha_navegacao, column=0,
                                columnspan=6, pady=10)

                # Botão Próximo
                btn_proximo = tk.Button(
                    self.frame, text="Próximo", command=self.proxima_pagina)
                btn_proximo.grid(row=linha_navegacao,
                                 column=4, columnspan=9, pady=10)
            else:
                linha_navegacao = 1  # Se não há livros, ajusta a posição

            # Botão Cadastrar Livro
            btn_cadastrar = tk.Button(
                self.frame, text="Cadastrar Livro", command=self.cadastrar_livro)
            btn_cadastrar.grid(row=linha_navegacao + 1,
                               column=0, columnspan=6, pady=10)

            # Botão Sair
            btn_sair = tk.Button(self.frame, text="Sair",
                                 command=self.on_logout)
            btn_sair.grid(row=linha_navegacao + 2,
                          column=0, columnspan=6, pady=10)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar livros: {e}")

    def pagina_anterior(self):
        """Navega para a página anterior."""
        if self.current_page > 0:
            self.current_page -= 1
            self.carregar_livros()

    def proxima_pagina(self):
        """Navega para a próxima página."""
        self.current_page += 1
        self.carregar_livros()

    def editar_livro(self, book_id):
        """Abre a tela de edição para o livro com o ID fornecido."""
        self.frame.destroy()
        AtualizarLivroScreen(self.root, book_id)

    def deletar_livro(self, book_id):
        """Deleta um livro pelo ID."""
        resposta = messagebox.askyesno(
            "Confirmar", "Tem certeza que deseja excluir este livro?")
        if resposta:
            try:
                delete_book(book_id)
                messagebox.showinfo("Sucesso", "Livro deletado com sucesso!")
                self.carregar_livros()  # Recarrega a lista, mantendo a página atual se possível
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar livro: {e}")

    def cadastrar_livro(self):
        """Abre a tela de cadastro de livros."""
        self.frame.destroy()
        CadastrarLivroScreen(self.root)
