"""Test KPI integration with simulator-worker."""

import datetime
import logging
import shutil
import tempfile
import unittest
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast
from unittest.mock import patch

import pytest
from prefect.states import State

from simulator_worker.prefect_flow import SimulatorFlowResult

if TYPE_CHECKING:
    import esdl

# Check if full simulator worker can be imported
SIMULATOR_AVAILABLE = False
pyesdl_from_string: Any = None
simulator_flow: Any = None
try:
    from omotes_simulator_core.infrastructure.utils import pyesdl_from_string as _pyesdl_from_string

    from simulator_worker.prefect_flow import simulator_flow as _simulator_flow

    pyesdl_from_string = _pyesdl_from_string
    simulator_flow = _simulator_flow
    SIMULATOR_AVAILABLE = True
except ImportError:
    pass

from kpicalculator import DEFAULT_DISCOUNT_RATE_PERCENT, DEFAULT_SYSTEM_LIFETIME_YEARS  # noqa: E402

from simulator_worker.utils import _parse_float_config  # noqa: E402

MINIO_TEST_ENV = {
    "MINIO_HOST": "minio",
    "MINIO_PORT": "9000",
    "MINIO_ACCESS_KEY": "access",
    "MINIO_SECRET": "secret",
}


def _run_simulator(workflow_config: dict) -> SimulatorFlowResult | State[Any] | None:
    test_esdl_path = Path(__file__).parent.parent / "testdata" / "test_ates.esdl"
    with open(test_esdl_path) as f:
        input_esdl = f.read()

    with (
        patch.dict(environ, MINIO_TEST_ENV, clear=False),
        patch("simulator_worker.utils.InfluxDBProfileManager") as profile_manager_cls,
    ):
        profile_manager_cls.return_value.profile_header = ["datetime"]
        profile_manager_cls.return_value.save_influxdb.return_value = None

        return simulator_flow.fn(input_esdl, workflow_config, "simulator")


def _default_config() -> dict:
    start_time = datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.UTC)
    end_time = datetime.datetime(2019, 1, 1, 2, 0, tzinfo=datetime.UTC)
    return {
        "timestep": 3600.0,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "system_lifetime": 30.0,
    }


def _get_energy_system(config: dict) -> "esdl.EnergySystem":
    """Helper: Run simulator and return parsed energy system."""
    if pyesdl_from_string is None:
        raise RuntimeError("pyesdl parser is unavailable")

    result = _run_simulator(config)
    if isinstance(result, SimulatorFlowResult) and isinstance(result.output_esdl, str):
        output_esdl = result.output_esdl
    elif isinstance(result, State):
        raise RuntimeError(f"Simulator flow failed with state: {result}")
    else:
        raise RuntimeError("Simulator flow did not return output ESDL")

    esh = pyesdl_from_string(output_esdl)
    return esh.energy_system


def _get_kpi_by_name(config: dict) -> dict:
    """Helper: Run simulator and return KPIs indexed by name."""
    energy_system = _get_energy_system(config)
    kpi_list = list(energy_system.instance[0].area.KPIs.kpi)
    return {kpi.name: kpi for kpi in kpi_list}


