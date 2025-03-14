import tkinter as tk
from tkinter import messagebox
from telas.atualizar_livros import AtualizarLivroScreen
from telas.cadastrar_livros import CadastrarLivroScreen
from telas.perfil_usuario import UserProfileScreen
from crud import read_books, delete_book


class ListarLivrosScreen:
    def __init__(self, root, on_logout, user_id, user_data):
        self.root = root
        self.on_logout = on_logout
        self.user_id = user_id
        self.user_data = user_data

        # Container principal para todos os elementos
        self.frame = tk.Frame(root)  # Renomeado para 'frame' para compatibilidade
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Frame superior para botões
        self.top_frame = tk.Frame(self.frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Botão Perfil (esquerda)
        btn_perfil = tk.Button(self.top_frame, text="Perfil", command=self.abrir_perfil)
        btn_perfil.pack(side=tk.LEFT, padx=5)

        # Botão Sair (direita)
        btn_sair = tk.Button(self.top_frame, text="Sair", command=self.on_logout)
        btn_sair.pack(side=tk.RIGHT, padx=5)

        # Frame principal para listagem de livros
        self.main_frame = tk.Frame(self.frame, borderwidth=2, relief="solid")
        self.main_frame.pack(padx=10, pady=10, anchor='center')

        self.current_page = 0
        self.items_per_page = 10
        self.carregar_livros()

    def carregar_livros(self):
        """Carrega a lista de livros dentro do main_frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        try:
            livros = read_books()
            if not livros:
                messagebox.showinfo("Aviso", "Nenhum livro encontrado.")
                return

            # Cabeçalhos
            headers = ["Título", "Autor", "Páginas", "Ano"]
            for col, header in enumerate(headers):
                tk.Label(self.main_frame, text=header, font=("Arial", 12, "bold")).grid(
                    row=0, column=col, padx=5, pady=5
                )

            # Lógica de paginação e exibição dos livros
            total_livros = len(livros)
            total_paginas = (total_livros + self.items_per_page - 1) // self.items_per_page

            if self.current_page >= total_paginas:
                self.current_page = max(0, total_paginas - 1)

            inicio = self.current_page * self.items_per_page
            fim = inicio + self.items_per_page
            livros_pagina = livros[inicio:fim]

            for i, livro in enumerate(livros_pagina, start=1):
                linha_dados = (i - 1) * 2 + 1
                tk.Label(self.main_frame, text=livro['title']).grid(row=linha_dados, column=0, padx=5, pady=2)
                tk.Label(self.main_frame, text=livro['author']).grid(row=linha_dados, column=1, padx=5, pady=2)
                tk.Label(self.main_frame, text=livro['pages']).grid(row=linha_dados, column=2, padx=5, pady=2)
                tk.Label(self.main_frame, text=livro['year']).grid(row=linha_dados, column=3, padx=5, pady=2)
                tk.Button(self.main_frame, text="Editar", command=lambda id=livro['id']: self.editar_livro(id)).grid(
                    row=linha_dados, column=4, padx=5, pady=2
                )
                tk.Button(self.main_frame, text="Deletar", command=lambda id=livro['id']: self.deletar_livro(id)).grid(
                    row=linha_dados, column=5, padx=5, pady=2
                )

                # Linha separadora
                tk.Frame(self.main_frame, height=1, width=500, bg="black").grid(
                    row=linha_dados + 1, column=0, columnspan=6, pady=2, sticky='ew'
                )

            # Botões de navegação
            linha_navegacao = (len(livros_pagina) * 2) + 1
            if total_paginas > 0:
                tk.Button(self.main_frame, text="Anterior", command=self.pagina_anterior).grid(
                    row=linha_navegacao, column=0, columnspan=1, pady=10
                )
                tk.Label(self.main_frame, text=f"Página {self.current_page + 1} de {total_paginas}").grid(
                    row=linha_navegacao, column=0, columnspan=6, pady=10
                )
                tk.Button(self.main_frame, text="Próximo", command=self.proxima_pagina).grid(
                    row=linha_navegacao, column=4, columnspan=9, pady=10
                )

            # Botão Cadastrar Livro
            tk.Button(self.main_frame, text="Cadastrar Livro", command=self.cadastrar_livro).grid(
                row=linha_navegacao + 1, column=0, columnspan=6, pady=10
            )

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
    def abrir_perfil(self):
        """Abre a tela de perfil com o ID e os dados do usuário."""
        self.frame.destroy()  # Destroi o container principal
        UserProfileScreen(
            self.root,
            self.user_id,
            self.user_data,
            lambda: ListarLivrosScreen(self.root, self.on_logout, self.user_id, self.user_data)
        )