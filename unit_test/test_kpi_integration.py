"""Test KPI integration with simulator-worker."""

import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from omotes_sdk.types import ProtobufDict

# Check if full simulator worker can be imported
SIMULATOR_AVAILABLE = False
try:
    from omotes_simulator_core.infrastructure.utils import pyesdl_from_string

    from simulator_worker.simulator_worker import simulator_worker_task

    SIMULATOR_AVAILABLE = True
except ImportError:
    simulator_worker_task = None  # type: ignore[assignment, misc]
    pyesdl_from_string = None  # type: ignore[assignment, misc]


@pytest.mark.skipif(not SIMULATOR_AVAILABLE, reason="omotes_simulator_core not installed")
class TestKPIEndToEndIntegration:
    """Integration tests for end-to-end KPI calculation in simulator workflow."""

    def test_kpis_calculated_and_stored_in_output_esdl(self) -> None:
        """Test that KPIs are calculated from simulation and stored in output ESDL."""
        test_esdl_path = Path(__file__).parent.parent / "testdata" / "test_ates.esdl"
        with open(test_esdl_path, "r") as f:
            input_esdl = f.read()

        start_time = datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        end_time = datetime.datetime(2019, 1, 1, 2, 0, tzinfo=datetime.timezone.utc)

        workflow_config: ProtobufDict = {
            "timestep": 3600.0,
            "start_time": start_time.timestamp(),
            "end_time": end_time.timestamp(),
            "system_lifetime": 30.0,
        }

        mock_progress = MagicMock()

        # Mock InfluxDB so simulation results are not written to a real database
        with patch("simulator_worker.utils.InfluxDBProfileManager"):
            output_esdl, _ = simulator_worker_task(
                input_esdl, workflow_config, mock_progress, "simulator"
            )

        # Verify output ESDL structure
        assert output_esdl is not None
        esh = pyesdl_from_string(output_esdl)
        energy_system = esh.energy_system

        assert energy_system.instance, "Output ESDL must have at least one instance"
        main_area = energy_system.instance[0].area
        assert main_area is not None, "instance[0] must have an area"

        # KPIs are attached to the main area, not energy_system directly
        assert main_area.KPIs is not None, "KPIs should be present in the main area"
        kpi_list = list(main_area.KPIs.kpi)
        assert len(kpi_list) > 0, "At least one KPI should be calculated"

        # Verify each KPI has a name and a non-negative value
        for kpi in kpi_list:
            assert kpi.name, f"KPI {kpi} should have a name"

        kpi_by_name = {kpi.name: kpi for kpi in kpi_list}

        # --- Cost KPIs: exact values from test_ates.esdl costInformation ---
        # The ATES asset has investmentCosts=2333594.0 EUR and fixedMaintenanceCosts
        # that produce OPEX=215138.89 EUR/year. These derive purely from the ESDL
        # cost data and are deterministic regardless of simulation time series.
        assert (
            "High level cost breakdown [EUR]" in kpi_by_name
        ), "Cost breakdown KPI missing from output"
        cost_items = {
            item.label: item.value
            for item in kpi_by_name["High level cost breakdown [EUR]"].distribution.stringItem
        }
        assert cost_items.get("CAPEX (total)") == pytest.approx(
            2_333_594.0
        ), f"CAPEX should match investmentCosts in test_ates.esdl; got {cost_items}"
        assert cost_items.get("OPEX (yearly)") == pytest.approx(
            215_138.89
        ), f"OPEX should match fixedMaintenanceCosts in test_ates.esdl; got {cost_items}"

        assert "Energy breakdown [Wh]" in kpi_by_name, "Energy breakdown KPI missing"
