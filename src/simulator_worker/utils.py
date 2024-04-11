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
import logging
import os
import uuid
from datetime import datetime
from typing import cast

import esdl
import pandas as pd
from esdl.profiles.influxdbprofilemanager import (
    ConnectionSettings,
    InfluxDBProfileManager,
)
from esdl.profiles.profilemanager import ProfileManager
from simulator_core.infrastructure.utils import pyesdl_from_string

logger = logging.getLogger(__name__)


def _id_to_asset(id: str, energy_system: esdl.EnergySystem) -> esdl.Asset:
    return cast(esdl.Asset,
                next((x for x in energy_system.eAllContents() if hasattr(x, "id") and x.id == id)))


def add_datetime_index(
        df: pd.DataFrame, starttime: datetime, endtime: datetime, timestep: int
) -> pd.DataFrame:
    """Create new datetime column in df based on start and end time range."""
    df["datetime"] = pd.date_range(
        start=starttime, end=endtime, freq=f"{timestep}S", inclusive="left"
    )
    df.set_index("datetime", inplace=True)
    return df


def get_profileQuantityAndUnit(property_name: str) -> esdl.esdl.QuantityAndUnitType:
    """Get the profile quantity and unit."""
    if property_name.startswith("mass_flow"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.FLOW,
            unit=esdl.UnitEnum.CUBIC_METRE,
            perTimeUnit=esdl.TimeUnitEnum.SECOND,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("pressure"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.PRESSURE,
            unit=esdl.UnitEnum.PASCAL,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("temperature"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.TEMPERATURE,
            unit=esdl.UnitEnum.DEGREES_CELSIUS,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    else:
        raise ValueError(f"Unknown property name: {property_name}")


def create_output_esdl(
        input_esdl: str,
        simulation_result: pd.DataFrame,
) -> str:
    """Prepare output esdl for simulator-worker.

    Takes an input ESDL string and a dataframe. Generates an updated ESDL
    file with references to the time series stored in the database
    """
    esh = pyesdl_from_string(input_esdl)
    input_uuid = str(esh.energy_system.id)  # store input_esdl UUID
    esh.energy_system.id = str(uuid.uuid4())
    logger.info(f"Input ESDL UUID: {input_uuid}")
    logger.info(f"Output ESDL UUID: {esh.energy_system.id}")
    logger.debug(simulation_result.head())

    influxdb_host = os.getenv("INFLUXDB_HOSTNAME", "localhost")
    influxdb_port = os.getenv("INFLUXDB_PORT", "8086")
    influxdb_username = os.getenv("INFLUXDB_USERNAME", "testuser")
    influxdb_password = os.getenv("INFLUXDB_PASSWORD", "")
    logger.debug(f"Connecting to InfluxDB: {influxdb_username}@{influxdb_host}:{influxdb_port}")
    influxdb_conn_settings = ConnectionSettings(
        host=influxdb_host,
        port=int(influxdb_port),
        username=influxdb_username,
        password=influxdb_password,
        database=input_uuid,
        ssl=False,
        verify_ssl=False,
    )
    profiles = ProfileManager()
    profiles.profile_type = "DATETIME_LIST"
    profiles.profile_header = ["datetime"]
    for series_name, _ in simulation_result.items():
        logger.debug(f"Output series: {series_name}")
        # print(f"{series_name}:\t\t {asset.port}")
        # print(f"Inport index={get_port_index(asset, esdl.InPort)}")
        profiles.profile_header.append(series_name[1])  # type: ignore[index]
        profile_attributes = esdl.InfluxDBProfile(
            database=input_uuid,
            measurement=series_name[0],  # type: ignore[index]
            field=profiles.profile_header[-1],
            port=int(influxdb_port),
            host=influxdb_host,
            startDate=simulation_result.index[0],
            endDate=simulation_result.index[-1],
            id=str(uuid.uuid4()),
        )
        profile_attributes.profileQuantityAndUnit = get_profileQuantityAndUnit(
            series_name[1])  # type: ignore[index]
    for index, row in simulation_result.iterrows():
        profiles.profile_data_list.append([index, *row.values.tolist()])
    profiles.num_profile_items = len(profiles.profile_data_list)
    profiles.start_datetime = simulation_result.index[0]
    profiles.end_datetime = simulation_result.index[-1]

    influxdb_profile_manager = InfluxDBProfileManager(influxdb_conn_settings, profiles)
    influxdb_profile_manager.save_influxdb(
        measurement=input_uuid,
        field_names=influxdb_profile_manager.profile_header[1:],
        tags={
            "output_esdl_id": esh.energy_system.id
        },
    )
    output_esdl = esh.to_string()
    return output_esdl


if __name__ == "__main__":
    with open(r"./testdata/test1.esdl", "r") as f:
        input_esdl = f.read()

    df = pd.read_pickle(r"./testdata/test1.pkl")
    result_indexed = add_datetime_index(
        df,
        datetime.strptime("2019-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        datetime.strptime("2019-01-01T10:00:00", "%Y-%m-%dT%H:%M:%S"),
        3600,
    )
    print(f"shape={result_indexed.shape}")
    output_esdl = create_output_esdl(input_esdl=input_esdl, simulation_result=result_indexed)
    with open("./testdata/test1_output.esdl", "w") as output_esdl_file:
        output_esdl_file.write(output_esdl)
