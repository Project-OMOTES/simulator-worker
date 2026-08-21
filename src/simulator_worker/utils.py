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
from pathlib import Path
from typing import Any, TypeVar, cast

import esdl
import omotes_simulator_core
import pandas as pd
from esdl.profiles.influxdbprofilemanager import (
    ConnectionSettings,
    InfluxDBProfileManager,
)
from esdl.profiles.profilemanager import ProfileManager
from omotes_simulator_core.infrastructure.utils import pyesdl_from_string
from prefect.runtime import flow_run

T = TypeVar("T")


def id_to_esdl_item(id: str, energy_system: esdl.EnergySystem, item_type: type[T]) -> T:
    """Finds the esdl item for a given ID. This method currently only supports Assets and Ports.

    Args:
        id: The ID of the asset to find.
        energy_system: The energy system to search in.
        item_type: The expected item type.

    Returns:
        The ESDL item with the given ID and expected type.

    Raises:
        ValueError: If the item does not exist or has an unexpected type.
    """
    item = next((x for x in energy_system.eAllContents() if hasattr(x, "id") and x.id == id), None)
    if item is None:
        raise ValueError(f"{id} does not exist in this energy system")
    if not isinstance(item, item_type):
        raise ValueError("Not an Asset or Port")
    return item


def find_asset_from_port(id: str, energy_system: esdl.EnergySystem) -> esdl.Asset:
    """Finds the esdl asset for a given port id.

    Args:
        id: The ID of the port to find.
        energy_system: The energy system to search in.

    Returns:
        The asset that owns the given port.

    Raises:
        ValueError: If no asset contains the given port ID.
    """
    for asset in energy_system.eAllContents():
        if not isinstance(asset, esdl.Asset):
            continue
        for port in asset.port:
            if port.id == id:
                return asset
    raise ValueError(f"port {id} does not exist in this energy system")


def add_datetime_index(df: pd.DataFrame, starttime: datetime, endtime: datetime, timestep: int) -> pd.DataFrame:
    """Create new datetime column in df based on start and end time range.

    Args:
        df: The dataframe to add the datetime index to.
        starttime: The start time of the datetime index.
        endtime: The end time of the datetime index.
        timestep: The timestep of the datetime index in seconds.

    Returns:
        The dataframe with a datetime index.
    """
    df["datetime"] = pd.date_range(start=starttime, end=endtime, freq=f"{timestep}s", inclusive="left")
    df.set_index("datetime", inplace=True)
    return df


def get_profileQuantityAndUnit(property_name: str) -> esdl.esdl.QuantityAndUnitType | None:
    """Get the profile quantity and unit.

    Args:
        property_name: The name of the property to map.

    Returns:
        The quantity and unit for the given property name, or None if unknown.
    """
    physical_quantity_enum = cast(Any, esdl.PhysicalQuantityEnum)
    unit_enum = cast(Any, esdl.UnitEnum)
    time_unit_enum = cast(Any, esdl.TimeUnitEnum)
    multiplier_enum = cast(Any, esdl.MultiplierEnum)

    if property_name.startswith("mass_flow"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.FLOW,
            unit=unit_enum.GRAM,
            perTimeUnit=time_unit_enum.SECOND,
            multiplier=multiplier_enum.KILO,
        )
    elif property_name.startswith("pressure"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.PRESSURE,
            unit=unit_enum.PASCAL,
            multiplier=multiplier_enum.NONE,
        )
    elif property_name.startswith("temperature"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.TEMPERATURE,
            unit=unit_enum.KELVIN,
            multiplier=multiplier_enum.NONE,
        )
    elif property_name.startswith("volume_flow"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.FLOW,
            unit=unit_enum.CUBIC_METRE,
            perTimeUnit=time_unit_enum.SECOND,
            multiplier=multiplier_enum.NONE,
        )
    elif property_name.startswith("pressure_loss_per_length"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.PRESSURE,
            perMultiplier=multiplier_enum.METRE,
            unit=unit_enum.PASCAL,
            multiplier=multiplier_enum.NONE,
        )
    elif property_name.startswith("pressure_loss"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.PRESSURE,
            unit=unit_enum.PASCAL,
            multiplier=multiplier_enum.NONE,
        )
    elif (
        property_name.startswith("heat_loss")
        or property_name.startswith("heat_supplied")
        or property_name.startswith("heat_demand")
        or property_name.startswith("heat_supply_set_point")
        or property_name.startswith("heat_demand_set_point")
    ):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.POWER,
            unit=unit_enum.WATT,
            multiplier=multiplier_enum.NONE,
        )
    elif property_name.startswith("velocity"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.SPEED,
            unit=unit_enum.METRE,
            perTimeUnit=time_unit_enum.SECOND,
            multiplier=multiplier_enum.NONE,
        )
    elif property_name.startswith("charge rate") or property_name.startswith("discharge rate"):
        return esdl.esdl.QuantityAndUnitType(
            physicalQuantity=physical_quantity_enum.FLOW,
            unit=unit_enum.GRAM,
            perTimeUnit=time_unit_enum.SECOND,
            multiplier=multiplier_enum.KILO,
        )
    else:
        logging.info(f"Unknown property name: {property_name}")
        return None


