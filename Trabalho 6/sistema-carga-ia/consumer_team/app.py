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
PROCESSING_TIME = int(os.getenv('PROCESSING_TIME', 4))  # Seconds per message

# Exchange and queue configuration
EXCHANGE_NAME = 'images_exchange'
EXCHANGE_TYPE = 'topic'
QUEUE_NAME = 'team_identification_queue'
ROUTING_KEY = 'team'

# List of common soccer teams for identification
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
    """Class to identify soccer team logos"""
    
    def __init__(self):
        """Initialize the team identifier"""
        # Load the MobileNetV2 model pre-trained on ImageNet
        self.base_model = tf.keras.applications.MobileNetV2(
            weights='imagenet',
            include_top=True,
            input_shape=(224, 224, 3)
        )
        
        # We'll use this model for feature extraction
        logger.info("Team identification model loaded")
        
    def preprocess_image(self, image):
        """Preprocess image for the model"""
        # Resize to 224x224
        image_resized = cv2.resize(image, (224, 224))
        
        # Convert BGR to RGB if needed
        if len(image_resized.shape) == 3 and image_resized.shape[2] == 3:
            image_resized = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        
        # Expand dimensions and preprocess for MobileNetV2
        img_array = np.expand_dims(image_resized, axis=0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        return img_array
    
    def extract_features(self, preprocessed_image):
        """Extract features from the image"""
        features = self.base_model.predict(preprocessed_image)
        return features
    
    def identify_team(self, image):
        """Identify the soccer team from the logo"""
        try:
            # Preprocess the image
            preprocessed = self.preprocess_image(image)
            
            # Extract features
            features = self.extract_features(preprocessed)
            
            # In a real system, we would match these features against a database
            # of known team logos. For this demo, we'll simulate with random confidence.
            
            # Simulate classification (in real-world, use a classifier trained on team logos)
            # We'll randomly select a team with high confidence to simulate identification
            team_index = np.random.randint(0, len(SOCCER_TEAMS))
            team_name = SOCCER_TEAMS[team_index]
            
            # Generate confidence scores (simulate a prediction)
            confidence_scores = np.random.dirichlet(np.ones(5), size=1)[0]
            
            # Create top 5 predictions with confidence scores
            top_teams = np.random.choice(SOCCER_TEAMS, size=5, replace=False)
            predictions = [
                {"team": team, "confidence": float(score)}
                for team, score in zip(top_teams, confidence_scores)
            ]
            
            # Sort by confidence (highest first)
            predictions.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Set first prediction to our "identified" team with high confidence
            predictions[0]["team"] = team_name
            predictions[0]["confidence"] = float(np.random.uniform(0.7, 0.95))
            
            # Format for return
            return {
                "identified_team": team_name,
                "confidence": predictions[0]["confidence"],
                "top_predictions": predictions
            }
            
        except Exception as e:
            logger.error(f"Error identifying team: {e}")
            return {"error": str(e)}

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
        
        logger.info(f"Processing team logo image: {filename}")
        
        # Decode image
        image = decode_image(encoded_image)
        if image is None:
            logger.warning(f"Failed to decode image: {filename}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Process with team identifier
        start_time = time.time()
        team_result = team_identifier.identify_team(image)
        
        # Log result
        if 'error' in team_result:
            logger.warning(f"Failed to identify team in {filename}: {team_result['error']}")
        else:
            team_name = team_result['identified_team']
            confidence = team_result['confidence']
            top_predictions = team_result['top_predictions']
            
            logger.info(f"Team identification for {filename}: {team_name} (Confidence: {confidence:.1%})")
            
            # Log top 3 predictions
            top3 = top_predictions[:3]
            top3_formatted = [f"{pred['team']} ({pred['confidence']:.1%})" for pred in top3]
            logger.info(f"Top 3 predictions: {', '.join(top3_formatted)}")
        
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
        # Initialize team identifier
        global team_identifier
        team_identifier = TeamIdentifier()
        
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