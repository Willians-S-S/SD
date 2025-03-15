import tkinter as tk
from tkinter import messagebox
from crud import read_user_by_id

class PerfilUsuarioScreen:
    def __init__(self, root, usuario_atual, tela_anterior):
        self.root = root
        self.usuario_atual = usuario_atual  # ID do usuário logado
        self.tela_anterior = tela_anterior  # Referência da tela anterior
        self.frame = tk.Frame(root)
        self.frame.pack(padx=20, pady=20)

        # Obtém os dados do usuário
        self.dados_usuario = read_user_by_id(self.usuario_atual)

        if not self.dados_usuario:
            messagebox.showerror(
                "Erro", "Não foi possível carregar os dados do usuário.")
            self.voltar()
            return

        # Exibição do usuário atual
        self.lbl_usuario = tk.Label(
            self.frame,
            text=f"Usuário logado: {self.dados_usuario.get('display_name', 'Desconhecido')}",
            font=('Arial', 12, 'bold'),
            fg='black'
        )
        self.lbl_usuario.pack(pady=10)

        # Exibição do e-mail
        self.lbl_email = tk.Label(
            self.frame,
            text=f"E-mail: {self.dados_usuario.get('email', 'Não disponível')}",
            font=('Arial', 10)
        )
        self.lbl_email.pack(pady=5)

        # Botões
        botoes_frame = tk.Frame(self.frame)
        botoes_frame.pack(pady=10)

        self.button_editar = tk.Button(
            botoes_frame, text="Editar Perfil", command=self.editar, width=10)
        self.button_editar.grid(row=0, column=1, padx=5)

        self.button_apagar = tk.Button(
            botoes_frame, text="Apagar Perfil", command=self.apagar, width=10)
        self.button_apagar.grid(row=1, column=1, padx=5)

        self.button_cancelar = tk.Button(
            botoes_frame, text="Voltar", command=self.voltar, width=10)
        self.button_cancelar.grid(row=2, column=1, padx=5)

    def editar(self):
        from telas.atualizar_usuario import AtualizarUsuarioScreen
        self.frame.pack_forget()
        AtualizarUsuarioScreen(self.root, self.usuario_atual, self)

    def apagar(self):
        from telas.deletar_usuario import DeletarUsuarioScreen
        self.frame.pack_forget()
        DeletarUsuarioScreen(self.root, self.usuario_atual, self)

    def voltar(self):
        self.frame.destroy()
        if self.tela_anterior:
            self.tela_anterior.frame.pack()  # Recarrega a tela de listagem
