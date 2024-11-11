FROM python:3.11-slim-bookworm

WORKDIR /app/simulator_worker

# Install OpenJDK-17
RUN apt-get -y update  && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean;

COPY .  /app/simulator_worker/
WORKDIR /app/simulator_worker
RUN pip install --no-cache-dir -r /app/simulator_worker/requirements.txt
RUN pip install .
ENTRYPOINT ["simulator_worker"]
