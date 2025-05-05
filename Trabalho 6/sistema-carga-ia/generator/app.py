#!/usr/bin/env python
import os
import time
import random
import base64
import logging
import pika
import glob
from PIL import Image
from io import BytesIO
import json
from dotenv import load_dotenv

# Configurar o logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS')
MESSAGE_RATE = int(os.getenv('MESSAGE_RATE'))  # Mensagens por segundo

# Configuração da exchange e da fila
EXCHANGE_NAME = 'images_exchange'
EXCHANGE_TYPE = 'topic'

# Caminhos das imagens
FACES_DIR = '/app/images/faces'
TEAMS_DIR = '/app/images/teams'

def get_image_files(directory):
    """Obter lista de arquivos de imagem do diretório"""
    if not os.path.exists(directory):
        logger.error(f"Diretório não encontrado: {directory}")
        return []
    
    extensions = ['*.jpg', '*.jpeg', '*.png']
    image_files = []
    
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    return image_files

def encode_image(image_path):
    """Codificar imagem para string base64"""
    try:
        with Image.open(image_path) as img:
            # Redimensionar para dimensões razoáveis, se necessário
            if max(img.size) > 800:
                img.thumbnail((800, 800))
            
            # Converter para RGB, se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Salvar para objeto BytesIO
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_str
    except Exception as e:
        logger.error(f"Erro ao codificar imagem {image_path}: {e}")
        return None

def connect_to_rabbitmq():
    """Estabelecer conexão com o RabbitMQ"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    
    # Tentar reconectar se o RabbitMQ não estiver imediatamente disponível
    max_retries = 10
    retry_interval = 5
    
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    credentials=credentials,
                    heartbeat=600
                )
            )
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Falha ao conectar ao RabbitMQ (tentativa {attempt+1}/{max_retries}). Tentando novamente em {retry_interval} segundos...")
                time.sleep(retry_interval)
            else:
                logger.error(f"Falha ao conectar ao RabbitMQ após {max_retries} tentativas: {e}")
                raise

def main():
    """Função principal para enviar mensagens para o RabbitMQ"""
    # Carregar arquivos de imagem
    face_images = get_image_files(FACES_DIR)
    team_images = get_image_files(TEAMS_DIR)
    
    if not face_images:
        logger.warning(f"Nenhuma imagem de face encontrada em {FACES_DIR}")
    if not team_images:
        logger.warning(f"Nenhuma imagem de time encontrada em {TEAMS_DIR}")
    
    if not face_images and not team_images:
        logger.error("Nenhuma imagem encontrada. Saindo.")
        return
    
    # Conectar ao RabbitMQ
    try:
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        
        # Declarar exchange
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        logger.info(f"Conectado ao RabbitMQ em {RABBITMQ_HOST}")
        logger.info(f"Encontradas {len(face_images)} imagens de face e {len(team_images)} imagens de time")
        logger.info(f"Enviando mensagens a uma taxa de {MESSAGE_RATE} por segundo")
        
        # Enviar mensagens continuamente
        message_count = 0
        interval = 1.0 / MESSAGE_RATE  # Tempo entre mensagens
        
        while True:
            # Decidir qual tipo de imagem enviar (alternando ou aleatório)
            if random.random() < 0.5 and face_images:
                # Imagem de face
                image_path = random.choice(face_images)
                routing_key = "face"
                image_type = "face"
            elif team_images:
                # Imagem de time
                image_path = random.choice(team_images)
                routing_key = "team"
                image_type = "team"
            else:
                # Voltar para o que tivermos
                image_path = random.choice(face_images or team_images)
                routing_key = "face" if image_path in face_images else "team"
                image_type = "face" if image_path in face_images else "team"
            
            # Codificar imagem
            encoded_image = encode_image(image_path)
            if encoded_image:
                # Criar mensagem
                message = {
                    "type": image_type,
                    "filename": os.path.basename(image_path),
                    "image": encoded_image,
                    "timestamp": time.time()
                }
                
                # Publicar mensagem
                channel.basic_publish(
                    exchange=EXCHANGE_NAME,
                    routing_key=routing_key,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # tornar a mensagem persistente
                        content_type='application/json'
                    )
                )
                
                message_count += 1
                if message_count % 10 == 0:
                    logger.info(f"Enviadas {message_count} mensagens ({routing_key}: {os.path.basename(image_path)})")
                
                # Aguardar para manter a taxa de mensagens
                time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário. Fechando conexão...")
    except Exception as e:
        logger.error(f"Erro: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    # Esperar que o RabbitMQ esteja totalmente pronto
    time.sleep(5)
    main()