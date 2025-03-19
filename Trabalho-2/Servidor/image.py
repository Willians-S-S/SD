import os
import shutil
from typing import List
from uuid import uuid4
from fastapi import UploadFile

IMAGE_PATH = "..\Imagens"
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

def save_image(img: UploadFile) -> str:
    try:
        # Certifica que o diretório existe
        os.makedirs(IMAGE_PATH, exist_ok=True)

        # Valida a extensão do arquivo
        _, ext = os.path.splitext(img.filename)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Extensão de arquivo não suportada: {ext}")

        # Gera um nome de arquivo único
        unique_name = f"{uuid4().hex}{ext}"
        file_path = os.path.join(IMAGE_PATH, unique_name)

        # Salva o arquivo no sistema
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

        return unique_name
    except Exception as e:
        print(f"Erro ao salvar a imagem: {e}")
        return None