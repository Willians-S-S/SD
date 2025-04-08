import tkinter as tk
from tkinter import filedialog, Label, Button
from PIL import Image, ImageTk
import requests
import io

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return
    
    with open(file_path, "rb") as file:
        response = requests.post("http://10.180.47.250:5000/upload", files={"file": file})
    
    if response.status_code == 200:
        original_img = Image.open(file_path)
        processed_img = Image.open(io.BytesIO(response.content))
        
        original_img.thumbnail((250, 250))
        processed_img.thumbnail((250, 250))
        
        original_tk = ImageTk.PhotoImage(original_img)
        processed_tk = ImageTk.PhotoImage(processed_img)
        
        label_original.config(image=original_tk)
        label_original.image = original_tk
        
        label_processed.config(image=processed_tk)
        label_processed.image = processed_tk
        
        label_filter.config(text="Filtro aplicado: Inversão de cores")
    else:
        print("Erro ao enviar a imagem.")

# Criar janela principal
root = tk.Tk()
root.title("Editor de Imagens")
root.geometry("1000x800")  # Ajustando tamanho para acomodar as imagens lado a lado

btn_upload = Button(root, text="Selecionar Imagem", command=upload_image)
btn_upload.pack()

frame_images = tk.Frame(root)
frame_images.pack()

label_original = Label(frame_images, text="Imagem Original")
label_original.grid(row=0, column=0, padx=10, pady=10)

arrow_label = Label(frame_images, text="➡", font=("Arial", 20))
arrow_label.grid(row=0, column=1, padx=10, pady=10)

label_processed = Label(frame_images, text="Imagem Processada")
label_processed.grid(row=0, column=2, padx=10, pady=10)

label_filter = Label(root, text="Filtro aplicado: Nenhum")
label_filter.pack()

root.mainloop()
