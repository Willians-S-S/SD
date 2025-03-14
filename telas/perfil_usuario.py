import tkinter as tk
from tkinter import messagebox

class UserProfileScreen:
    def __init__(self, root, user_id, user_data, on_back):
        self.root = root
        self.user_id = user_id
        self.user_data = user_data  # Dicionário com dados do usuário
        self.on_back = on_back
        self.frame = tk.Frame(root, borderwidth=2, relief="solid")
        self.frame.pack(padx=10, pady=10)

        tk.Label(self.frame, text="Perfil do Usuário", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(self.frame, text="Email:").pack()
        self.entry_email = tk.Entry(self.frame)
        self.entry_email.insert(0, user_data.get("email", ""))
        self.entry_email.pack()
        
        tk.Label(self.frame, text="Nova Senha:").pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()
        
        tk.Button(self.frame, text="Atualizar", command=self.update_profile).pack(pady=5)
        tk.Button(self.frame, text="Voltar", command=self.go_back).pack()
    def update_profile(self):
        new_email = self.entry_email.get().strip()
        new_password = self.entry_password.get().strip()
        
        if not new_email:
            messagebox.showerror("Erro", "O email não pode estar vazio.")
            return
        
        # Atualiza no Firestore usando o ID correto
        from crud import update_user
        
        if new_email != self.user_data['email']:
            update_user(self.user_id, 'email', new_email)
            self.user_data['email'] = new_email
        
        if new_password:
            update_user(self.user_id, 'password', new_password)
            self.user_data['password'] = new_password
        
        messagebox.showinfo("Sucesso", "Perfil atualizado!")
        self.go_back()
    def go_back(self):
        """Retorna à tela anterior."""
        self.frame.destroy()
        self.on_back()