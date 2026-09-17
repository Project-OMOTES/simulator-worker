import logging
from contextlib import nullcontext
from typing import Any
from uuid import uuid4

from kpicalculator import (
    DEFAULT_DISCOUNT_RATE_PERCENT,
    DEFAULT_SYSTEM_LIFETIME_YEARS,
    build_esdl_string_with_kpis,
    calculate_kpis_from_simulator,
)
from omotes_sdk.esdl_messages import EsdlMessage, MessageSeverity
from omotes_sdk.log_forwarding import StdCaptureToLogSession
from omotes_sdk.prefect_util import (
    create_flow_progress_updater,
    in_prefect_flow_context,
    write_flow_return_artifact_to_minio,
)
from omotes_simulator_core.entities.esdl_object import EsdlObject
from omotes_simulator_core.entities.simulation_configuration import (
    SimulationConfiguration,
)
from omotes_simulator_core.infrastructure.simulation_manager import SimulationManager
from omotes_simulator_core.infrastructure.utils import pyesdl_from_string
from prefect import flow
from prefect.states import Failed, State
from pydantic import BaseModel, Field

from simulator_worker.env import EnvSettings
from simulator_worker.utils import (
    _parse_bool_config,
    _parse_datetime_config,
    _parse_float_config,
    add_datetime_index,
    create_output_esdl,
    save_debug_esdl,
)


class SimulatorFlowResult(BaseModel):
    """Flow result payload written as artifact output."""

    output_esdl: str | None = Field(default=None, json_schema_extra={"file_extension": ".esdl"})
    esdl_messages: list[dict[str, Any]] = Field(default_factory=list, json_schema_extra={"file_extension": ".json"})


