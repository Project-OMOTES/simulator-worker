FROM python:3.11-slim-bookworm

WORKDIR /app/simulator_worker

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


COPY .  /app/simulator_worker/
WORKDIR /app/simulator_worker
RUN pip install .
ENTRYPOINT simulator_worker
