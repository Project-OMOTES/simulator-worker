FROM python:3.11-bookworm

WORKDIR /app/simulator_worker

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt


COPY .  /app/simulator_worker/
COPY .git /app/simulator_worker/.git
WORKDIR /app/simulator_worker
RUN pip install .
#RUN ls --recursive /app/simulator_worker/
ENTRYPOINT simulator_worker
