FROM python:3.11-slim-bookworm

WORKDIR /app/simulator_worker

# Install OpenJDK-17
RUN apt-get -y update  && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean;

COPY simulator-worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install local versions of sdk and protocol
COPY ../omotes-sdk-protocol/python/ /omotes-sdk-protocol/python/
COPY ../omotes-sdk-python/ /omotes-sdk-python/
RUN pip install /omotes-sdk-python/
RUN pip install /omotes-sdk-protocol/python/

COPY simulator-worker/  /app/simulator_worker/
WORKDIR /app/simulator_worker
RUN pip install .
ENTRYPOINT ["simulator_worker"]
