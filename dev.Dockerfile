FROM python:3.11-slim-bookworm

WORKDIR /app/simulator_worker

COPY simulator-worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ../omotes-sdk-protocol/python/ /omotes-sdk-protocol/python/
COPY ../omotes-sdk-python/ /omotes-sdk-python/
RUN pip install -e /omotes-sdk-python/
RUN pip install -e /omotes-sdk-protocol/python/

COPY simulator-worker/  /app/simulator_worker/
#COPY simulator-worker/.git /app/simulator_worker/.git
WORKDIR /app/simulator_worker
RUN pip install .
ENTRYPOINT simulator_worker
