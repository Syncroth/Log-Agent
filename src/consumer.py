#!/usr/bin/env python3

from confluent_kafka import Consumer
from confluent_kafka import Consumer, KafkaError
import uuid
import time
import os
import yaml
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma

from langchain_core.documents.base import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load config file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(os.path.join(script_dir, "..", "config.yaml"))
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

kafka_config = config["kafka"]
processing_config = config["processing"]

# Load environment variables
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
model=ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key, verbose=True)
embedding_function = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

database_path = os.path.abspath(os.path.join(script_dir, "..", "database/chroma_db"))
vectorstore = Chroma("logs_store", embedding_function, persist_directory=database_path)


consumer_config = {
    'bootstrap.servers': kafka_config['bootstrap_servers'],
    'group.id': f"{kafka_config['group_id_prefix']}{uuid.uuid4()}",
    'auto.offset.reset': kafka_config['auto_offset_reset'],
    'enable.auto.commit': kafka_config['enable_auto_commit']
}

# config variables 
batch_size = processing_config['batch_size']
max_messages = processing_config['max_messages']

idle_timeout = processing_config['idle_timeout']

# Create a Consumer instance
consumer = Consumer(consumer_config)

running = True
idle_timeout = processing_config['idle_timeout']  # Time in seconds to wait for new messages before shutting down

last_message_time = time.time()
message_timer = 0

# Create a thread pool executor
executor = ThreadPoolExecutor(max_workers=5)
 
messages= []
def consume_messages(consumer,topics) -> None:
    global running, last_message_time, messages, message_timer
    try:
        consumer.subscribe(topics)
        while running:
            if max_messages and message_timer >= max_messages:
                print(f"Processed {message_timer} messages, shutting down...")
                shutdown()

            msg= consumer.poll(timeout=5.0)
            if msg is None:
                if time.time() - last_message_time > idle_timeout:
                    print("Idle timeout exceeded, shutting down...")
                    shutdown()
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f'{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')

                else:
                    print(f"Error: {msg.error()}")
                continue
                
            
            messages.append(msg_process(msg))
            last_message_time = time.time()
            message_timer += 1
            if len(messages) >= batch_size:
                batch = messages[:batch_size]

                messages = messages[batch_size:]
                executor.submit(process_batch, batch)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print(f"Messages processed: {message_timer}")
        consumer.close()
        executor.shutdown(wait=True)

def shutdown():
    global running
    running = False

def msg_process(msg):
    # Process the message
    message_content = Document(page_content=msg.value().decode('utf-8'), metadata={"source": "kafka_topic logs"})
    print(f"Received message: {msg.value().decode('utf-8')} \n --------------------------------- \n")
    print(f"Size of messages: {len(messages)}")
    return message_content

def process_batch(batch):
    global vectorstore
    print(f"Processing batch of {len(batch)} messages")
    vectorstore.add_documents(batch)


topics = kafka_config['topics']

consume_messages(consumer, topics)