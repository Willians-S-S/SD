from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageOps
import os
import sqlite3
from datetime import datetime

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

@app.route("/teste", methods=["GET"])
def teste():
    return {"mensagem":"Olá, mundo!"}

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
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
