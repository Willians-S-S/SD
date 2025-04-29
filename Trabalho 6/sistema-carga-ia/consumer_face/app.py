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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin123')
PROCESSING_TIME = int(os.getenv('PROCESSING_TIME', 3))  # Seconds per message

# Exchange and queue configuration
EXCHANGE_NAME = 'images_exchange'
EXCHANGE_TYPE = 'topic'
QUEUE_NAME = 'face_analysis_queue'
ROUTING_KEY = 'face'

def connect_to_rabbitmq():
    """Establish connection to RabbitMQ"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    
    # Retry connection if RabbitMQ is not immediately available
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
                logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt+1}/{max_retries}). Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts: {e}")
                raise

def decode_image(encoded_image):
    """Decode base64 image to OpenCV format"""
    try:
        # Decode base64 string
        img_data = base64.b64decode(encoded_image)
        
        # Convert to PIL Image
        img = Image.open(BytesIO(img_data))
        
        # Convert to OpenCV format (numpy array)
        img_cv = np.array(img)
        
        # Convert RGB to BGR (OpenCV uses BGR)
        if len(img_cv.shape) == 3 and img_cv.shape[2] == 3:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
            
        return img_cv
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        return None

def analyze_face_emotion(image):
    """Analyze face emotion using DeepFace"""
    try:
        # Process with DeepFace - analyze emotions
        result = DeepFace.analyze(
            img_path=image,
            actions=['emotion'],
            enforce_detection=False  # Don't throw error if face not detected
        )
        
        # Can be a list or single result
        if isinstance(result, list):
            if not result:  # Empty list
                return {"error": "No face detected"}
            result = result[0]  # Take first face
            
        # Extract emotion data
        emotions = result.get('emotion', {})
        dominant_emotion = result.get('dominant_emotion', 'unknown')
        
        return {
            'dominant_emotion': dominant_emotion,
            'emotions': emotions
        }
    except Exception as e:
        logger.error(f"Error analyzing face: {e}")
        return {"error": str(e)}

def process_message(ch, method, properties, body):
    """Process incoming message"""
    try:
        # Parse message
        message = json.loads(body)
        filename = message.get('filename', 'unknown')
        image_type = message.get('type', 'unknown')
        encoded_image = message.get('image')
        
        if not encoded_image:
            logger.warning(f"Message missing image data: {filename}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        logger.info(f"Processing face image: {filename}")
        
        # Decode image
        image = decode_image(encoded_image)
        if image is None:
            logger.warning(f"Failed to decode image: {filename}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Analyze face emotion
        start_time = time.time()
        emotion_result = analyze_face_emotion(image)
        
        # Log result
        if 'error' in emotion_result:
            logger.warning(f"Failed to analyze face in {filename}: {emotion_result['error']}")
        else:
            dominant_emotion = emotion_result['dominant_emotion']
            emotions = emotion_result['emotions']
            
            # Format emotion percentages nicely
            emotions_formatted = {k: f"{v:.1f}%" for k, v in emotions.items()}
            
            logger.info(f"Face analysis for {filename}: {dominant_emotion}")
            logger.info(f"Detailed emotions: {emotions_formatted}")
        
        # Simulate slow processing to ensure queue buildup
        elapsed = time.time() - start_time
        sleep_time = max(0, PROCESSING_TIME - elapsed)
        if sleep_time > 0:
            logger.debug(f"Sleeping for {sleep_time:.2f}s to simulate slow processing")
            time.sleep(sleep_time)
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON message")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        # Acknowledge even on error to avoid clogging the queue
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Main function to consume messages from RabbitMQ"""
    try:
        # Connect to RabbitMQ
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        
        # Declare exchange
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        # Declare queue
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        # Bind queue to exchange with routing key
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key=ROUTING_KEY
        )
        
        # Set QoS - only process one message at a time
        channel.basic_qos(prefetch_count=1)
        
        # Start consuming
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=process_message
        )
        
        logger.info(f"Connected to RabbitMQ at {RABBITMQ_HOST}")
        logger.info(f"Consuming messages from queue: {QUEUE_NAME}")
        logger.info(f"Processing time per message: {PROCESSING_TIME}s")
        logger.info("Waiting for messages. To exit press CTRL+C")
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Closing connection...")
        if 'connection' in locals() and connection.is_open:
            connection.close()
    except Exception as e:
        logger.error(f"Error: {e}")
        if 'connection' in locals() and connection.is_open:
            connection.close()

if __name__ == "__main__":
    # Wait for RabbitMQ to be fully ready
    time.sleep(10)
    main()