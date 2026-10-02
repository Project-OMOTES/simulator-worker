import asyncio
from collections.abc import Mapping
from importlib import import_module, reload
from os import environ
from unittest import TestCase
from unittest.mock import AsyncMock, patch


class TestDeployFlowJobVariables(TestCase):
    """Tests for the job_variables structure built at module level."""

    def _get_job_variables(self) -> Mapping[str, object]:
        required_env = {
            "LOG_LEVEL": "INFO",
            "INFLUXDB_HOSTNAME": "omotes_influxdb",
            "INFLUXDB_PORT": "8096",
            "INFLUXDB_USERNAME": "user",
            "INFLUXDB_PASSWORD": "pass",
            "PREFECT_API_AUTH_STRING": "token",
            "PREFECT_API_URL_FOR_WORKER": "http://prefect:4200/api",
            "MINIO_HOST": "minio",
            "MINIO_EXTERNAL_URL": "http://localhost:9000",
            "MINIO_PORT": "9000",
            "MINIO_ACCESS_KEY": "access",
            "MINIO_SECRET": "secret",
            "PREFECT_WORK_POOL_NAME": "default",
            "PREFECT_FLOW_MAX_CONCURRENT_RUNS": "1",
            "PREFECT_DOCKER_WORKER_NETWORKS": "omotes,mapeditor-net",
        }
        with patch.dict(environ, required_env, clear=False):
            m = import_module("simulator_worker.prefect_deploy_flow")
            m = reload(m)

        return m.job_variables

    def test_job_variables_auto_remove_is_set(self) -> None:
        """auto_remove should be True, not left over missing from testing."""
        self.assertTrue(self._get_job_variables()["auto_remove"])

    def test_job_variables_include_all_docker_networks(self) -> None:
        """Attach flow-run containers to every configured Docker network."""
        self.assertEqual(self._get_job_variables()["networks"], ["omotes", "mapeditor-net"])

    def test_main_deploys_on_limited_work_queue(self) -> None:
        """Limit simulator runs across deployment versions on one work queue."""
        env = {
            "LOG_LEVEL": "INFO",
            "INFLUXDB_HOSTNAME": "omotes_influxdb",
            "INFLUXDB_PORT": "8096",
            "INFLUXDB_USERNAME": "user",
            "INFLUXDB_PASSWORD": "pass",
            "PREFECT_API_AUTH_STRING": "token",
            "PREFECT_API_URL_FOR_WORKER": "http://prefect:4200/api",
            "MINIO_HOST": "minio",
            "MINIO_EXTERNAL_URL": "http://localhost:9000",
            "MINIO_PORT": "9000",
            "MINIO_ACCESS_KEY": "access",
            "MINIO_SECRET": "secret",
            "PREFECT_WORK_POOL_NAME": "pool",
            "PREFECT_FLOW_MAX_CONCURRENT_RUNS": "4",
            "PREFECT_USE_LOCAL_CODE_AND_IMAGE": "false",
            "SIMULATOR_WORKER_VERSION": "1.2.3",
            "PREFECT_DOCKER_WORKER_NETWORKS": "omotes,mapeditor-net",
        }
        with patch.dict(environ, env, clear=False):
            module = reload(import_module("simulator_worker.prefect_deploy_flow"))
            with patch.object(module, "deploy_flow", new=AsyncMock()) as deploy_mock:
                asyncio.run(module.main())

        assert deploy_mock.await_args is not None
        deployment_args = deploy_mock.await_args.kwargs
        self.assertEqual(
            (
                deployment_args["deployment_name"],
                deployment_args["work_queue_name"],
                deployment_args["max_concurrent_runs"],
            ),
            ("omotes-simulator-worker:1.2.3", "omotes-simulator-worker", 4),
        )
        self.assertEqual(deployment_args["job_variables"]["networks"], ["omotes", "mapeditor-net"])
