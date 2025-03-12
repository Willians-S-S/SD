import tkinter as tk
from tkinter import messagebox, simpledialog
# from database import buscar_todos_os_livros, deletar_livro

class ListarLivrosScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.carregar_livros()
    
    def carregar_livros(self):
        # Simulação de dados (substituir pelo banco de dados)
        livros = [
            {"id": 1, "titulo": "Livro A", "autor": "Autor 1", "paginas": 200, "ano": 2020},
            {"id": 2, "titulo": "Livro B", "autor": "Autor 2", "paginas": 150, "ano": 2018},
            {"id": 3, "titulo": "Livro C", "autor": "Autor 3", "paginas": 300, "ano": 2022}
        ]
        # livros = buscar_todos_os_livros()  # Banco de dados

        if not livros:
            messagebox.showinfo("Aviso", "Nenhum livro encontrado.")
            self.frame.destroy()
            return

        for i, livro in enumerate(livros):
            lbl_titulo = tk.Label(self.frame, text=livro['titulo'], width=20, borderwidth=1, relief="solid")
            lbl_titulo.grid(row=i, column=0, sticky="nsew")
            
            lbl_autor = tk.Label(self.frame, text=livro['autor'], width=20, borderwidth=1, relief="solid")
            lbl_autor.grid(row=i, column=1, sticky="nsew")
            
            lbl_paginas = tk.Label(self.frame, text=f"{livro['paginas']} pág.", width=15, borderwidth=1, relief="solid")
            lbl_paginas.grid(row=i, column=2, sticky="nsew")
            
            lbl_ano = tk.Label(self.frame, text=livro['ano'], width=10, borderwidth=1, relief="solid")
            lbl_ano.grid(row=i, column=3, sticky="nsew")
            
            btn_editar = tk.Button(self.frame, text="Editar", command=lambda id=livro['id']: self.editar_livro(id))
            btn_editar.grid(row=i, column=4, sticky="nsew")
            
            btn_deletar = tk.Button(self.frame, text="Deletar", command=lambda id=livro['id']: self.deletar_livro(id))
            btn_deletar.grid(row=i, column=5, sticky="nsew")
    
    def editar_livro(self, livro_id):
        from atualizar_livro_screen import AtualizarLivroScreen  # Importação para evitar loop
        AtualizarLivroScreen(self.root)

    def deletar_livro(self, livro_id):
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este livro?")
        if resposta:
            # deletar_livro(livro_id)  # Banco de dados
            messagebox.showinfo("Sucesso", "Livro deletado!")
            self.frame.destroy()
            self.__init__(self.root)  # Recarregar a tela

# Exemplo de uso:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lista de Livros")
    ListarLivrosScreen(root)
    root.mainloop()
