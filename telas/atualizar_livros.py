import tkinter as tk
from tkinter import messagebox, simpledialog # Importe simpledialog
# from database import buscar_livro_por_id, atualizar_livro

class AtualizarLivroScreen:
    def __init__(self, root, id):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()
        
        self.livro_id = id  # Armazena o ID do livro a ser atualizado
        self.carregar_campos()


    def carregar_campos(self):
        # Primeiro, peça o ID do livro a ser atualizado
        # self.livro_id = simpledialog.askinteger("Atualizar Livro", "Digite o ID do livro:", parent=self.root)

        if not self.livro_id:
            messagebox.showinfo("Aviso", "Operação cancelada.")
            self.frame.destroy()
            return


        # livro = buscar_livro_por_id(self.livro_id) # Ex. com banco de dados
        livro = {"id": self.livro_id, "titulo": "Exemplo", "autor": "Autor X", "ano": 2023}  # DADOS DE EXEMPLO!

        if not livro:
            messagebox.showerror("Erro", "Livro não encontrado.")
            self.frame.destroy()
            return


        # Crie os campos de entrada PREENCHIDOS com os dados atuais
        self.label_titulo = tk.Label(self.frame, text="Título:")
        self.label_titulo.pack()
        self.entry_titulo = tk.Entry(self.frame)
        self.entry_titulo.insert(0, livro["titulo"])  # Preenche o campo
        self.entry_titulo.pack()

        self.label_autor = tk.Label(self.frame, text="Autor:")
        self.label_autor.pack()
        self.entry_autor = tk.Entry(self.frame)
        self.entry_autor.insert(0, livro["autor"])  # Preenche
        self.entry_autor.pack()
        
        self.label_ano = tk.Label(self.frame, text="Ano:")
        self.label_ano.pack()
        self.entry_ano = tk.Entry(self.frame)
        self.entry_ano.insert(0, livro["ano"])
        self.entry_ano.pack()

        self.button_atualizar = tk.Button(self.frame, text="Atualizar", command=self.atualizar)
        self.button_atualizar.pack()

    def atualizar(self):
        titulo = self.entry_titulo.get()
        autor = self.entry_autor.get()
        ano = self.entry_ano.get()

        # if atualizar_livro(self.livro_id, titulo, autor, ano):  # Banco
        if titulo and autor and ano:
            messagebox.showinfo("Sucesso", "Livro atualizado!")
            self.frame.destroy()
        else:
            messagebox.showerror("Erro", "Preencha todos os campos.")