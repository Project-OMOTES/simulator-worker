FROM python:3.11-slim-bookworm

WORKDIR /app/simulator_worker

# Install OpenJDK-21
RUN apt-get -y update  && \
    apt-get install -y openjdk-21-jdk && \
    apt-get clean;

COPY .  /app/simulator_worker/
WORKDIR /app/simulator_worker
RUN pip install --no-cache-dir -r /app/simulator_worker/requirements.txt
RUN pip install .
ENTRYPOINT ["simulator_worker"]
