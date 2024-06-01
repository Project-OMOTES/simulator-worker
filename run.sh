#!/usr/bin/bash

. .venv/bin/activate
PYTHONPATH="src/" python3 -m simulator_worker
