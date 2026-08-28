from os import environ
from pathlib import Path
from unittest.mock import patch

from simulator_worker.prefect_flow import SimulatorFlowResult, simulator_flow

MINIO_TEST_ENV = {
    "MINIO_HOST": "minio",
    "MINIO_HOST_EXTERNAL": "localhost",
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
        patch("simulator_worker.utils.InfluxDBProfileManager") as profile_manager_cls,
    ):
        profile_manager_cls.return_value.profile_header = ["datetime"]
        profile_manager_cls.return_value.save_influxdb.return_value = None

        result = simulator_flow.fn(
            input_esdl=input_esdl,
            workflow_config={
                "timestep": 3600,
                "start_time": "2019-01-01T00:00:00.000Z",
                "end_time": "2019-01-03T00:00:00.000Z",
            },
            workflow_type_name="simulator",
        )

    # Assert
    assert isinstance(result, SimulatorFlowResult)
    assert result.output_esdl is not None
    assert write_artifact.call_args.args[5] == "localhost"
