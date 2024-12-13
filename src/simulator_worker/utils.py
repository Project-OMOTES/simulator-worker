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
from typing import Dict, List, Tuple, Type, TypeVar, cast

import esdl
import pandas as pd
from esdl.profiles.influxdbprofilemanager import (
    ConnectionSettings,
    InfluxDBProfileManager,
)
from esdl.profiles.profilemanager import ProfileManager
from omotes_simulator_core.infrastructure.utils import pyesdl_from_string

logger = logging.getLogger("simulator_worker")

T = TypeVar("T")


def id_to_esdl_item(id: str, energy_system: esdl.EnergySystem, item_type: Type[T]) -> T:
    """Finds the esdl item for a given ID. This method currently only supports Assets and Ports.

    :param id: The ID of the asset to find.
    :param energy_system: The energy system to search in.
    :return: The esdl item with the given ID.
    :raises ValueError: If the asset with the given ID is not found.
    """
    item = next((x for x in energy_system.eAllContents() if hasattr(x, "id") and x.id == id), None)
    if item is None:
        raise ValueError(f"{id} does not exist in this energy system")
    if not isinstance(item, item_type):
        raise ValueError("Not an Asset or Port")
    return item


def find_asset_from_port(id: str, energy_system: esdl.EnergySystem) -> esdl.Asset:
    """Finds the esdl asset for a given port id.

    :param id: The ID of the asset to find.
    :param energy_system: The energy system to search in.
    :return: The asset ID that owns the given port.
    :raises ValueError: If the asset with the given ID is not found.
    """
    for asset in energy_system.eAllContents():
        if not isinstance(asset, esdl.Asset):
            continue
        for port in asset.port:
            if port.id == id:
                return asset
    raise ValueError(f"port {id} does not exist in this energy system")


def add_datetime_index(
    df: pd.DataFrame, starttime: datetime, endtime: datetime, timestep: int
) -> pd.DataFrame:
    """Create new datetime column in df based on start and end time range.

    :param df: The dataframe to add the datetime index to.
    :param starttime: The start time of the datetime index.
    :param endtime: The end time of the datetime index.
    :param timestep: The timestep of the datetime index in seconds.
    :return: The dataframe with the datetime index added.
    """
    df["datetime"] = pd.date_range(
        start=starttime, end=endtime, freq=f"{timestep}s", inclusive="left"
    )
    df.set_index("datetime", inplace=True)
    return df


