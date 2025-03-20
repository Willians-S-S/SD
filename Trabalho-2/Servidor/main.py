from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from image import save_image
import pygame

import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pygame.mixer.init()


@app.post("/image")
def upload_image(image: UploadFile = File(...)):
    image_db = save_image(image)
    pygame.mixer.music.load("/home/will/Documentos/UFPI/SD/Trabalho-2/Servidor/alarme/alarm_sound.mp3")
    pygame.mixer.music.play(-1)  # Reproduzir em loop
    print(f"Imagem salva com sucesso: {image_db}")
    
    return {"Mensagem": "Alarme desativado"}

@app.get("/stop")
def stop_alarm():
    if pygame.mixer.get_init() is None:
        print("Alerme não tá tocando")
        return {"Mensagem":"Alerme não tá tocando"}
    pygame.mixer.music.stop()
    return {"message": "Alarme desativado."}

@app.get("/teste")
def teste():
    return {"mensagem":"Olá, mundo!"}
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)