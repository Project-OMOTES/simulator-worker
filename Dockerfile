FROM python:3.11-slim-bookworm

WORKDIR /app/simulator_worker


# Install required tools and OpenJDK 21 manually
RUN apt-get update && \
    apt-get install -y wget tar ca-certificates && \
    apt-get clean && \
    wget https://download.java.net/java/GA/jdk21.0.2/f2283984656d49d69e91c558476027ac/13/GPL/openjdk-21.0.2_linux-x64_bin.tar.gz && \
    tar -xzf openjdk-21.0.2_linux-x64_bin.tar.gz && \
    mv jdk-21.0.2 /usr/local/openjdk-21 && \
    rm openjdk-21.0.2_linux-x64_bin.tar.gz

# Set environment variables for Java
ENV JAVA_HOME=/usr/local/openjdk-21
ENV PATH="$JAVA_HOME/bin:$PATH"


COPY .  /app/simulator_worker/
WORKDIR /app/simulator_worker
RUN pip install --no-cache-dir -r /app/simulator_worker/requirements.txt
RUN pip install .
ENTRYPOINT ["simulator_worker"]
