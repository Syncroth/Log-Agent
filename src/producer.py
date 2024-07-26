#!/usr/bin/env python3

from confluent_kafka import Producer
import yaml
import os

# Load config file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(os.path.join(script_dir, "..", "config.yaml"))

print(f"This is the config path: {config_path}")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)
# Define the producer config 
producer_config = { 
    'bootstrap.servers': config['kafka']['bootstrap_servers'],
}

# create a producer instance
producer = Producer(producer_config)

def preprocess_logs(file_path) -> set:
    logs = set()

    with open(file_path,'r') as f:
        for line in f:
            logs.add(line)
    return logs

def delivery_report(err, msg):
    """Callback for Kafka's producer delivery reports. """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_log(file_path, topic, sample_size=10000, full_log=False):
    if full_log: sample_size = None
    logs_sample = list(preprocess_logs(file_path))[:sample_size]
    for log in logs_sample:
        producer.produce(topic, value=log.encode('utf-8'), callback=delivery_report)
        producer.poll(0)

    producer.flush()

log_file_path = os.path.abspath(os.path.join(script_dir,"..",config['log_file_path']))

topic = config['kafka']['topics'][0]
if __name__ == '__main__':
    produce_log(log_file_path, 'logs', full_log=True)
    print("Log file has been ingested into the Kafka topic.")

