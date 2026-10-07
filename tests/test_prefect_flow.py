from os import environ
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import esdl
import pytest
from esdl import DatabaseTypeEnum, DataTableProfile
from esdl.esdl_handler import EnergySystemHandler
from omotes_sdk.prefect_util import load_input_esdl
from prefect.states import State

from simulator_worker.prefect_flow import SimulatorFlowResult, simulator_flow

MINIO_TEST_ENV = {
    "ESDL_OUTPUT_PROFILES_TYPE": "INFLUXDB",
    "DB_HOSTNAME": "omotes_influxdb",
    "DB_PORT": "8096",
    "DB_USERNAME": "user",
    "DB_PASSWORD": "password",
    "PG_DB_TIMESERIES": "omotes_timeseries",
    "MINIO_HOST": "minio",
    "MINIO_EXTERNAL_URL": "http://localhost:9000",
    "MINIO_PORT": "9000",
    "MINIO_ACCESS_KEY": "access",
    "MINIO_SECRET": "secret",
}


@pytest.mark.parametrize("output_profiles_type", ["INFLUXDB", "POSTGRESQL"])
def test_simulator_flow_writes_datatable_profiles(output_profiles_type: str) -> None:
    """Write simulator output as DataTable profiles to the configured database."""
    # Arrange
    fixture_path = Path(__file__).parent / "data" / "esdl" / "simulator_tutorial.esdl"
    input_esdl = fixture_path.read_text()
    db_host = "omotes_postgres" if output_profiles_type == "POSTGRESQL" else "omotes_influxdb"
    db_port = "6432" if output_profiles_type == "POSTGRESQL" else "8096"

    # Act
    with (
        patch.dict(
            environ,
            MINIO_TEST_ENV
            | {
                "ESDL_OUTPUT_PROFILES_TYPE": output_profiles_type,
                "DB_HOSTNAME": db_host,
                "DB_PORT": db_port,
            },
            clear=False,
        ),
        patch("simulator_worker.prefect_flow.write_flow_return_artifact_to_minio") as write_artifact,
        patch("simulator_worker.utils.publish_job_cleanup_resource") as publish_resource,
        patch("simulator_worker.utils.Credentials.add_credential") as add_credential,
        patch("simulator_worker.utils.save_data_table_profiles_to_database") as save_profiles,
    ):
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
    output_system_id = output_handler.energy_system.id
    expected_db_type = getattr(cast(Any, DatabaseTypeEnum), output_profiles_type)
    profiles = [
        profile for profile in output_handler.energy_system.eAllContents() if isinstance(profile, DataTableProfile)
    ]
    assert profiles
    profile_keys = [
        (
            profile.configuration.type,
            profile.configuration.host,
            profile.configuration.port,
            profile.configuration.database,
            profile.schema,
            profile.tableName,
            profile.filter,
            profile.columnName,
        )
        for profile in profiles
    ]
    assert len(profile_keys) == len(set(profile_keys))
    assert all('"portId"=' in profile.filter for profile in profiles)
    assert all(profile.configuration.type == expected_db_type for profile in profiles)
    assert all(profile.configuration.host == db_host for profile in profiles)
    assert all(profile.configuration.port == int(db_port) for profile in profiles)
    if output_profiles_type == "POSTGRESQL":
        assert all(profile.configuration.database == "omotes_timeseries" for profile in profiles)
        assert all(profile.schema == output_system_id for profile in profiles)
        expected_cleanup = {
            "type": "postgresql",
            "host": db_host,
            "port": int(db_port),
            "database": "omotes_timeseries",
            "schema": output_system_id,
        }
    else:
        assert all(profile.configuration.database == output_system_id for profile in profiles)
        expected_cleanup = {
            "type": "influxdb",
            "host": db_host,
            "port": int(db_port),
            "database": output_system_id,
        }
    cleanup_resource = publish_resource.call_args.args[0].model_dump(mode="json", exclude_none=True, by_alias=True)
    assert cleanup_resource == expected_cleanup
    save_calls = save_profiles.call_args_list
    assert len(save_calls) == len({profile.filter.split("'")[1] for profile in profiles})
    saved_managers = [manager for call in save_calls for manager in call.args[0]]
    assert len(saved_managers) == len(profiles)
    assert all(manager.profile_data_list for manager in saved_managers)
    for call in save_calls:
        managers = call.args[0]
        tags = call.kwargs["additional_tags"]
        assert len({manager.data_table_profile.filter.split("'")[1] for manager in managers}) == 1
        assert tags["assetId"] == managers[0].data_table_profile.filter.split("'")[1]
        assert tags["simulationRun"] == output_system_id
        assert tags["simulation_type"] == "omotes-simulator"
        asset = next(
            item
            for item in output_handler.energy_system.eAllContents()
            if isinstance(item, esdl.Asset) and item.id == tags["assetId"]
        )
        capabilities = [esdl.Transport, esdl.Conversion, esdl.Consumer, esdl.Producer]
        expected_capability = next(
            (capability.__name__ for capability in capabilities if capability in asset.__class__.__mro__),
            "None",
        )
        assert tags == {
            "assetClass": asset.__class__.__name__,
            "assetId": asset.id,
            "assetName": asset.name,
            "capability": expected_capability,
            "simulationRun": output_system_id,
            "simulation_type": "omotes-simulator",
        }
    add_credential.assert_called_once_with(f"{db_host}:{db_port}", "user", "password")


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


def test_simulator_flow_returns_failed_state_when_failure_artifact_write_fails() -> None:
    """A MinIO error while writing the failure artifact must not mask the original error."""
    with (
        patch.dict(environ, MINIO_TEST_ENV, clear=False),
        patch(
            "simulator_worker.prefect_flow.load_input_esdl",
            side_effect=ConnectionError("minio unreachable"),
        ),
        patch(
            "simulator_worker.prefect_flow.write_flow_return_artifact_to_minio",
            side_effect=ConnectionError("minio still unreachable"),
        ) as write_artifact,
    ):
        result = simulator_flow.fn(
            input_esdl_minio_path="s3://prefect-results/flow-results/simulator-run/input.esdl",
            workflow_config={},
            workflow_type_name="simulator",
            flow_results_folder="simulator-run",
        )

    assert isinstance(result, State)
    assert result.is_failed()
    assert result.message == "Simulator flow failed: minio unreachable"
    write_artifact.assert_called_once()
