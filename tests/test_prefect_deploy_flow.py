import asyncio
from collections.abc import Mapping
from importlib import import_module, reload
from os import environ
from pathlib import Path
from unittest import TestCase
from unittest.mock import AsyncMock, patch


class TestDeployFlowJobVariables(TestCase):
    """Tests for the job_variables structure built at module level."""

    def _get_job_variables(
        self, extra_env: Mapping[str, str] | None = None, unset: tuple[str, ...] = ()
    ) -> Mapping[str, object]:
        required_env = {
            "LOG_LEVEL": "INFO",
            "ESDL_OUTPUT_PROFILES_TYPE": "POSTGRESQL",
            "DB_HOSTNAME": "db",
            "DB_PORT": "5432",
            "DB_USERNAME": "user",
            "DB_PASSWORD": "pass",
            "PG_DB_TIMESERIES": "timeseries",
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
            "PREFECT_USE_LOCAL_CODE_AND_IMAGE": "false",
            "SIMULATOR_WORKER_VERSION": "1.2.3",
            **(extra_env or {}),
        }
        with patch.dict(environ, required_env, clear=False):
            for name in unset:
                environ.pop(name, None)
            m = import_module("simulator_worker.prefect_deploy_flow")
            m = reload(m)

        return m.job_variables

    def test_job_variables_auto_remove_is_set(self) -> None:
        """auto_remove should be True, not left over missing from testing."""
        self.assertTrue(self._get_job_variables()["auto_remove"])

    def test_job_variables_include_all_docker_networks(self) -> None:
        """Attach flow-run containers to every configured Docker network."""
        self.assertEqual(self._get_job_variables()["networks"], ["omotes", "mapeditor-net"])

    def test_local_image_needs_no_version(self) -> None:
        job_variables = self._get_job_variables(
            {"PREFECT_USE_LOCAL_CODE_AND_IMAGE": "true"}, unset=("SIMULATOR_WORKER_VERSION",)
        )
        self.assertIn("env", job_variables)

    def test_published_image_requires_version(self) -> None:
        """Deploying a published image without a version must fail instead of tagging ':None' or ':'."""
        try:
            for unset, extra_env in (
                (("SIMULATOR_WORKER_VERSION",), {}),
                ((), {"SIMULATOR_WORKER_VERSION": "  "}),
            ):
                with (
                    self.subTest(unset=unset, extra_env=extra_env),
                    self.assertRaisesRegex(RuntimeError, "SIMULATOR_WORKER_VERSION"),
                ):
                    self._get_job_variables(extra_env, unset=unset)
        finally:
            # A failed reload leaves the module half-initialised; restore it for other tests.
            self._get_job_variables()

    def test_main_deploys_on_limited_work_queue(self) -> None:
        """Limit simulator runs across deployment versions on one work queue."""
        env = {
            "LOG_LEVEL": "INFO",
            "ESDL_OUTPUT_PROFILES_TYPE": "POSTGRESQL",
            "DB_HOSTNAME": "db",
            "DB_PORT": "5432",
            "DB_USERNAME": "user",
            "DB_PASSWORD": "pass",
            "PG_DB_TIMESERIES": "timeseries",
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

    def test_local_image_build_uses_repo_root_as_context(self) -> None:
        """Build the local image from the repository root, whatever the caller's working directory."""
        env = {
            "LOG_LEVEL": "INFO",
            "ESDL_OUTPUT_PROFILES_TYPE": "POSTGRESQL",
            "DB_HOSTNAME": "db",
            "DB_PORT": "5432",
            "DB_USERNAME": "user",
            "DB_PASSWORD": "pass",
            "PG_DB_TIMESERIES": "timeseries",
            "PREFECT_API_AUTH_STRING": "token",
            "PREFECT_API_URL_FOR_WORKER": "http://prefect:4200/api",
            "MINIO_HOST": "minio",
            "MINIO_EXTERNAL_URL": "http://localhost:9000",
            "MINIO_PORT": "9000",
            "MINIO_ACCESS_KEY": "access",
            "MINIO_SECRET": "secret",
            "PREFECT_WORK_POOL_NAME": "pool",
            "PREFECT_FLOW_MAX_CONCURRENT_RUNS": "4",
            "PREFECT_USE_LOCAL_CODE_AND_IMAGE": "true",
            "PREFECT_USE_LOCAL_SDK": "false",
            "PREFECT_DOCKER_WORKER_NETWORKS": "omotes",
        }
        expected_repo_root = Path(__file__).resolve().parents[1]
        try:
            with patch.dict(environ, env, clear=False):
                module = reload(import_module("simulator_worker.prefect_deploy_flow"))
                with (
                    patch.object(module.shutil, "which", return_value="docker"),
                    patch.object(module, "_build_docker_image", new=AsyncMock()) as build_mock,
                    patch.object(module, "deploy_flow", new=AsyncMock()),
                ):
                    asyncio.run(module.main())
        finally:
            # The reload above bound module-level state to the local image; restore the default.
            self._get_job_variables()

        assert build_mock.await_args is not None
        command = build_mock.await_args.args[0]
        self.assertEqual(command[-1], ".")
        self.assertEqual(build_mock.await_args.kwargs["cwd"], expected_repo_root)
        self.assertTrue((expected_repo_root / "Dockerfile").is_file())
