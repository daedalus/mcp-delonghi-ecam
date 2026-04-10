"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_ecam_client() -> AsyncMock:
    """Create a mock ECAM client."""
    client = AsyncMock()
    client.is_connected.return_value = True
    client.get_status.return_value = {
        "state": "ReadyOrDispensing",
        "state_code": 7,
        "temperature": "Medium",
        "switches": {
            "water_spout": False,
            "water_tank_absent": False,
            "drip_tray_full": False,
        },
        "alarms": [],
        "is_brewing": False,
        "progress": 0,
    }
    client.get_machine_info.return_value = {
        "serial_number": "123456789012",
        "model": "ECAM 550.55",
        "software_version": "1.0.0",
        "bean_system": "Single",
    }
    client.get_statistics.return_value = {
        "total_coffees": 100,
        "total_cappuccinos": 50,
        "total_lattes": 30,
        "total_water": 500,
        "descaling_needed": False,
        "filter_needed": True,
    }
    return client
