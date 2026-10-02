FROM python:3.11-slim-bookworm

# WORKDIR /app/simulator_worker

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

WORKDIR /src

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

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
# enable running commands without 'uv run'
ENV PATH="/src/.venv/bin:$PATH"

COPY src .