def create_output_esdl(input_esdl: str, simulation_result: pd.DataFrame) -> str:
    """Prepare output esdl for simulator-worker.

    Takes an input ESDL string and a dataframe. Generates an updated ESDL
    file with references to the time series stored in the database

    Args:
        input_esdl: The input ESDL file as a string.
        simulation_result: The simulation result as a DataFrame.

    Returns:
        The output ESDL file as a string.
    """
    esh = pyesdl_from_string(input_esdl)
    input_esdl_uuid = str(esh.energy_system.id)  # store input_esdl UUID
    esh.energy_system.id = str(uuid.uuid4())
    output_uuid = esh.energy_system.id

    input_esdl_name = str(esh.energy_system.name)  # store input_esdl name
    output_esdl_name = input_esdl_name + "_"
    output_esdl_name += flow_run.name if flow_run and flow_run.name else "simulated"
    esh.energy_system.name = output_esdl_name

    logging.info("Input ESDL UUID: %s, name: %s", input_esdl_uuid, input_esdl_name)
    logging.info("Output ESDL UUID: %s, name: %s", output_uuid, output_esdl_name)
    logging.debug(simulation_result.head())

    influxdb_host = os.getenv("INFLUXDB_HOSTNAME", "localhost")
    influxdb_port = os.getenv("INFLUXDB_PORT", "8086")
    influxdb_username = os.getenv("INFLUXDB_USERNAME", "testuser")
    influxdb_password = os.getenv("INFLUXDB_PASSWORD", "")
    logging.debug("Connecting to InfluxDB: %s@%s:%s", influxdb_username, influxdb_host, influxdb_port)
    influxdb_conn_settings = ConnectionSettings(
        host=influxdb_host,
        port=int(influxdb_port),
        username=influxdb_username,
        password=influxdb_password,
        database=output_uuid,
        ssl=False,
        verify_ssl=False,
    )

    series_per_asset_id_per_carrier_id: dict[str, dict[str, list[tuple[tuple[str, str], esdl.Port]]]] = {}

    series_name: tuple[str, str]
    for series_name_uncasted, _ in simulation_result.items():
        series_name = cast(tuple[str, str], series_name_uncasted)
        port_id = series_name[0]
        port: esdl.Port = id_to_esdl_item(port_id, esh.energy_system, esdl.Port)
        carrier: esdl.Carrier = port.carrier
        profile_name = series_name[1]
        logging.debug("Output series: %s", series_name)
        asset = find_asset_from_port(port_id, esh.energy_system)
        asset_id = asset.id
        logging.debug("%s:\t\t %s", series_name, cast(Any, asset).port)

        series_per_asset_id_for_carrier = series_per_asset_id_per_carrier_id.setdefault(carrier.id, {})
        series_for_asset_id_for_carrier = series_per_asset_id_for_carrier.setdefault(asset_id, [])
        series_for_asset_id_for_carrier.append((series_name, port))

    datasource = esdl.esdl.DataSource(
        name="Omotes simulator core run",
        id=str(uuid.uuid4()),
        description="This profile is a simulation results obtained with the Omotes simulator core",
        reference="https://simulator-core.readthedocs.io/en/latest/",
        releaseDate=datetime.now(),
        version=omotes_simulator_core.__version__,
        license="GNU GENERAL PUBLIC LICENSE",
        author="Deltares/TNO",
        contactDetails="https://github.com/Project-OMOTES",
    )
    esh.energy_system.energySystemInformation.dataSources = esdl.DataSources(
        id=str(uuid.uuid4()), dataSource=[datasource]
    )

    capabilities = [esdl.Transport, esdl.Conversion, esdl.Consumer, esdl.Producer]
    for carrier_id in series_per_asset_id_per_carrier_id:
        for asset_id in series_per_asset_id_per_carrier_id[carrier_id]:
            asset = id_to_esdl_item(asset_id, esh.energy_system, esdl.Asset)
            maybe_asset_capability = next((c for c in capabilities if c in asset.__class__.__mro__), None)
            asset_capability = maybe_asset_capability.__name__ if maybe_asset_capability else "None"
            profiles = ProfileManager()
            profiles.profile_type = "DATETIME_LIST"
            profiles.profile_header = ["datetime"]

            for series_name, port in series_per_asset_id_per_carrier_id[carrier_id][asset_id]:
                # Add profile to esdl
                profile_name = series_name[1]
                reference = esdl.esdl.DataSourceReference(reference=datasource)
                profiles.profile_header.append(profile_name)
                profile_type_enum = cast(Any, esdl.ProfileTypeEnum)
                profile_attributes = esdl.InfluxDBProfile(
                    database=output_uuid,
                    measurement=carrier_id,
                    field=profile_name,
                    port=int(influxdb_port),
                    host=influxdb_host,
                    startDate=simulation_result.index[0],
                    endDate=simulation_result.index[-1],
                    id=str(uuid.uuid4()),
                    filters=f"\"assetId\"='{asset_id}'",
                    profileType=profile_type_enum.OUTPUT,
                    dataSource=reference,
                )

                if (quantity_and_unit := get_profileQuantityAndUnit(profile_name)) is not None:
                    profile_attributes.profileQuantityAndUnit = quantity_and_unit
                port.profile.append(profile_attributes)

            for index, row in simulation_result.loc[
                :,
                [series_name for series_name, _ in series_per_asset_id_per_carrier_id[carrier_id][asset_id]],
            ].iterrows():
                profiles.profile_data_list.append([index, *row.values.tolist()])
            profiles.num_profile_items = len(profiles.profile_data_list)
            profiles.start_datetime = simulation_result.index[0]
            profiles.end_datetime = simulation_result.index[-1]

            influxdb_profile_manager = InfluxDBProfileManager(influxdb_conn_settings, profiles)
            field_names = (influxdb_profile_manager.profile_header or [])[1:]
            influxdb_profile_manager.save_influxdb(
                measurement=carrier_id,
                field_names=field_names,
                tags={
                    "assetClass": asset.__class__.__name__,
                    "assetId": asset_id,
                    "assetName": asset.name,
                    "capability": asset_capability,
                    "simulationRun": output_uuid,
                    "simulation_type": "omotes-simulator",
                },
            )
    output_esdl = esh.to_string()
    return output_esdl


