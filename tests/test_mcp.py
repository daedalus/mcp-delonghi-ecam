"""Tests for MCP tools."""

import pytest

from mcp_delonghi_ecam.core import BeverageType, ResponseFormat, Taste, Temperature
from mcp_delonghi_ecam.mcp import (
    BrewBeverageInput,
    ConnectInput,
    CupControlInput,
    MachineInfoInput,
    StatisticsInput,
    StatusInput,
)


class TestConnectInput:
    """Tests for ConnectInput validation."""

    def test_valid_ip_address(self) -> None:
        """Test valid IP addresses pass validation."""
        input_model = ConnectInput(ip_address="192.168.1.100")
        assert input_model.ip_address == "192.168.1.100"

    def test_valid_localhost(self) -> None:
        """Test localhost address passes validation."""
        input_model = ConnectInput(ip_address="127.0.0.1")
        assert input_model.ip_address == "127.0.0.1"

    def test_invalid_ip_format(self) -> None:
        """Test invalid IP addresses fail validation."""
        with pytest.raises(ValueError, match="Invalid IP address"):
            ConnectInput(ip_address="not.an.ip.address")

    def test_invalid_ip_too_many_octets(self) -> None:
        """Test invalid IP with too many octets."""
        with pytest.raises(ValueError):
            ConnectInput(ip_address="192.168.1.1.1")


class TestBrewBeverageInput:
    """Tests for BrewBeverageInput validation."""

    def test_default_values(self) -> None:
        """Test default parameter values."""
        input_model = BrewBeverageInput()
        assert input_model.beverage == BeverageType.ESPRESSO
        assert input_model.coffee_amount == 40
        assert input_model.taste == Taste.NORMAL
        assert input_model.temperature == Temperature.MEDIUM

    def test_custom_values(self) -> None:
        """Test custom parameter values."""
        input_model = BrewBeverageInput(
            beverage=BeverageType.CAPPUCCINO,
            coffee_amount=100,
            taste=Taste.STRONG,
            temperature=Temperature.HIGH,
        )
        assert input_model.beverage == BeverageType.CAPPUCCINO
        assert input_model.coffee_amount == 100
        assert input_model.taste == Taste.STRONG
        assert input_model.temperature == Temperature.HIGH

    def test_coffee_amount_bounds(self) -> None:
        """Test coffee amount boundary validation."""
        with pytest.raises(ValueError):
            BrewBeverageInput(coffee_amount=-1)

        with pytest.raises(ValueError):
            BrewBeverageInput(coffee_amount=251)

        # Valid bounds
        BrewBeverageInput(coffee_amount=0)
        BrewBeverageInput(coffee_amount=250)


class TestStatusInput:
    """Tests for StatusInput."""

    def test_default_format(self) -> None:
        """Test default response format."""
        input_model = StatusInput()
        assert input_model.response_format == ResponseFormat.MARKDOWN


class TestCupControlInput:
    """Tests for CupControlInput."""

    def test_default_enabled(self) -> None:
        """Test default enabled value."""
        input_model = CupControlInput()
        assert input_model.enabled is True


class TestMachineInfoInput:
    """Tests for MachineInfoInput."""

    def test_default_format(self) -> None:
        """Test default response format."""
        input_model = MachineInfoInput()
        assert input_model.response_format == ResponseFormat.MARKDOWN


class TestStatisticsInput:
    """Tests for StatisticsInput."""

    def test_default_format(self) -> None:
        """Test default response format."""
        input_model = StatisticsInput()
        assert input_model.response_format == ResponseFormat.MARKDOWN
