#!/usr/bin/bash

. .venv/bin/activate
cd src/
python -m simulator_worker.simulator_worker