def get_profileQuantityAndUnit(property_name: str) -> esdl.esdl.QuantityAndUnitType:
    """Get the profile quantity and unit.

    :param property_name: The name of the property to get the quantity and unit for.
    :return: The quantity and unit for the given property name.
    """
    if property_name.startswith("mass_flow"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.FLOW,
            unit=esdl.UnitEnum.GRAM,
            perTimeUnit=esdl.TimeUnitEnum.SECOND,
            multiplier=esdl.MultiplierEnum.KILO,
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
            unit=esdl.UnitEnum.KELVIN,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("volume_flow"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.FLOW,
            unit=esdl.UnitEnum.CUBIC_METRE,
            perTimeUnit=esdl.TimeUnitEnum.SECOND,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("pressure_loss_per_length"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.PRESSURE,
            perMultiplier=esdl.MultiplierEnum.METRE,
            unit=esdl.UnitEnum.PASCAL,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("pressure_loss"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.PRESSURE,
            unit=esdl.UnitEnum.PASCAL,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("heat_loss"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.HEAT_FLOW,
            unit=esdl.UnitEnum.WATT,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("heat_supplied"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.HEAT_FLOW,
            unit=esdl.UnitEnum.WATT,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("heat_demand"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.HEAT_FLOW,
            unit=esdl.UnitEnum.WATT,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("heat_supply_set_point"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.HEAT_FLOW,
            unit=esdl.UnitEnum.WATT,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    elif property_name.startswith("heat_demand_set_point"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=esdl.PhysicalQuantityEnum.HEAT_FLOW,
            unit=esdl.UnitEnum.WATT,
            multiplier=esdl.MultiplierEnum.NONE,
        )
    else:
        raise ValueError(f"Unknown property name: {property_name}")


def create_output_esdl(input_esdl: str, simulation_result: pd.DataFrame) -> str:
    """Prepare output esdl for simulator-worker.

    Takes an input ESDL string and a dataframe. Generates an updated ESDL
    file with references to the time series stored in the database

    :param input_esdl: The input ESDL file as a string.
    :param simulation_result: The simulation result as a DataFrame.
    :return: The output ESDL file as a string.
    """
    esh = pyesdl_from_string(input_esdl)
    input_uuid = str(esh.energy_system.id)  # store input_esdl UUID
    esh.energy_system.id = str(uuid.uuid4())
    output_uuid = esh.energy_system.id
    logger.info("Input ESDL UUID: %s", input_uuid)
    logger.info("Output ESDL UUID: %s", output_uuid)
    logger.debug(simulation_result.head())

    influxdb_host = os.getenv("INFLUXDB_HOSTNAME", "localhost")
    influxdb_port = os.getenv("INFLUXDB_PORT", "8086")
    influxdb_username = os.getenv("INFLUXDB_USERNAME", "testuser")
    influxdb_password = os.getenv("INFLUXDB_PASSWORD", "")
    logger.debug(
        "Connecting to InfluxDB: %s@%s:%s", influxdb_username, influxdb_host, influxdb_port
    )
    influxdb_conn_settings = ConnectionSettings(
        host=influxdb_host,
        port=int(influxdb_port),
        username=influxdb_username,
        password=influxdb_password,
        database=output_uuid,
        ssl=False,
        verify_ssl=False,
    )

    series_per_asset_id_per_carrier_id: Dict[
        str, Dict[str, List[Tuple[Tuple[str, str], esdl.Port]]]
    ] = {}

    series_name: Tuple[str, str]
    for series_name_uncasted, _ in simulation_result.items():
        series_name = cast(Tuple[str, str], series_name_uncasted)
        port_id = series_name[0]
        port: esdl.Port = id_to_esdl_item(port_id, esh.energy_system, esdl.Port)
        carrier: esdl.Carrier = port.carrier
        profile_name = series_name[1]
        logger.debug("Output series: %s", series_name)
        asset = find_asset_from_port(port_id, esh.energy_system)
        asset_id = asset.id
        logger.debug("%s:\t\t %s", series_name, asset.port)

        series_per_asset_id_for_carrier = series_per_asset_id_per_carrier_id.setdefault(
            carrier.id, {}
        )
        series_for_asset_id_for_carrier = series_per_asset_id_for_carrier.setdefault(asset_id, [])
        series_for_asset_id_for_carrier.append((series_name, port))

    capabilities = [esdl.Transport, esdl.Conversion, esdl.Consumer, esdl.Producer]
    for carrier_id in series_per_asset_id_per_carrier_id:
        for asset_id in series_per_asset_id_per_carrier_id[carrier_id]:
            asset = id_to_esdl_item(asset_id, esh.energy_system, esdl.Asset)
            maybe_asset_capability = next(
                (c for c in capabilities if c in asset.__class__.__mro__), None
            )
            asset_capability = maybe_asset_capability.__name__ if maybe_asset_capability else "None"
            profiles = ProfileManager()
            profiles.profile_type = "DATETIME_LIST"
            profiles.profile_header = ["datetime"]

            for series_name, port in series_per_asset_id_per_carrier_id[carrier_id][asset_id]:
                # Add profile to esdl
                profile_name = series_name[1]

                profiles.profile_header.append(profile_name)
                profile_attributes = esdl.InfluxDBProfile(
                    database=output_uuid,
                    measurement=carrier_id,
                    field=profile_name,
                    port=int(influxdb_port),
                    host=influxdb_host,
                    startDate=simulation_result.index[0],
                    endDate=simulation_result.index[-1],
                    id=str(uuid.uuid4()),
                )

                profile_attributes.profileQuantityAndUnit = get_profileQuantityAndUnit(profile_name)
                port.profile.append(profile_attributes)

            for index, row in simulation_result.loc[
                :,
                [
                    series_name
                    for series_name, _ in series_per_asset_id_per_carrier_id[carrier_id][asset_id]
                ],
            ].iterrows():
                profiles.profile_data_list.append([index, *row.values.tolist()])
            profiles.num_profile_items = len(profiles.profile_data_list)
            profiles.start_datetime = simulation_result.index[0]
            profiles.end_datetime = simulation_result.index[-1]

            influxdb_profile_manager = InfluxDBProfileManager(influxdb_conn_settings, profiles)
            influxdb_profile_manager.save_influxdb(
                measurement=carrier_id,
                field_names=influxdb_profile_manager.profile_header[1:],
                tags={
                    "assetClass": asset.__class__.__name__,
                    "assetId": asset_id,
                    "assetName": asset.name,
                    "capability": asset_capability,
                    "simulationRun": output_uuid,
                    "simulation_type": "omotes-simulator",
                },
            )
    output_esdl = cast(str, esh.to_string())
    return output_esdl


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    with open(r"./testdata/test1.esdl", "r") as f:
        input_esdl = f.read()

    df = pd.read_pickle(r"./testdata/test1.pkl")
    result_indexed = add_datetime_index(
        df,
        datetime.strptime("2019-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        datetime.strptime("2019-01-01T10:00:00", "%Y-%m-%dT%H:%M:%S"),
        3600,
    )
    print(f"{df.head()}\nshape={result_indexed.shape}")
    output_esdl = create_output_esdl(input_esdl=input_esdl, simulation_result=result_indexed)
    with open("./testdata/test1_output.esdl", "w") as output_esdl_file:
        output_esdl_file.write(output_esdl)