def _parse_bool_config(config: dict, key: str, default: bool) -> bool:
    """Read a bool parameter from workflow config, with Protobuf-safe string handling.

    Returns:
        The parsed boolean value.
    """
    value = config.get(key, default)
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


def _parse_float_config(config: dict, key: str, default: float, warn_msg: str | None = None) -> float:
    """Read a float parameter from workflow config, falling back to default if absent.

    Returns:
        The parsed float value.
    """
    if key not in config:
        if warn_msg:
            logging.warning(warn_msg)
        return default
    value = config[key]
    try:
        return float(value) if isinstance(value, (int, float, str)) else default
    except (ValueError, TypeError):
        return default


def _parse_datetime_config(config: dict, key: str, default: datetime, warn_msg: str | None = None) -> datetime:
    """Read an ISO-format datetime parameter from workflow config, falling back to default if absent/invalid.

    Returns:
        The parsed datetime value.
    """
    if key not in config:
        if warn_msg:
            logging.warning(warn_msg)
        return default

    value = config[key]
    if not isinstance(value, str):
        return default

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return default


def save_debug_esdl(
    simulation_id: uuid.UUID | str, input_esdl: str, output_esdl: str, base_dir: str | Path = "."
) -> Path:
    """Save input and output ESDL files to a debug directory.

    The directory name is `debug_esdl_{simulation_id}` under `base_dir`.
    Raises on I/O failure — callers are responsible for exception handling.

    Returns:
        The path to the directory containing the debug ESDL files.
    """
    debug_dir = Path(base_dir) / f"debug_esdl_{simulation_id}"
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "input.esdl").write_text(input_esdl, encoding="utf-8")
    (debug_dir / "output.esdl").write_text(output_esdl, encoding="utf-8")
    logging.info("Wrote debug ESDL files to %s", debug_dir)
    return debug_dir


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    with open(r"./testdata/test1.esdl") as f:
        input_esdl = f.read()

    df = cast(pd.DataFrame, pd.read_pickle(r"./testdata/test1.pkl"))  # noqa: S301
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
