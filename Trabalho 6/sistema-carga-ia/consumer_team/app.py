#!/usr/bin/env python
import os
import time
import json
import base64
import logging
import pika
import numpy as np
import cv2
import tensorflow as tf
from PIL import Image
from io import BytesIO
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
PROCESSING_TIME = int(os.getenv('PROCESSING_TIME', 4))  # Segundos por mensagem

# Configuração da exchange e da fila
EXCHANGE_NAME = 'images_exchange'
EXCHANGE_TYPE = 'topic'
QUEUE_NAME = 'team_identification_queue'
ROUTING_KEY = 'team'

# Lista de times de futebol comuns para identificação
SOCCER_TEAMS = [
    "Barcelona", "Real Madrid", "Manchester United", "Liverpool", 
    "Bayern Munich", "Juventus", "Paris Saint-Germain", "Chelsea",
    "Arsenal", "AC Milan", "Inter Milan", "Borussia Dortmund",
    "Ajax", "Benfica", "Flamengo", "Boca Juniors", "River Plate",
    "Santos", "Corinthians", "São Paulo", "Palmeiras", "Fluminense",
    "Grêmio", "Internacional", "Cruzeiro", "Vasco da Gama",
    "Atlético Mineiro", "Botafogo", "Manchester City", "Tottenham"
]

class TeamIdentifier:
    """Classe para identificar logos de times de futebol"""
    
    def __init__(self):
        """Inicializar o identificador de times"""
        # Carregar o modelo MobileNetV2 pré-treinado com ImageNet
        self.model = tf.keras.applications.MobileNetV2(weights='imagenet') # Alterado para self.model
        
        # Usaremos este modelo para extração de características
        logger.info("Modelo de identificação de times carregado")
        
    def preprocess_image(self, image):
        """Pré-processar a imagem para o modelo"""
        # Redimensionar para 224x224
        image_resized = cv2.resize(image, (224, 224))

        # Converter BGR para RGB, se necessário
        if len(image_resized.shape) == 3 and image_resized.shape[2] == 3:
            image_resized = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        
        # Expandir dimensões e pré-processar para MobileNetV2
        img_array = np.expand_dims(image_resized, axis=0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        return img_array
    
    def identify_team(self, image): # Removido extract_features, pois usaremos diretamente decode_predictions
        """Identificar o time de futebol a partir do logo"""
        try:
            # Pré-processar a imagem
            img_array = self.preprocess_image(image)

            # Fazer a previsão usando o modelo carregado
            predictions = self.model.predict(img_array)

            # Decodificar as top 5 previsões
            decoded = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=5)[0]

            # Extrair os resultados formatados
            top_predictions = []
            for i, (imagenet_id, label, confidence) in enumerate(decoded):
                top_predictions.append({"team": label, "confidence": float(confidence)})  # Usar o label como "team" para este exemplo

            # Determinar o time identificado (usando a predição de maior confiança)
            identified_team = top_predictions[0]["team"]
            confidence = top_predictions[0]["confidence"]

            # Formatar para retorno
            return {
                "identified_team": identified_team,
                "confidence": confidence,
                "top_predictions": top_predictions
            }

        except Exception as e:
            logger.error(f"Erro ao identificar o time: {e}")
            return {"error": str(e)}
        
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
        logger.error(f"Erro ao decodificar a imagem: {e}")
        return None

def process_message(ch, method, properties, body):
    """Processar mensagem recebida"""
    try:
        # Analisar mensagem
        message = json.loads(body)
        filename = message.get('filename', 'unknown')
        image_type = message.get('type', 'unknown')
        encoded_image = message.get('image')
        
        if not encoded_image:
            logger.warning(f"Mensagem faltando dados da imagem: {filename}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        logger.info(f"Processando imagem do logo do time: {filename}")
        
        # Decodificar imagem
        image = decode_image(encoded_image)
        if image is None:
            logger.warning(f"Falha ao decodificar a imagem: {filename}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Processar com o identificador de times
        start_time = time.time()
        team_result = team_identifier.identify_team(image)
        
        # Registrar resultado
        if 'error' in team_result:
            logger.warning(f"Falha ao identificar o time em {filename}: {team_result['error']}")
        else:
            team_name = team_result['identified_team']
            confidence = team_result['confidence']
            top_predictions = team_result['top_predictions']
            
            logger.info(f"Identificação do time para {filename}: {team_name} (Confiança: {confidence:.1%})")
            
            # Registrar as 3 principais previsões
            top3 = top_predictions[:3]
            top3_formatted = [f"{pred['team']} ({pred['confidence']:.1%})" for pred in top3]
            logger.info(f"Top 3 previsões: {', '.join(top3_formatted)}")
        
        # Simular processamento lento para garantir o acúmulo na fila
        elapsed = time.time() - start_time
        sleep_time = max(0, PROCESSING_TIME - elapsed)
        if sleep_time > 0:
            logger.debug(f"Dormindo por {sleep_time:.2f}s para simular processamento lento")
            time.sleep(sleep_time)
        
        # Confirmar mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError:
        logger.error("Falha ao decodificar a mensagem JSON")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Erro ao processar a mensagem: {e}")
        # Confirmar mesmo em caso de erro para evitar o congestionamento da fila
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Função principal para consumir mensagens do RabbitMQ"""
    try:
        # Inicializar o identificador de times
        global team_identifier
        team_identifier = TeamIdentifier()
        
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