@flow(timeout_seconds=EnvSettings.prefect_flow_timeout_seconds())
def simulator_flow(
    input_esdl: str,
    workflow_config: dict,
    workflow_type_name: str,
) -> SimulatorFlowResult | State[Any] | None:
    """Prefect flow function for the simulator worker.

    Args:
        input_esdl: The input ESDL XML string.
        workflow_config: Extra parameters to configure this run.
        workflow_type_name: Name of the workflow.

    Returns:
        SimulatorFlowResult | State[Any] | None: The flow result on success; a Failed state if execution
        fails for any reason.

    Raises:
        ValueError: Raised internally for invalid input (e.g. missing workflow_config keys, no simulation
        results), but always caught and converted to a Failed state rather than propagated to the caller.

    """
    logging.info("Starting simulator flow with workflow type: %s", workflow_type_name)
    _update_flow_progress = create_flow_progress_updater(
        start_progress_fraction=0.0,
        start_description="Starting simulator flow",
    )

    # Capture and forward solver output only during orchestrated Prefect flow runs.
    capture_session = StdCaptureToLogSession() if in_prefect_flow_context() else nullcontext()
    with capture_session:
        try:
            minio_host = EnvSettings.minio_host()
            minio_external_url = EnvSettings.minio_external_url()
            minio_port = EnvSettings.minio_port()
            minio_access_key = EnvSettings.minio_access_key()
            minio_secret = EnvSettings.minio_secret()
        except Exception as e:
            # No MinIO configuration available: cannot write a failure artifact either.
            logging.exception("MinIO configuration is unavailable")
            return Failed(message=f"Simulator flow failed: {e}")

        esdl_messages: list[EsdlMessage] = []
        try:
            logging.info(f"workflow config: {workflow_config}")
            if "timestep" not in workflow_config:
                raise ValueError("workflow_config missing required key 'timestep'.")
            timestep = workflow_config["timestep"]
            start = _parse_datetime_config(workflow_config, "start_time")
            end = _parse_datetime_config(workflow_config, "end_time")

            simulation_id = uuid4()
            config = SimulationConfiguration(
                simulation_id=simulation_id,
                name="test run",
                timestep=timestep,
                start=start,
                stop=end,
            )
            app = SimulationManager(EsdlObject(pyesdl_from_string(input_esdl)), config)
            result = app.execute(_update_flow_progress)

            if len(result.index) == 0:
                logging.error("No simulation results found")
                raise ValueError("No simulation results returned from simulator-core.")

            result_indexed = add_datetime_index(result, config.start, config.stop, config.timestep)
            logging.info(
                "Simulation result: %s rows, %s columns (shape=%s)",
                len(result_indexed.index),
                len(result_indexed.columns),
                result_indexed.shape,
            )

            # Create output ESDL with simulation results
            output_esdl = create_output_esdl(input_esdl, result_indexed)

            # KPI Calculation
            logging.info("Calculating KPIs from simulation results...")
            try:
                system_lifetime = _parse_float_config(
                    workflow_config,
                    "system_lifetime",
                    DEFAULT_SYSTEM_LIFETIME_YEARS,
                    warn_msg=(
                        f"workflow_config missing 'system_lifetime'; "
                        f"using default {DEFAULT_SYSTEM_LIFETIME_YEARS:.1f} years."
                    ),
                )
                discount_rate = _parse_float_config(
                    workflow_config,
                    "discount_rate",
                    DEFAULT_DISCOUNT_RATE_PERCENT,
                    warn_msg=(
                        f"workflow_config missing 'discount_rate'; using default {DEFAULT_DISCOUNT_RATE_PERCENT:.1f}%."
                    ),
                )
                round_up_replacement = _parse_bool_config(workflow_config, "round_up_replacement", True)

                kpi_results = calculate_kpis_from_simulator(
                    result_indexed,
                    input_esdl,
                    system_lifetime=system_lifetime,
                    discount_rate=discount_rate,
                    round_up_replacement=round_up_replacement,
                )
                logging.info(
                    "KPI calculation completed for %d assets.",
                    len(kpi_results["asset_financials"]),
                )
                output_esdl_with_kpis = build_esdl_string_with_kpis(output_esdl, kpi_results)
            except Exception as kpi_error:
                logging.exception("KPI calculation failed. Results will be returned without KPIs.")
                output_esdl_with_kpis = output_esdl
                esdl_messages.append(
                    EsdlMessage(
                        technical_message=f"KPI calculation failed: {kpi_error}",
                        severity=MessageSeverity.WARNING,
                    )
                )

            # Debug output: save ESDL files if enabled (can be controlled via workflow_config)
            debug_enabled = _parse_bool_config(workflow_config, "debug_esdl", False)
            if debug_enabled:
                debug_base = str(workflow_config.get("debug_esdl_dir", "."))
                try:
                    save_debug_esdl(simulation_id, input_esdl, output_esdl_with_kpis, base_dir=debug_base)
                except Exception:
                    logging.exception("Failed to save debug ESDL files for %s", simulation_id)

            success_result = SimulatorFlowResult(
                output_esdl=output_esdl_with_kpis,
                esdl_messages=[m.model_dump(mode="json") for m in esdl_messages],
            )

            write_flow_return_artifact_to_minio(
                success_result,
                minio_host,
                minio_port,
                minio_access_key,
                minio_secret,
                minio_external_url,
            )

            # return only for local runs and testing, not persisted for containerized runs: artifacts are used
            return success_result
        except Exception as e:
            logging.exception("Exception during simulator flow")
            esdl_messages.append(
                EsdlMessage(
                    technical_message=f"Simulator flow failed: {e}",
                    severity=MessageSeverity.ERROR,
                )
            )

            failed_result = SimulatorFlowResult(
                output_esdl=None,
                esdl_messages=[m.model_dump(mode="json") for m in esdl_messages],
            )
            write_flow_return_artifact_to_minio(
                failed_result,
                minio_host,
                minio_port,
                minio_access_key,
                minio_secret,
                minio_external_url,
            )

            return Failed(message=f"Simulator flow failed: {e}")
