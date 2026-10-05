# OMOTES simulator-worker

This repository is part of the 'Nieuwe Warmte Nu Design Toolkit' project.

## Development

### Tools

This project uses:

- **uv**: Fast Python package manager and resolver. Install via [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- **just**: Command runner for common tasks (similar to Make). Install via [https://github.com/casey/just](https://github.com/casey/just)

### Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Copy `.env.template` to `.env`

**Note** to use local code for sdk run `.venv/bin/pip install -e ../omotes-sdk-python/`.

### Run/debug the prefect flow function locally

In vscode go to the debug view and run `run_simulator_flow_function`. This runs the function without prefect.

### Lint/typecheck/test locally

Run via just (also used in in github actions):

```bash
just ci            # run all CI checks (lint, security, format-check, typecheck, test)

just lint          # ruff
just security      # ruff security
just format        # ruff format
just format-check  # verify formatting
just typecheck     # ty type checking
just test          # pytest
```

To debug test go to the debug view in vscode and run "pytest".\
When using an editable install of the sdk, don't use the just command as `uv run ...` will remove this editable install.

### Deploy flow to prefect

In vscode go to the debug view and run `prefect_deploy_flow`.\
This will create a deployment on prefect (to the prefect instance on `PREFECT_API_URL`).\

During development you may want to deploy local code of this repo instead of an already published image, then set `PREFECT_USE_LOCAL_CODE_AND_IMAGE=true` in `.env`.
To also use local code for the omotes-sdk-python set `PREFECT_USE_LOCAL_SDK=true` as well.

## Project Structure

```text
simulator-worker/
├── src/
│   ├── simulator_worker/
│   │   ├── __init__.py              # Package exports and version metadata
│   │   ├── env.py                   # Environment variable access helpers
│   │   ├── prefect_deploy_flow.py   # Prefect deployment registration script
│   │   ├── prefect_flow.py          # Prefect flow entry point for simulator runs
│   │   ├── py.typed                 # Marker for typed package consumers
│   │   └── utils.py                 # ESDL/profile/KPI support utilities
│   └── simulator_worker.egg-info/   # Generated package metadata
├── tests/
│   ├── data/                        # Test fixtures used by flow/integration tests
│   ├── test_hello.py                # Unit tests for config parsing and date indexing
│   ├── test_kpi_integration.py      # KPI integration tests for simulator output ESDL
│   ├── test_prefect_deploy_flow.py  # Tests for Prefect deployment job variables
│   └── test_prefect_flow.py         # Tests for local Prefect flow execution
├── testdata/                        # ESDL and pickle fixtures for local/manual runs
├── doc/
│   ├── dev_documentation/           # Sphinx developer documentation
│   └── user_documentation/          # Sphinx user documentation
├── .github/workflows/               # GitHub Actions CI and publish workflows
├── Dockerfile                       # Runtime container image definition
├── dev.Dockerfile                   # Development container image using local SDK code
├── justfile                         # Task runner commands
├── pyproject.toml                   # Project metadata, dependencies, and tool config
├── uv.lock                          # Locked dependency resolution
├── CHANGELOG.md                     # Release notes
├── CONTRIBUTING.md                  # Contribution guidelines
├── LICENSE
└── README.md
```
