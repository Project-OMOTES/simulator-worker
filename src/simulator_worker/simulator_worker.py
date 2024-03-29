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
import os
import traceback
import uuid
from datetime import datetime

# from pathlib import Path
from typing import Dict
from uuid import uuid4

# from simulator_worker.app_logging import LogLevel, setup_logging
import dotenv

# from app_logging import LogLevel, setup_logging
# from celery.signals import after_setup_logger  # type: ignore
from omotes_sdk.internal.worker.worker import (  # type: ignore
    UpdateProgressHandler,
    initialize_worker,
)
from simulator_core.entities.esdl_object import EsdlObject
from simulator_core.entities.simulation_configuration import SimulationConfiguration
from simulator_core.infrastructure.simulation_manager import SimulationManager
from simulator_core.infrastructure.utils import pyesdl_from_string

from simulator_worker.utils import add_datetime_index, create_output_esdl

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

# logger = logging.getLogger("simulator_worker")


def simulator_worker_task(
    input_esdl: str, workflow_config: Dict[str, str], update_progress_handler: UpdateProgressHandler
) -> str:
    """Simulator worker function for celery task.

    Note: Be careful! This spawns within a subprocess and gains a copy of memory from parent
    process. You cannot open sockets and other resources in the main process and expect
    it to be copied to subprocess. Any resources e.g. connections/sockets need to be opened
    in this task by the subprocess.

    :param input_esdl:
    :param workflow_config:
    :param update_progress_handler:
    :return: Simulated ESDL (no changes from input)
    """

    logger.info("Starting Simulator-core...")

    # TODO
    # pass update_progress_handler(fraction: float, msg: str) to simulator-core

    config = SimulationConfiguration(
        simulation_id=uuid4(),
        name="test run",
        timestep=3600,
        start=datetime.strptime("2019-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        stop=datetime.strptime("2019-01-01T01:00:00", "%Y-%m-%dT%H:%M:%S"),
    )
    app = SimulationManager(EsdlObject(pyesdl_from_string(input_esdl)), config)
    result = app.execute()

    if len(result.index) == 0:
        logger.error("No simulation results found")
        raise ValueError("No simulation results returned from simulator-core.")

    result_indexed = add_datetime_index(result, config.start, config.stop, config.timestep)
    logger.info(
        f"Simulation result: {len(result_indexed.index)} rows, "
        "{len(result_indexed.columns)} columns "
        "(shape={result_indexed.shape})"
    )
    output_esdl = create_output_esdl(input_esdl, result_indexed)
    return output_esdl


# @after_setup_logger.connect
# def setup_loggers(
#     logger: logging.Logger, loglevel: int, colorize: bool, format: str, **kwargs: str
# ) -> None:
#     """Event handler to setup logging."""
#     setup_logging(
#         log_level=LogLevel(loglevel),
#         colors=colorize,
#         format_string=format,
#     )
#     pass


# @worker_shutting_down.connect
# def shutdown(*args, **kwargs):
#     print(args, kwargs)
#     broker_if.stop()


def start_app(loglevel: str = "DEBUG", colors: bool = False) -> None:
    """Design Toolkit Application application."""
    # setup_logging(LogLevel.parse(loglevel), colors)
    try:
        initialize_worker("simulator", simulator_worker_task)
    except Exception as error:
        logger.error(f"Error occured: {error} at: {traceback.format_exc(limit=-1)}")
        logger.debug(traceback.format_exc())
        raise error


if __name__ == "__main__":
    start_app(loglevel="DEBUG", colors=True)
