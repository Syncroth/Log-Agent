from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

print(os.getcwd())

default_args={
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    }


with DAG(
    'smart_logs_pipeline',
    default_args= default_args,
    description='A pipeline to process logs and answer questions using LLM',
    schedule= timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],


) as dag :
    
    t1 = BashOperator(
        task_id='produce_logs',
        bash_command='python3 /home/roomless/projects/smart_log_analyzer/Log-Agent/src/producer.py'
    )

    t2 = BashOperator(
        task_id='consume_logs',
        bash_command='python3 /home/roomless/projects/smart_log_analyzer/Log-Agent/src/consumer.py'
    )

    t3 = BashOperator(
        task_id='llm_agent',
        bash_command='python3 /home/roomless/projects/smart_log_analyzer/Log-Agent/src/log_agent.py'
    )

    t1 >> t2 >> t3





