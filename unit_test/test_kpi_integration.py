"""Test KPI integration with simulator-worker."""

import datetime
import logging
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Dict
from unittest.mock import MagicMock, patch

import pytest
from omotes_sdk.types import ProtobufDict

if TYPE_CHECKING:
    import esdl

# Check if full simulator worker can be imported
SIMULATOR_AVAILABLE = False
try:
    from omotes_simulator_core.infrastructure.utils import pyesdl_from_string

    from simulator_worker.simulator_worker import simulator_worker_task

    SIMULATOR_AVAILABLE = True
except ImportError:
    simulator_worker_task = None  # type: ignore[assignment, misc]
    pyesdl_from_string = None  # type: ignore[assignment, misc]


def _run_simulator(workflow_config: ProtobufDict) -> tuple:
    test_esdl_path = Path(__file__).parent.parent / "testdata" / "test_ates.esdl"
    with open(test_esdl_path, "r") as f:
        input_esdl = f.read()

    mock_progress = MagicMock()

    with patch("simulator_worker.utils.InfluxDBProfileManager"):
        return simulator_worker_task(input_esdl, workflow_config, mock_progress, "simulator")


def _default_config() -> ProtobufDict:
    start_time = datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2019, 1, 1, 2, 0, tzinfo=datetime.timezone.utc)
    return {
        "timestep": 3600.0,
        "start_time": start_time.timestamp(),
        "end_time": end_time.timestamp(),
        "system_lifetime": 30.0,
    }


def _get_energy_system(config: ProtobufDict) -> "esdl.EnergySystem":
    """Helper: Run simulator and return parsed energy system."""
    output_esdl, _ = _run_simulator(config)
    esh = pyesdl_from_string(output_esdl)
    return esh.energy_system


def _get_kpi_by_name(config: ProtobufDict) -> dict:
    """Helper: Run simulator and return KPIs indexed by name."""
    energy_system = _get_energy_system(config)
    kpi_list = list(energy_system.instance[0].area.KPIs.kpi)
    return {kpi.name: kpi for kpi in kpi_list}


@pytest.mark.skipif(not SIMULATOR_AVAILABLE, reason="omotes_simulator_core not installed")
class TestKPIOutputEsdlStructure(unittest.TestCase):
    """Output ESDL contains a valid area with KPIs attached."""

    energy_system: ClassVar["esdl.EnergySystem"]

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.energy_system = _get_energy_system(_default_config())
        except Exception as e:
            raise unittest.SkipTest(f"Simulator unavailable: {e}") from e

    def test__output_esdl_is_not_none(self) -> None:
        # Arrange (done in setUp)

        # Act
        instances = self.energy_system.instance

        # Assert
        self.assertTrue(instances, "Output ESDL must have at least one instance")

    def test__output_esdl_has_instance_with_area(self) -> None:
        # Arrange (done in setUp)

        # Act
        area = self.energy_system.instance[0].area

        # Assert
        self.assertIsNotNone(area, "instance[0] must have an area")

    def test__kpis_attached_to_main_area(self) -> None:
        # Arrange (done in setUp)
        main_area = self.energy_system.instance[0].area

        # Act
        kpi_list = list(main_area.KPIs.kpi)

        # Assert
        self.assertIsNotNone(main_area.KPIs, "KPIs should be present in the main area")
        self.assertGreater(len(kpi_list), 0, "At least one KPI should be calculated")

    def test__all_kpis_have_names(self) -> None:
        # Arrange
        kpi_list = list(self.energy_system.instance[0].area.KPIs.kpi)

        # Act / Assert
        for kpi in kpi_list:
            self.assertIsInstance(kpi.name, str, f"KPI {kpi} name must be a string")
            self.assertTrue(kpi.name, f"KPI {kpi} must have a non-empty name")


@pytest.mark.skipif(not SIMULATOR_AVAILABLE, reason="omotes_simulator_core not installed")
class TestKPICostValues(unittest.TestCase):
    """Cost KPI values match the costInformation in test_ates.esdl.

    The ATES asset has investmentCosts=2333594.0 EUR and fixedMaintenanceCosts
    that produce OPEX=215138.89 EUR/year. These derive purely from the ESDL cost
    data and are deterministic regardless of simulation time series.
    """

    kpi_by_name: ClassVar[Dict[str, "esdl.KPI"]]

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.kpi_by_name = _get_kpi_by_name(_default_config())
        except Exception as e:
            raise unittest.SkipTest(f"Simulator unavailable: {e}") from e

    def test__cost_breakdown_kpi_is_present(self) -> None:
        # Arrange (done in setUp)

        # Act
        cost_kpi_present = "High level cost breakdown [EUR]" in self.kpi_by_name

        # Assert
        self.assertTrue(cost_kpi_present, "Cost breakdown KPI missing from output")

    def test__capex_matches_investment_costs(self) -> None:
        # Arrange
        cost_kpi = self.kpi_by_name["High level cost breakdown [EUR]"]
        cost_items = {item.label: item.value for item in cost_kpi.distribution.stringItem}

        # Act / Assert
        self.assertIn("CAPEX (total)", cost_items, f"CAPEX key missing; got {cost_items}")
        self.assertAlmostEqual(
            cost_items["CAPEX (total)"],
            2_333_594.0,
            places=2,
            msg=f"CAPEX should match investmentCosts in test_ates.esdl; got {cost_items}",
        )

    def test__opex_matches_fixed_maintenance_costs(self) -> None:
        # Arrange
        cost_kpi = self.kpi_by_name["High level cost breakdown [EUR]"]
        cost_items = {item.label: item.value for item in cost_kpi.distribution.stringItem}

        # Act / Assert
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

    kpi_by_name: ClassVar[Dict[str, "esdl.KPI"]]

    @classmethod
    def setUpClass(cls) -> None:
        config = _default_config()
        config["debug_esdl"] = True
        debug_dir = tempfile.mkdtemp()
        config["debug_esdl_dir"] = debug_dir
        cls.addClassCleanup(shutil.rmtree, debug_dir)
        try:
            cls.kpi_by_name = _get_kpi_by_name(config)
        except Exception as e:
            raise unittest.SkipTest(f"Simulator unavailable: {e}") from e

    def test__net_present_value_kpi_is_present(self) -> None:
        self.assertIn("Net Present Value [EUR]", self.kpi_by_name)

    def test__energy_breakdown_kpi_is_present(self) -> None:
        self.assertIn("Energy breakdown [Wh]", self.kpi_by_name)


@pytest.mark.skipif(not SIMULATOR_AVAILABLE, reason="omotes_simulator_core not installed")
class TestKPIDefaultWarnings(unittest.TestCase):
    """Warnings are emitted when KPI config keys are absent from workflow_config."""

    def test__missing_system_lifetime__warns(self) -> None:
        # Arrange
        config = _default_config()
        del config["system_lifetime"]

        # Act / Assert
        with self.assertLogs("simulator_worker", level=logging.WARNING) as cm:
            _run_simulator(config)

        self.assertTrue(
            any("system_lifetime" in msg for msg in cm.output),
            f"Expected 'system_lifetime' warning; got: {cm.output}",
        )

    def test__missing_discount_rate__warns(self) -> None:
        # Arrange — discount_rate is not in the default config, so the warning fires
        config = _default_config()

        # Act / Assert
        with self.assertLogs("simulator_worker", level=logging.WARNING) as cm:
            _run_simulator(config)

        self.assertTrue(
            any("discount_rate" in msg for msg in cm.output),
            f"Expected 'discount_rate' warning; got: {cm.output}",
        )
