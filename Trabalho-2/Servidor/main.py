from fastapi import FastAPI, UploadFile, File
from image import save_image
import pygame

import uvicorn

app = FastAPI()

@app.post("/image")
def upload_image(image: UploadFile = File(...)):
    image_db = save_image(image)
    print(f"Imagem salva com sucesso: {image_db}")
    pygame.mixer.init()

    pygame.mixer.music.load(
        'alarme\som.mp3')

    pygame.mixer.music.play()

    while True:
        sair = input("Escreva sair para sair: ")
        if sair == "sair":
            pygame.mixer.music.stop()
            break
    
    return {"Mensagem": "Alarme desativado"}

@app.get("/teste")
def teste():
    return {"mensagem":"Olá, mundo!"}
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)