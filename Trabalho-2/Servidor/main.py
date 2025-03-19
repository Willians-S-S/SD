from fastapi import FastAPI, UploadFile, File
from image import save_image
import pygame

app = FastAPI()

@app.post("/image")
def upload_image(image: UploadFile = File(...)):
    image_db = save_image(image)
    print(f"Imagem salva com sucesso: {image_db}")
    pygame.mixer.init()

    pygame.mixer.music.load('/home/will/Documentos/UFPI/SD/Trabalho-2/Servidor/alarme/Sirene de 6 tons demonstração.mp3')

    pygame.mixer.music.play()

    while True:
        sair = input("Escreva sair para sair: ")
        if sair == "sair":
            pygame.mixer.music.stop()
            break
    
    return {"Mensagem": "Alarme desativado"}