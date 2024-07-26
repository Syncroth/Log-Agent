# Define variables
VENV_DIR = venv
REQ_FILE = requirements.txt
DAG_SRC_DIR = dags
DAG_DEST_DIR = $(HOME)/airflow/dags

# Define .PHONY targets
.PHONY: venv copy-dags start-confluent start-airflow stop-services clean all

# Target to create a virtual environment and install requirements
venv:
	@echo "Creating virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		python3 -m venv $(VENV_DIR); \
		. $(VENV_DIR)/bin/activate; \
		pip install -r $(REQ_FILE); \
		deactivate; \
	else \
		echo "Virtual environment already exists."; \
	fi

# Target to copy DAG files
copy-dags:
	@echo "Copying DAG files..."
	@mkdir -p $(DAG_DEST_DIR)
	@cp $(DAG_SRC_DIR)/*.py $(DAG_DEST_DIR)
	@echo "DAG files copied to $(DAG_DEST_DIR)."

# Target to start Confluent services
start-confluent:
	@echo "Starting Confluent services..."
	confluent local services zookeeper start
	confluent local services kafka start

# Target to start Airflow scheduler and webserver
start-airflow:
	@echo "Starting Airflow scheduler and webserver..."
	. $(VENV_DIR)/bin/activate; \
	airflow scheduler & \
	airflow webserver & \
	deactivate
	@echo "Airflow scheduler and webserver started in the background."

# Target to stop Confluent and Airflow services
stop-services:
	@echo "Stopping Confluent and Airflow services..."
	confluent local services stop
	pkill -f airflow || true
	@echo "Confluent and Airflow services stopped."

# Target to clean up the environment
clean:
	@echo "Cleaning up the environment..."
	rm -rf $(VENV_DIR)
	confluent local services stop
	pkill -f airflow || true
	@echo "Cleaned up the environment."



# Convenience target to run all tasks
all: venv copy-dags start-confluent start-airflow
	@echo "All tasks completed."
