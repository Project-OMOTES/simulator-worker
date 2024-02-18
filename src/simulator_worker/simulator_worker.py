#  Copyright (c) 2023. {cookiecutter.cookiecutter.maintainer_name}}
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

"""Main python file for Design Toolkit Application."""
import logging
import os
import traceback

# from pathlib import Path
from typing import Dict

from celery.signals import after_setup_logger  # type: ignore
from omotes_sdk.internal.worker.worker import (  # type: ignore
    UpdateProgressHandler,
    initialize_worker,
)

from simulator_worker.app_logging import LogLevel, setup_logging

logger = logging.getLogger(__name__)

logger = logging.getLogger("grow_worker")


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
    :return: GROW optimized or simulated ESDL
    """
    # base_folder = Path(__file__).resolve().parent.parent
    write_result_db_profiles = "INFLUXDB_HOSTNAME" in os.environ
    influxdb_host = os.environ.get("INFLUXDB_HOSTNAME", "localhost")
    influxdb_port = int(os.environ.get("INFLUXDB_PORT", "8086"))

    logger.info(
        f"Will write result profiles to database: {write_result_db_profiles}. "
        f"At {influxdb_host}:{influxdb_port}"
    )

    # TODO
    # add simulator-core
    # pass update_progress_handler(fraction: float, msg: str) to simulator-core
    # catch return from simultor-core and chuck into DB?

    return input_esdl  # simulator always returns the same ESDL as input


@after_setup_logger.connect
def setup_loggers(
    logger: logging.Logger, loglevel: str, colorize: str, format: str, **kwargs: str
) -> None:
    """Event handler to setup logging."""
    setup_logging(
        log_level=LogLevel.parse(loglevel),
        colors=(colorize.lower() in ["yes", "true"]),
        format_string=format,
    )
    pass


# @worker_shutting_down.connect
# def shutdown(*args, **kwargs):
#     print(args, kwargs)
#     broker_if.stop()


def start_app(loglevel: str = "DEBUG", colors: bool = False) -> None:
    """Design Toolkit Application application."""
    setup_logging(LogLevel.parse(loglevel), colors)
    try:
        initialize_worker("simulator", simulator_worker_task)
    except Exception as error:
        logger.error(f"Error occured: {error} at: {traceback.format_exc(limit=-1)}")
        logger.debug(traceback.format_exc())
        raise error


if __name__ == "__main__":
    start_app(loglevel="DEBUG", colors=True)
