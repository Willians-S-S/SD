#!/usr/bin/env python
import os
import time
import json
import base64
import logging
import pika
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from deepface import DeepFace
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
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin123')
PROCESSING_TIME = int(os.getenv('PROCESSING_TIME', 3))  # Segundos por mensagem

# Configuração da exchange e da fila
EXCHANGE_NAME = 'images_exchange'
EXCHANGE_TYPE = 'topic'
QUEUE_NAME = 'face_analysis_queue'
ROUTING_KEY = 'face'

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

def decode_image(encoded_image):
    """Decodificar imagem base64 para o formato OpenCV"""
    try:
        # Decodificar string base64
        img_data = base64.b64decode(encoded_image)
        
        # Converter para imagem PIL
        img = Image.open(BytesIO(img_data))
        
        # Converter para o formato OpenCV (array numpy)
        img_cv = np.array(img)
        
        # Converter RGB para BGR (OpenCV usa BGR)
        if len(img_cv.shape) == 3 and img_cv.shape[2] == 3:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
            
        return img_cv
    except Exception as e:
        logger.error(f"Erro ao decodificar imagem: {e}")
        return None

def analyze_face_emotion(image):
    """Analisar a emoção facial usando DeepFace"""
    try:
        # Processar com DeepFace - analisar emoções
        result = DeepFace.analyze(
            img_path=image,
            actions=['emotion'],
            enforce_detection=False  # Não lançar erro se nenhuma face for detectada
        )
        
        # Pode ser uma lista ou um único resultado
        if isinstance(result, list):
            if not result:  # Lista vazia
                return {"error": "Nenhuma face detectada"}
            result = result[0]  # Pegar a primeira face
            
        # Extrair dados de emoção
        emotions = result.get('emotion', {})
        dominant_emotion = result.get('dominant_emotion', 'unknown')
        
        return {
            'dominant_emotion': dominant_emotion,
            'emotions': emotions
        }
    except Exception as e:
        logger.error(f"Erro ao analisar face: {e}")
        return {"error": str(e)}

def process_message(ch, method, properties, body):
    """Processar mensagem recebida"""
    try:
        # Analisar mensagem
        message = json.loads(body)
        filename = message.get('filename', 'unknown')
        encoded_image = message.get('image')
        
        if not encoded_image:
            logger.warning(f"Mensagem faltando dados da imagem: {filename}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        logger.info(f"Processando imagem facial: {filename}")
        
        # Decodificar imagem
        image = decode_image(encoded_image)
        if image is None:
            logger.warning(f"Falha ao decodificar imagem: {filename}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Analisar a emoção facial
        start_time = time.time()
        emotion_result = analyze_face_emotion(image)
        
        # Registrar resultado
        if 'error' in emotion_result:
            logger.warning(f"Falha ao analisar face em {filename}: {emotion_result['error']}")
        else:
            dominant_emotion = emotion_result['dominant_emotion']
            logger.info(f"Análise facial para {filename}: {dominant_emotion}")
        
        # Simular processamento lento para garantir o acúmulo na fila
        elapsed = time.time() - start_time
        sleep_time = max(0, PROCESSING_TIME - elapsed)
        
        if sleep_time > 0:
            logger.debug(f"Dormindo por {sleep_time:.2f}s para simular processamento lento")
            time.sleep(sleep_time)
        
        # Confirmar mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError:
        logger.error("Falha ao decodificar mensagem JSON")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        # Confirmar mesmo em caso de erro para evitar o congestionamento da fila
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Função principal para consumir mensagens do RabbitMQ"""
    try:
        # Conectar ao RabbitMQ
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        
        # Declarar exchange
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        # Declarar fila
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        # Ligar fila à exchange com a chave de roteamento
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key=ROUTING_KEY
        )
        
        # Definir QoS - processar apenas uma mensagem por vez
        channel.basic_qos(prefetch_count=1)
        
        # Começar a consumir
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=process_message
        )
        
        logger.info(f"Conectado ao RabbitMQ em {RABBITMQ_HOST}")
        logger.info(f"Consumindo mensagens da fila: {QUEUE_NAME}")
        logger.info(f"Tempo de processamento por mensagem: {PROCESSING_TIME}s")
        logger.info("Aguardando mensagens. Para sair, pressione CTRL+C")
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário. Fechando conexão...")
        if 'connection' in locals() and connection.is_open:
            connection.close()
    except Exception as e:
        logger.error(f"Erro: {e}")
        if 'connection' in locals() and connection.is_open:
            connection.close()

if __name__ == "__main__":
    # Esperar que o RabbitMQ esteja totalmente pronto
    time.sleep(10)
    main()