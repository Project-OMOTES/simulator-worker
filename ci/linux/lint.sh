#!/usr/bin/env bash

if [[ "$OSTYPE" != "win32" && "$OSTYPE" != "msys" ]]; then
  echo "Activating .venv first."
  . .venv/bin/activate
fi

flake8 ./src/simulator_worker ./unit_test/
