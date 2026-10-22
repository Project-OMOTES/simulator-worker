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

### Deploy flow to Prefect

There are different ways to deploy the Prefect flow:

- locally to a Prefect instance using local code
- automatically to the NWN MapEditor environments when a container image is published

The deployment is registered as `omotes-simulator-worker:<version>` and runs on the
`omotes-simulator-worker` work queue. Its concurrency limit is configured with
`PREFECT_FLOW_MAX_CONCURRENT_RUNS` (4 in the NWN MapEditor environments).

#### Local Prefect deployment

In VS Code, go to the debug view and run `prefect_deploy_flow`. This creates or updates a deployment on the Prefect
instance configured by `PREFECT_API_URL`.

During development, set `PREFECT_USE_LOCAL_CODE_AND_IMAGE=true` in `.env` to build and deploy a local image instead
of using a published image. To use local code for `omotes-sdk-python` as well, set `PREFECT_USE_LOCAL_SDK=true`.

#### Deployment via GitHub

Publishing a tagged container image automatically registers the deployment on the NWN MapEditor TEST environment.
The same image is then deployed to PROD after approval of the `nwn-me-production` GitHub environment. See the
[deployment workflow](https://github.com/Project-OMOTES/simulator-worker/actions).

### Update omotes-simulator-core version and deploy flow on NWN MapEditor environments

Make sure to have the required [tools](#tools) installed.

Create an issue in the [simulator-worker repository](https://github.com/Project-OMOTES/simulator-worker/issues),
create a branch for the issue, and pull it locally. Update the `omotes-simulator-core` version in
[pyproject.toml](pyproject.toml), then run (on Windows, use a `Git Bash` terminal):

```bash
uv lock
uv sync --locked --group dev
just ci
```

This updates and installs the package versions, then runs the CI checks locally.

Commit the changes to [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock), then push them to GitHub. Optionally,
create a pull request and merge it into `main`.

Create a new release in the [simulator-worker releases](https://github.com/Project-OMOTES/simulator-worker/releases):

1. Choose **Create a new release** and create a new tag.
2. Select `main` (or the intended development branch) as the target.
3. Select the previous tag; do not leave it set to automatic.
4. Generate release notes.
5. Optionally select **Set as a pre-release**.
6. Publish the release.

Publishing the tag builds and publishes a new Docker image, then deploys its Prefect flow to NWN MapEditor TEST.
Approval is required before deployment to PROD; follow the
[deployment workflow](https://github.com/Project-OMOTES/simulator-worker/actions).

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
