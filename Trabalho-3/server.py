from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageOps
import os
import sqlite3
from datetime import datetime

"""
API de Processamento de Imagens com Flask

Este script implementa uma aplicação web simples usando Flask que permite aos usuários 
fazer upload de imagens, aplicar um filtro de processamento de imagem (inversão de cores) 
e receber a imagem processada como resposta. A aplicação também registra metadados sobre 
cada imagem enviada em um banco de dados SQLite.

Funcionalidades:
1. **Envio de Imagem**:
   - Os usuários podem enviar um arquivo de imagem via uma requisição POST para o endpoint `/upload`.
   - A imagem enviada é salva no diretório `uploads`.

2. **Processamento de Imagem**:
   - A imagem enviada é processada aplicando um filtro de inversão de cores utilizando a biblioteca PIL (Pillow).
   - A imagem processada é salva no diretório `processed`.

3. **Registro de Metadados**:
   - Metadados sobre a imagem enviada (nome do arquivo, filtro aplicado, timestamp) são armazenados em um banco de dados SQLite (`images.db`).
   - O esquema do banco de dados inclui uma tabela chamada `images` com as colunas: `id`, `filename`, `filter` e `timestamp`.

4. **Envio da Imagem Processada**:
   - Após o processamento, a aplicação envia a imagem processada de volta ao cliente como resposta.

Endpoints:
- **POST /upload**:
  - Aceita o envio de um arquivo via o campo `file` em uma requisição multipart/form-data.
  - Retorna o arquivo de imagem processado como resposta com o tipo MIME `image/png`.
  - Caso nenhum arquivo seja fornecido ou o arquivo seja inválido, uma mensagem de erro adequada é retornada com código de status 400.

Diretórios:
- `uploads`: Armazena as imagens originais enviadas.
- `processed`: Armazena as imagens após a aplicação do filtro de inversão.

Banco de Dados:
- O banco de dados SQLite `images.db` é usado para armazenar metadados sobre cada imagem enviada.
- A tabela `images` é criada se ainda não existir, garantindo a persistência dos metadados entre execuções da aplicação.

Dependências:
- Flask: Para criar o servidor web e lidar com requisições HTTP.
- PIL (Pillow): Para processamento de imagem (inversão de cores).
- SQLite3: Para armazenar metadados das imagens enviadas.
- os: Para operações de diretórios e caminhos de arquivos.
- datetime: Para registrar o timestamp das imagens enviadas.

Como Usar:
1. Execute o script para iniciar a aplicação Flask
"""

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect("images.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filter TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # Aplicar filtro (inversão de cores)
    image = Image.open(filepath)
    processed_image = ImageOps.invert(image.convert("RGB"))
    processed_filepath = os.path.join(PROCESSED_FOLDER, file.filename)
    processed_image.save(processed_filepath)
    
    # Salva metadados no banco
    conn = sqlite3.connect("images.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO images (filename, filter, timestamp) VALUES (?, ?, ?)",
                   (file.filename, "invert", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    return send_file(processed_filepath, mimetype="image/png")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
