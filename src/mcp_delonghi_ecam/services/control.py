"""Service layer for ECAM coffee machine control."""

import json
from typing import Any

from ..adapters import EcamClient, EcamConnectionError, EcamProtocolError
from ..core import (
    BEVERAGE_TO_ID,
    TASTE_TO_VALUE,
    TEMP_TO_VALUE,
    BeverageType,
    Recipe,
    ResponseFormat,
    Taste,
    Temperature,
)


class EcamService:
    """Service for controlling DeLonghi ECAM coffee machines."""

    def __init__(self) -> None:
        """Initialize the ECAM service."""
        self._client: EcamClient | None = None
        self._connected_ip: str | None = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to a machine."""
        return self._client is not None and self._client.is_connected()

    @property
    def machine_ip(self) -> str | None:
        """Get the connected machine IP."""
        return self._connected_ip

    async def connect(self, ip_address: str, port: int = 10280) -> str:
        """Connect to a coffee machine.

        Args:
            ip_address: IP address of the machine.
            port: Port number (default 10280).

        Returns:
            Success message.
        """
        if self._connected_ip == ip_address and self.is_connected:
            return f"Already connected to {ip_address}"

        self._client = EcamClient(ip_address, port)
        await self._client.connect()
        self._connected_ip = ip_address
        return f"Connected to coffee machine at {ip_address}"

    async def disconnect(self) -> str:
        """Disconnect from the current machine.

        Returns:
            Success message.
        """
        if self._client:
            await self._client.disconnect()
            self._client = None
            self._connected_ip = None
        return "Disconnected from coffee machine"

    async def get_status(self, format: ResponseFormat) -> str:
        """Get current machine status.

        Args:
            format: Output format (markdown or json).

        Returns:
            Formatted status response.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            status = await self._client.get_status()
            return self._format_status(status, format)
        except EcamConnectionError as e:
            return f"Error: Connection lost - {e}"
        except EcamProtocolError as e:
            return f"Error: Protocol error - {e}"
        except Exception as e:
            return f"Error: Unexpected error - {e}"

    def _format_status(self, status: dict[str, Any], format: ResponseFormat) -> str:
        """Format status data."""
        if format == ResponseFormat.JSON:
            return json.dumps(status, indent=2)

        lines = ["# Coffee Machine Status", ""]
        lines.append(f"**State**: {status['state']}")
        lines.append(f"**Temperature**: {status['temperature']}")
        lines.append(f"**Brewing**: {'Yes' if status['is_brewing'] else 'No'}")

        if status["progress"] > 0:
            lines.append(f"**Progress**: {status['progress']}%")

        if status["alarms"]:
            lines.append("")
            lines.append("**Alarms**:")
            for alarm in status["alarms"]:
                lines.append(f"  - {alarm}")
        else:
            lines.append("")
            lines.append("**Alarms**: None")

        lines.append("")
        lines.append("**Switches**:")
        for name, value in status["switches"].items():
            state = "ON" if value else "OFF"
            lines.append(f"  - {name}: {state}")

        return "\n".join(lines)

    async def brew_beverage(
        self,
        beverage: BeverageType,
        coffee_amount: int = 40,
        taste: Taste = Taste.NORMAL,
        temperature: Temperature = Temperature.MEDIUM,
    ) -> str:
        """Brew a beverage.

        Args:
            beverage: Type of beverage to brew.
            coffee_amount: Coffee amount (0-250).
            taste: Taste level.
            temperature: Temperature setting.

        Returns:
            Result message.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        beverage_id = BEVERAGE_TO_ID.get(beverage)
        if beverage_id is None:
            return f"Error: Unknown beverage type '{beverage.value}'"

        taste_val = TASTE_TO_VALUE.get(taste, 3)
        temp_val = TEMP_TO_VALUE.get(temperature, 1)

        try:
            await self._client.brew_beverage(
                beverage_id, coffee_amount, taste_val, temp_val
            )
            return f"Started brewing {beverage.value}"
        except EcamProtocolError as e:
            return f"Error: Failed to brew - {e}"
        except Exception as e:
            return f"Error: Unexpected error - {e}"

    async def stop_brewing(self) -> str:
        """Stop current brewing operation.

        Returns:
            Result message.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            await self._client.stop_brewing()
            return "Brewing stopped"
        except Exception as e:
            return f"Error: {e}"

    async def turn_on(self) -> str:
        """Turn the machine on.

        Returns:
            Result message.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            await self._client.turn_on()
            return "Machine turned on"
        except Exception as e:
            return f"Error: {e}"

    async def turn_off(self) -> str:
        """Turn the machine off.

        Returns:
            Result message.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            await self._client.turn_off()
            return "Machine turned off"
        except Exception as e:
            return f"Error: {e}"

    async def set_cup_light(self, enabled: bool) -> str:
        """Control cup light.

        Args:
            enabled: True to turn on, False to turn off.

        Returns:
            Result message.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            await self._client.set_cup_light(enabled)
            return f"Cup light {'ON' if enabled else 'OFF'}"
        except Exception as e:
            return f"Error: {e}"

    async def set_cup_warmer(self, enabled: bool) -> str:
        """Control cup warmer.

        Args:
            enabled: True to turn on, False to turn off.

        Returns:
            Result message.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            await self._client.set_cup_warmer(enabled)
            return f"Cup warmer {'ON' if enabled else 'OFF'}"
        except Exception as e:
            return f"Error: {e}"

    async def get_machine_info(self, format: ResponseFormat) -> str:
        """Get machine information.

        Args:
            format: Output format.

        Returns:
            Formatted machine info.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            info = await self._client.get_machine_info()
            return self._format_machine_info(info, format)
        except Exception as e:
            return f"Error: {e}"

    def _format_machine_info(self, info: dict[str, Any], format: ResponseFormat) -> str:
        """Format machine info."""
        if format == ResponseFormat.JSON:
            return json.dumps(info, indent=2)

        lines = ["# Machine Information", ""]
        lines.append(f"**Serial Number**: {info['serial_number']}")
        lines.append(f"**Model**: {info['model']}")
        lines.append(f"**Software Version**: {info['software_version']}")
        lines.append(f"**Bean System**: {info['bean_system']}")

        return "\n".join(lines)

    async def get_statistics(self, format: ResponseFormat) -> str:
        """Get machine statistics.

        Args:
            format: Output format.

        Returns:
            Formatted statistics.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        try:
            stats = await self._client.get_statistics()
            return self._format_statistics(stats, format)
        except Exception as e:
            return f"Error: {e}"

    def _format_statistics(self, stats: dict[str, int], format: ResponseFormat) -> str:
        """Format statistics."""
        if format == ResponseFormat.JSON:
            return json.dumps(stats, indent=2)

        lines = ["# Machine Statistics", ""]
        lines.append(f"**Total Coffees**: {stats.get('total_coffees', 0)}")
        lines.append(f"**Total Cappuccinos**: {stats.get('total_cappuccinos', 0)}")
        lines.append(f"**Total Lattes**: {stats.get('total_lattes', 0)}")
        lines.append(f"**Total Water**: {stats.get('total_water', 0)}")
        lines.append("")
        lines.append(
            f"**Descaling Needed**: {'Yes' if stats.get('descaling_needed') else 'No'}"
        )
        lines.append(
            f"**Filter Needed**: {'Yes' if stats.get('filter_needed') else 'No'}"
        )

        return "\n".join(lines)

    async def list_beverages(self) -> str:
        """List available beverages.

        Returns:
            List of beverages.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        beverages = [
            "Espresso",
            "Coffee",
            "Long Coffee",
            "Espresso x2",
            "Doppio+",
            "Americano",
            "Cappuccino",
            "Latte Macchiato",
            "Caffe Latte",
            "Flat White",
            "Espresso Macchiato",
            "Hot Milk",
            "Hot Water",
            "Steam",
            "Chocolate",
        ]

        lines = ["# Available Beverages", ""]
        for i, bev in enumerate(beverages, 1):
            lines.append(f"{i}. {bev}")

        return "\n".join(lines)

    async def get_recipe(self, beverage: BeverageType, format: ResponseFormat) -> str:
        """Get recipe for a beverage.

        Args:
            beverage: Beverage type.
            format: Output format.

        Returns:
            Recipe information.
        """
        if not self.is_connected or self._client is None:
            return "Error: Not connected to any coffee machine"

        recipes: dict[str, Recipe] = {
            "espresso": {
                "beverage": "espresso",
                "coffee_amount": 40,
                "taste": 3,
                "temperature": 1,
                "milk_amount": 0,
                "brew_time": 25,
            },
            "coffee": {
                "beverage": "coffee",
                "coffee_amount": 100,
                "taste": 3,
                "temperature": 1,
                "milk_amount": 0,
                "brew_time": 45,
            },
            "cappuccino": {
                "beverage": "cappuccino",
                "coffee_amount": 40,
                "taste": 3,
                "temperature": 1,
                "milk_amount": 80,
                "brew_time": 60,
            },
        }

        recipe = recipes.get(beverage.value)
        if recipe is None:
            return f"Error: No recipe found for {beverage.value}"

        if format == ResponseFormat.JSON:
            return json.dumps(recipe, indent=2)

        lines = [f"# Recipe: {beverage.value.title()}", ""]
        lines.append(f"**Coffee Amount**: {recipe['coffee_amount']}")
        lines.append(f"**Taste**: {recipe['taste']}")
        lines.append(f"**Temperature**: {recipe['temperature']}")
        lines.append(f"**Milk Amount**: {recipe['milk_amount']}")
        lines.append(f"**Brew Time**: {recipe['brew_time']}s")

        return "\n".join(lines)


# Global service instance
_service: EcamService | None = None


def get_service() -> EcamService:
    """Get the global service instance."""
    global _service
    if _service is None:
        _service = EcamService()
    return _service
