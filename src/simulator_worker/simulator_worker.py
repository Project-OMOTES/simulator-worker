#  Copyright (c) 2023. Deltares
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Main python file for Simulator-worker."""
import logging
import math
import traceback
from datetime import datetime, timedelta
from uuid import uuid4

import dotenv
from omotes_sdk.internal.orchestrator_worker_events.esdl_messages import EsdlMessage
from omotes_sdk.internal.worker.worker import UpdateProgressHandler, initialize_worker
from omotes_sdk.types import ProtobufDict
from omotes_sdk.workflow_type import (
    DateTimeParameter,
    DurationParameter,
    parse_workflow_config_parameter,
)
from omotes_simulator_core.entities.esdl_object import EsdlObject
from omotes_simulator_core.entities.simulation_configuration import (
    SimulationConfiguration,
)
from omotes_simulator_core.infrastructure.simulation_manager import SimulationManager
from omotes_simulator_core.infrastructure.utils import pyesdl_from_string

from simulator_worker.utils import add_datetime_index, create_output_esdl

dotenv.load_dotenv()

logger = logging.getLogger("simulator_worker")


def simulator_worker_task(
    input_esdl: str, workflow_config: ProtobufDict, update_progress_handler: UpdateProgressHandler
) -> tuple[str | None, list[EsdlMessage]]:
    """Simulator worker function for celery task.

    Note: Be careful! This spawns within a subprocess and gains a copy of memory from parent
    process. You cannot open sockets and other resources in the main process and expect
    it to be copied to subprocess. Any resources e.g. connections/sockets need to be opened
    in this task by the subprocess.

    Expected contents of workflow_config:
    - start_time_unix_s: int (float with .0), seconds since epoch
    - end_time_unix_s: int (float with .0), seconds since epoch
    - timestep_s: int (float with .0) seconds

    :param input_esdl: The input ESDL XML string.
    :param workflow_config: Extra parameters to configure this run.
    :param update_progress_handler: Handler to notify of any progress changes.
    :return: Simulated ESDL with simulation result profiles added to input ESDL but no other
        changes.
    """
    logger.info("Starting Simulator-core...")

    # TODO
    # pass update_progress_handler(fraction: float, msg: str) to simulator-core

    timestep: timedelta = parse_workflow_config_parameter(
        workflow_config, "timestep", DurationParameter, timedelta(hours=1)
    )
    start: datetime = parse_workflow_config_parameter(
        workflow_config,
        "start_time",
        DateTimeParameter,
        datetime.fromisoformat("2019-01-01T00:00:00+00:00"),
    )
    end: datetime = parse_workflow_config_parameter(
        workflow_config,
        "end_time",
        DateTimeParameter,
        datetime.fromisoformat("2019-01-01T01:00:00+00:00"),
    )

    simulation_id = uuid4()
    config = SimulationConfiguration(
        simulation_id=simulation_id,
        name="test run",
        timestep=math.floor(timestep.total_seconds()),
        start=start,
        stop=end,
    )
    app = SimulationManager(EsdlObject(pyesdl_from_string(input_esdl)), config)
    result = app.execute(update_progress_handler)

    if len(result.index) == 0:
        logger.error("No simulation results found")
        raise ValueError("No simulation results returned from simulator-core.")

    result_indexed = add_datetime_index(result, config.start, config.stop, config.timestep)
    logger.info(
        "Simulation result: %s rows, %s columns (shape=%s)",
        len(result_indexed.index),
        len(result_indexed.columns),
        result_indexed.shape,
    )
    output_esdl = create_output_esdl(input_esdl, result_indexed)

    # Write output_esdl to file for debugging
    # with open(f"result_{simulation_id}.esdl", "w") as file:
    #     file.writelines(output_esdl)
    return output_esdl, []


def start_app() -> None:
    """Design Toolkit Application application."""
    try:
        initialize_worker("simulator", simulator_worker_task)
    except Exception as error:
        logger.error("Error occured: %s at: %s", error, traceback.format_exc(limit=-1))
        logger.debug(traceback.format_exc())
        raise error


if __name__ == "__main__":
    start_app()
