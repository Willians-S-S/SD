from fastapi import FastAPI, UploadFile, File
from image import save_image

app = FastAPI()

@app.post("/image")
def upload_image(image: UploadFile = File(...)):
    image_db = save_image(image)
    print(f"Imagem salva com sucesso: {image_db}")