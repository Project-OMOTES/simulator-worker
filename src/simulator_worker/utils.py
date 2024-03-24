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
"""utility functions for simulator-worker."""
import os

import esdl
import pandas as pd
from esdl.profiles.influxdbprofilemanager import (
    ConnectionSettings,
    InfluxDBProfileManager,
)
from esdl.profiles.profilemanager import ProfileManager
from simulator_core.infrastructure.utils import pyesdl_from_string


def create_output_esdl(input_esdl: str, simulation_result: pd.DataFrame) -> None:
    """Prepare output esdl for simulator-worker.

    Takes an input ESDL string and a dataframe. Generates an updated ESDL
    file with references to the time series stored in the database
    """
    pass
    # esh = pyesdl_from_string(input_esdl)
    # influxdb_host = os.environ.get("INFLUXDB_HOSTNAME")
    # influxdb_port = os.environ.get("INFLUXDB_PORT")
    # influxdb_username = os.environ.get("INFLUXDB_USERNAME")
    # influxdb_password = os.environ.get("INFLUXDB_PASSWORD")
    # for series_name, series in simulation_result.items():
