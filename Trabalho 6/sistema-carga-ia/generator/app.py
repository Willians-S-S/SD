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
MESSAGE_RATE = int(os.getenv('MESSAGE_RATE', 5))  # Messages per second

# Exchange and queue configuration
EXCHANGE_NAME = 'images_exchange'
EXCHANGE_TYPE = 'topic'

# Image paths
FACES_DIR = '/app/images/faces'
TEAMS_DIR = '/app/images/teams'

def get_image_files(directory):
    """Get list of image files from directory"""
    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        return []
    
    extensions = ['*.jpg', '*.jpeg', '*.png']
    image_files = []
    
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    return image_files

def encode_image(image_path):
    """Encode image to base64 string"""
    try:
        with Image.open(image_path) as img:
            # Resize to reasonable dimensions if needed
            if max(img.size) > 800:
                img.thumbnail((800, 800))
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to BytesIO object
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_str
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

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

def main():
    """Main function to send messages to RabbitMQ"""
    # Load image files
    face_images = get_image_files(FACES_DIR)
    team_images = get_image_files(TEAMS_DIR)
    
    if not face_images:
        logger.warning(f"No face images found in {FACES_DIR}")
    if not team_images:
        logger.warning(f"No team images found in {TEAMS_DIR}")
    
    if not face_images and not team_images:
        logger.error("No images found. Exiting.")
        return
    
    # Connect to RabbitMQ
    try:
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        
        # Declare exchange
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        logger.info(f"Connected to RabbitMQ at {RABBITMQ_HOST}")
        logger.info(f"Found {len(face_images)} face images and {len(team_images)} team images")
        logger.info(f"Sending messages at rate of {MESSAGE_RATE} per second")
        
        # Send messages continuously
        message_count = 0
        interval = 1.0 / MESSAGE_RATE  # Time between messages
        
        while True:
            # Decide which type of image to send (alternating or random)
            if random.random() < 0.5 and face_images:
                # Face image
                image_path = random.choice(face_images)
                routing_key = "face"
                image_type = "face"
            elif team_images:
                # Team image
                image_path = random.choice(team_images)
                routing_key = "team"
                image_type = "team"
            else:
                # Fall back to whatever we have
                image_path = random.choice(face_images or team_images)
                routing_key = "face" if image_path in face_images else "team"
                image_type = "face" if image_path in face_images else "team"
            
            # Encode image
            encoded_image = encode_image(image_path)
            if encoded_image:
                # Create message
                message = {
                    "type": image_type,
                    "filename": os.path.basename(image_path),
                    "image": encoded_image,
                    "timestamp": time.time()
                }
                
                # Publish message
                channel.basic_publish(
                    exchange=EXCHANGE_NAME,
                    routing_key=routing_key,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type='application/json'
                    )
                )
                
                message_count += 1
                if message_count % 10 == 0:
                    logger.info(f"Sent {message_count} messages ({routing_key}: {os.path.basename(image_path)})")
                
                # Sleep to maintain message rate
                time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Closing connection...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    # Wait for RabbitMQ to be fully ready
    time.sleep(5)
    main()