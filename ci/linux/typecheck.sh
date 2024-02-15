#!/usr/bin/env sh

. .venv/bin/activate
python -m mypy ./src/simulator_worker ./unit_test/