@pytest.mark.skipif(not SIMULATOR_AVAILABLE, reason="omotes_simulator_core not installed")
class TestKPIOutputEsdlStructureAndCostValues(unittest.TestCase):
    """Output ESDL contains a valid area with KPIs attached, and cost values match test_ates.esdl.

    The ATES asset has investmentCosts=2333594.0 EUR and fixedMaintenanceCosts
    that produce OPEX=215138.89 EUR/year. These derive purely from the ESDL cost
    data and are deterministic regardless of simulation time series.
    """

    energy_system: ClassVar["esdl.EnergySystem"]
    kpi_by_name: ClassVar[dict[str, "esdl.KPI"]]

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.energy_system = _get_energy_system(_default_config())
            area = cls.energy_system.instance[0].area
            cls.kpi_by_name = {kpi.name: kpi for kpi in area.KPIs.kpi} if area.KPIs is not None else {}
        except RuntimeError as e:
            raise unittest.SkipTest(f"Simulator infrastructure unavailable: {e}") from e

    def test__output_esdl_has_area_with_kpis_container(self) -> None:
        self.assertIsNotNone(
            self.energy_system.instance[0].area.KPIs,
            "instance[0].area must have a KPIs container",
        )

    def test__kpis_attached_to_main_area(self) -> None:
        main_area = self.energy_system.instance[0].area
        self.assertIsNotNone(main_area.KPIs, "KPIs should be present in the main area")
        kpi_list = list(main_area.KPIs.kpi)
        self.assertGreater(len(kpi_list), 0, "At least one KPI should be calculated")

    def test__all_kpis_have_names(self) -> None:
        kpi_list = list(self.energy_system.instance[0].area.KPIs.kpi)
        self.assertGreater(len(kpi_list), 0, "KPI list must not be empty")
        for kpi in kpi_list:
            self.assertIsInstance(kpi.name, str, f"KPI {kpi} name must be a string")
            self.assertTrue(kpi.name, f"KPI {kpi} must have a non-empty name")

    def test__cost_breakdown_kpi_is_present(self) -> None:
        cost_kpi_present = "High level cost breakdown [EUR]" in self.kpi_by_name
        self.assertTrue(cost_kpi_present, "Cost breakdown KPI missing from output")

    def test__capex_matches_investment_costs(self) -> None:
        self.assertIn(
            "High level cost breakdown [EUR]",
            self.kpi_by_name,
            f"Cost breakdown KPI missing; got {list(self.kpi_by_name)}",
        )
        cost_kpi = self.kpi_by_name["High level cost breakdown [EUR]"]
        cost_items = {item.label: item.value for item in cast(Any, cost_kpi).distribution.stringItem}

        self.assertIn("CAPEX (total)", cost_items, f"CAPEX key missing; got {cost_items}")
        self.assertAlmostEqual(
            cost_items["CAPEX (total)"],
            2_333_594.0,
            places=2,
            msg=f"CAPEX should match investmentCosts in test_ates.esdl; got {cost_items}",
        )

    def test__opex_matches_fixed_maintenance_costs(self) -> None:
        self.assertIn(
            "High level cost breakdown [EUR]",
            self.kpi_by_name,
            f"Cost breakdown KPI missing; got {list(self.kpi_by_name)}",
        )
        cost_kpi = self.kpi_by_name["High level cost breakdown [EUR]"]
        cost_items = {item.label: item.value for item in cast(Any, cost_kpi).distribution.stringItem}

        self.assertIn("OPEX (yearly)", cost_items, f"OPEX key missing; got {cost_items}")
        self.assertAlmostEqual(
            cost_items["OPEX (yearly)"],
            215_138.89,
            places=2,
            msg=f"OPEX should match fixedMaintenanceCosts in test_ates.esdl; got {cost_items}",
        )


@pytest.mark.skipif(not SIMULATOR_AVAILABLE, reason="omotes_simulator_core not installed")
class TestAllKPICategories(unittest.TestCase):
    """All supported KPI categories are present in the output ESDL.

    This is the canonical end-to-end test: simulator time series → KPI calculator → ESDL export.
    It enables debug_esdl so the output ESDL is saved as a CI artifact for inspection.
    """

    kpi_by_name: ClassVar[dict[str, "esdl.KPI"]]

    @classmethod
    def setUpClass(cls) -> None:
        debug_dir = tempfile.mkdtemp(prefix="debug_esdl_")
        cls.addClassCleanup(shutil.rmtree, debug_dir, True)
        config = _default_config()
        config["debug_esdl"] = True
        config["debug_esdl_dir"] = debug_dir
        try:
            cls.kpi_by_name = _get_kpi_by_name(config)
        except RuntimeError as e:
            raise unittest.SkipTest(f"Simulator infrastructure unavailable: {e}") from e

    def test__net_present_value_kpi_is_present(self) -> None:
        self.assertIn("Net Present Value [EUR]", self.kpi_by_name)

    def test__energy_breakdown_kpi_is_present(self) -> None:
        self.assertIn("Energy breakdown [Wh]", self.kpi_by_name)


class TestKPIDefaultWarnings(unittest.TestCase):
    """_parse_float_config emits a warning when a KPI config key is absent."""

    def test__missing_kpi_config_key__warns(self) -> None:
        cases = [
            ("system_lifetime", DEFAULT_SYSTEM_LIFETIME_YEARS),
            ("discount_rate", DEFAULT_DISCOUNT_RATE_PERCENT),
        ]
        for key, default in cases:
            with self.subTest(key=key):
                sentinel = f"missing-{key}-sentinel"

                with self.assertLogs(level=logging.WARNING) as cm:
                    result = _parse_float_config({}, key, default, warn_msg=sentinel)

                self.assertEqual(result, default)
                self.assertIn(sentinel, " ".join(cm.output))
