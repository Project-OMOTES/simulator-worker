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
import traceback
from datetime import datetime, timedelta

from simulator_worker.app_logging import LogLevel, setup_logging

logger = logging.getLogger(__name__)


def testable_function(input: datetime) -> datetime:
    """Testable function."""
    return input + +timedelta(hours=1)


def start_app(loglevel: str, colors: bool) -> None:
    """Design Toolkit Application application."""
    setup_logging(LogLevel.parse(loglevel), colors)
    try:

        logger.info(f"The time + 1 hour is: {testable_function(datetime.now())}")

        # TODO insert your code here

    except Exception as error:
        logger.error(f"Error occured: {error} at: {traceback.format_exc(limit=-1)}")
        logger.debug(traceback.format_exc())


if __name__ == "__main__":
    start_app(loglevel="DEBUG", colors=True)
