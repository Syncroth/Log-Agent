# Real-Time Log Agent for System State Analysis
## Overview

This project introduces a Log Agent designed to provide real-time context and insights into the operational state of various systems. By leveraging real-time data ingestion and storage technologies, this agent offers a continuous, up-to-date view of system performance and health.

## Key Features

1. **Real-Time Data Ingestion:**
   - Utilizes Apache Kafka to ingest log data in real time.
   - Ensures immediate access to the latest information for timely analysis and response.

2. **Dynamic Vector Store Integration:**
   - Stores ingested logs in a continuously updated vector database.
   - Maintains an accurate and current representation of the system's state for efficient data retrieval and contextual analysis.

3. **Intelligent System Context:**
   - Powered by a Large Language Model (LLM) to understand and interpret the system's state.
   - Provides intelligent insights and context, aiding operators in making informed decisions based on the latest system data.

4. **Seamless Orchestration with Apache Airflow:**
   - Orchestrates the entire process to ensure smooth data flow and efficient operation.
   - Coordinates each step, from ingestion to storage and analysis, to maintain optimal system performance.

## Applications and Benefits

- **Proactive Monitoring and Response:**
  - Enables proactive monitoring with real-time insights.
  - Facilitates quick identification and resolution of potential issues, enhancing system reliability and reducing downtime.

- **Informed Decision-Making:**
  - Provides continuous access to real-time data and intelligent analysis.
  - Supports well-informed decisions to optimize system performance and address emerging challenges promptly.

- **Operational Efficiency:**
  - Integrates real-time ingestion, dynamic storage, and intelligent context analysis.
  - Streamlines operations, improving overall system efficiency and reducing operational risks.


## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.x
- pip
- Confluent Platform
- Apache Airflow

## Getting Started

1. **Clone the repository**:
    ```sh
    git clone https://github.com/Syncroth/Log-Agent.git
    cd Log-Agent
    ```

2. **Set up your environment variables**:
    Create a `.env` file in the root directory and add your Google API key:
    ```sh
    echo "GOOGLE_API_KEY=your_api_key_here" > .env
    ```

3. **Run the `make all` command**:
    This will create a virtual environment, install the necessary requirements, copy DAG files, and start Confluent and Airflow services.
    ```sh
    make all
    ```

## Makefile Targets

- **venv**: Creates a virtual environment and installs required Python packages.
    ```sh
    make venv
    ```

- **copy-dags**: Copies DAG files to the Airflow directory.
    ```sh
    make copy-dags
    ```

- **start-confluent**: Starts the Confluent services (Zookeeper and Kafka).
    ```sh
    make start-confluent
    ```

- **start-airflow**: Starts the Airflow scheduler and webserver.
    ```sh
    make start-airflow
    ```

- **stop-services**: Stops Confluent and Airflow services.
    ```sh
    make stop-services
    ```

- **clean**: Cleans up the environment by removing the virtual environment and stopping services.
    ```sh
    make clean
    ```

- **all**: Runs all the above tasks in sequence.
    ```sh
    make all
    ```

## Notes

- Ensure the Confluent Platform and Apache Airflow are properly installed and configured on your machine.
- The `GOOGLE_API_KEY` is required for certain functionalities. Make sure to replace `your_api_key_here` with your actual API key.
- The `make all` command is a convenience target that automates the setup and starting of services.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
