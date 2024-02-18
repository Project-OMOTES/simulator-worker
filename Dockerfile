FROM python:3.11-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY src/simulator_worker /app/

ENTRYPOINT python -m simulator_worker.simulator_worker