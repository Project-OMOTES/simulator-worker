from os import environ
from pathlib import Path
from unittest.mock import patch

from esdl.esdl_handler import EnergySystemHandler
from omotes_sdk.prefect_util import load_input_esdl
from prefect.states import State

from simulator_worker.prefect_flow import SimulatorFlowResult, simulator_flow

MINIO_TEST_ENV = {
    "INFLUXDB_HOSTNAME": "omotes_influxdb",
    "INFLUXDB_PORT": "8096",
    "MINIO_HOST": "minio",
    "MINIO_EXTERNAL_URL": "http://localhost:9000",
    "MINIO_PORT": "9000",
    "MINIO_ACCESS_KEY": "access",
    "MINIO_SECRET": "secret",
}


def test_optimizer_flow_runs_delft_esdl() -> None:
    """Run the optimizer flow with the same fixture as the local runner."""
    # Arrange
    fixture_path = Path(__file__).parent / "data" / "esdl" / "simulator_tutorial.esdl"
    input_esdl = fixture_path.read_text()

    # Act
    with (
        patch.dict(environ, MINIO_TEST_ENV, clear=False),
        patch("simulator_worker.prefect_flow.write_flow_return_artifact_to_minio") as write_artifact,
        patch("simulator_worker.utils.publish_job_cleanup_resource") as publish_resource,
        patch("simulator_worker.utils.InfluxDBProfileManager") as profile_manager_cls,
    ):
        profile_manager_cls.return_value.profile_header = ["datetime"]
        profile_manager_cls.return_value.save_influxdb.return_value = None

        result = simulator_flow.fn(
            input_esdl_minio_path=input_esdl,
            workflow_config={
                "timestep": 3600,
                "start_time": "2019-01-01T00:00:00.000Z",
                "end_time": "2019-01-03T00:00:00.000Z",
            },
            workflow_type_name="simulator",
            flow_results_folder="test-simulator-run",
        )

    # Assert
    assert isinstance(result, SimulatorFlowResult)
    assert result.output_esdl is not None
    assert write_artifact.call_args.args[5] == "http://localhost:9000"
    assert write_artifact.call_args.kwargs["flow_results_folder"] == "test-simulator-run"
    output_handler = EnergySystemHandler()
    output_handler.load_from_string(result.output_esdl)
    assert publish_resource.call_args.args[0].model_dump(mode="json", exclude_none=True) == {
        "type": "influxdb",
        "host": "omotes_influxdb",
        "port": 8096,
        "database": output_handler.energy_system.id,
    }


def test_load_input_esdl_reads_minio_reference() -> None:
    """Read the input ESDL from the orchestrator's shared flow-results folder."""
    with patch("omotes_sdk.prefect_util.RemoteFileSystem") as remote_filesystem:
        remote_filesystem.return_value.read_path.return_value = b"<esdl />"
        result = load_input_esdl(
            "s3://prefect-results/flow-results/simulator-run/input.esdl", "minio", "9000", "access", "secret"
        )

    assert result == "<esdl />"
    remote_filesystem.return_value.read_path.assert_called_once_with("flow-results/simulator-run/input.esdl")


def test_simulator_flow_writes_failure_to_shared_folder() -> None:
    """Preserve the orchestrator's result folder when input loading fails."""
    with (
        patch.dict(environ, MINIO_TEST_ENV, clear=False),
        patch("simulator_worker.prefect_flow.load_input_esdl", side_effect=ValueError("missing input")) as load_input,
        patch("simulator_worker.prefect_flow.write_flow_return_artifact_to_minio") as write_artifact,
    ):
        result = simulator_flow.fn(
            input_esdl_minio_path="s3://prefect-results/flow-results/simulator-run/input.esdl",
            workflow_config={},
            workflow_type_name="simulator",
            flow_results_folder="simulator-run",
        )

    assert isinstance(result, State)
    assert result.is_failed()
    load_input.assert_called_once_with(
        "s3://prefect-results/flow-results/simulator-run/input.esdl", "minio", "9000", "access", "secret"
    )
    assert write_artifact.call_args.kwargs["flow_results_folder"] == "simulator-run"
