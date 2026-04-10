"""Network adapter for communicating with DeLonghi ECAM machines."""

import asyncio
import base64
import struct
from typing import Any

import httpx


class EcamProtocolError(Exception):
    """Exception raised for ECAM protocol errors."""

    pass


class EcamConnectionError(Exception):
    """Exception raised for connection errors."""

    pass


class EcamClient:
    """Client for communicating with DeLonghi ECAM machines via local network."""

    DEFAULT_PORT = 10280
    CONNECTION_TIMEOUT = 10.0
    COMMAND_TIMEOUT = 30.0

    # Request IDs
    MONITOR_V0 = 0x60
    MONITOR_V1 = 0x70
    MONITOR_V2 = 0x75
    BEVERAGE_DISPENSING = 0x83
    APP_CONTROL = 0x84
    PARAMETER_WRITE = 0x90
    PARAMETER_READ = 0x95
    STATISTICS_READ = 0xA2

    def __init__(self, ip_address: str, port: int = DEFAULT_PORT) -> None:
        """Initialize the ECAM client.

        Args:
            ip_address: IP address of the coffee machine.
            port: Port number for the local API server (default: 10280).
        """
        self.ip_address = ip_address
        self.port = port
        self.base_url = f"http://{ip_address}:{port}"
        self._connected = False

    def is_connected(self) -> bool:
        """Check if connected to the machine."""
        return self._connected

    async def connect(self) -> bool:
        """Connect to the coffee machine.

        Returns:
            True if connection successful.

        Raises:
            EcamConnectionError: If connection fails.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/local_lan/properties",
                    timeout=self.CONNECTION_TIMEOUT,
                )
                if response.status_code == 200:
                    self._connected = True
                    return True
                raise EcamConnectionError(
                    f"Failed to connect to machine at {self.ip_address}: "
                    f"status {response.status_code}"
                )
        except httpx.ConnectError as e:
            raise EcamConnectionError(
                f"Cannot connect to machine at {self.ip_address}:{self.port}. "
                "Ensure the machine is on and connected to the same network."
            ) from e
        except httpx.TimeoutException as e:
            raise EcamConnectionError(
                f"Connection to {self.ip_address} timed out."
            ) from e

    async def disconnect(self) -> None:
        """Disconnect from the coffee machine."""
        self._connected = False

    def _calculate_checksum(self, data: bytes) -> int:
        """Calculate checksum for ECAM protocol packets."""
        checksum = 0x1D0F
        for byte in data:
            checksum = ((checksum << 8) | (checksum >> 8)) ^ (byte & 0xFFFF)
        return checksum & 0xFFFF

    def _build_packet(self, request_id: int, data: bytes) -> bytes:
        """Build an ECAM protocol packet."""
        payload = bytes([request_id]) + data
        length = len(payload) + 3  # +3 for magic byte, length, and checksum
        packet = bytes([0x0D, length]) + payload
        checksum = self._calculate_checksum(packet)
        return packet + struct.pack(">H", checksum)

    def _parse_status(self, data: bytes) -> dict[str, Any]:
        """Parse status response from the machine."""
        if len(data) < 19:
            return {
                "state": "Unknown",
                "state_code": 0,
                "temperature": "Unknown",
                "switches": {},
                "alarms": [],
                "is_brewing": False,
                "progress": 0,
            }

        state_code = data[2]
        temp_code = data[3]

        state_map = {
            0: "StandBy",
            1: "TurningOn",
            2: "ShuttingDown",
            4: "Descaling",
            5: "SteamPreparation",
            6: "Recovery",
            7: "ReadyOrDispensing",
            8: "Rinsing",
            10: "MilkPreparation",
            11: "HotWaterDelivery",
            12: "MilkCleaning",
            16: "ChocolatePreparation",
        }

        temp_map = {0: "Low", 1: "Medium", 2: "High", 3: "VeryHigh"}

        switches = {
            "water_spout": bool(data[4] & 0x01),
            "motor_up": bool(data[4] & 0x02),
            "motor_down": bool(data[4] & 0x04),
            "waste_container": bool(data[4] & 0x08),
            "water_tank_absent": bool(data[4] & 0x10),
            "knob": bool(data[4] & 0x20),
            "water_level_low": bool(data[4] & 0x40),
        }

        alarm_codes = {
            0: "EmptyWaterTank",
            1: "CoffeeWasteContainerFull",
            2: "DescaleAlarm",
            3: "ReplaceWaterFilter",
            4: "CoffeeGroundTooFine",
            5: "CoffeeBeansEmpty",
        }

        alarms = []
        alarm_byte = data[5]
        for i, alarm_name in alarm_codes.items():
            if alarm_byte & (1 << i):
                alarms.append(alarm_name)

        is_brewing = state_code in (7, 10, 11, 12, 16)
        progress = data[8] if is_brewing else 0

        return {
            "state": state_map.get(state_code, "Unknown"),
            "state_code": state_code,
            "temperature": temp_map.get(temp_code, "Unknown"),
            "switches": switches,
            "alarms": alarms,
            "is_brewing": is_brewing,
            "progress": progress,
        }

    async def send_command(self, request_id: int, data: bytes) -> dict[str, Any]:
        """Send a command to the machine and get the response.

        Args:
            request_id: The request ID for the command.
            data: The data payload for the command.

        Returns:
            Parsed response from the machine.
        """
        packet = self._build_packet(request_id, data)
        encoded = base64.b64encode(packet).decode("ascii")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/local_lan/properties",
                    json={"app_data": encoded},
                    timeout=self.COMMAND_TIMEOUT,
                )
                response.raise_for_status()
                result = response.json()

                if "app_data" in result:
                    resp_data = base64.b64decode(result["app_data"])
                    return {"raw": resp_data.hex(), "data": resp_data}
                return result  # type: ignore[no-any-return]
        except httpx.TimeoutException as e:
            raise EcamProtocolError(
                f"Command timeout after {self.COMMAND_TIMEOUT}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise EcamProtocolError(
                f"Command failed with status {e.response.status_code}"
            ) from e

    async def get_status(self) -> dict[str, Any]:
        """Get the current machine status.

        Returns:
            Dictionary containing machine status information.
        """
        data = bytes([0x0F, 0x01])  # Monitor request
        result = await self.send_command(self.MONITOR_V2, data)
        return self._parse_status(result.get("data", b""))

    async def get_machine_info(self) -> dict[str, Any]:
        """Get machine information (serial, model, etc).

        Returns:
            Dictionary containing machine information.
        """
        serial_packet = self._build_packet(0x95, bytes([0xA6, 0x00]))
        encoded = base64.b64encode(serial_packet).decode("ascii")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/local_lan/properties",
                json={"d270_serialnumber": encoded},
                timeout=self.COMMAND_TIMEOUT,
            )

        result = response.json()
        if "d270_serialnumber" in result:
            data = base64.b64decode(result["d270_serialnumber"])
            serial = data[3:15].decode("ascii", errors="ignore").strip("\x00")
            return {
                "serial_number": serial,
                "model": "ECAM Series",
                "software_version": "Unknown",
                "bean_system": "Single" if data[2] == 0 else "Dual",
            }
        return {
            "serial_number": "Unknown",
            "model": "ECAM Series",
            "software_version": "Unknown",
            "bean_system": "Unknown",
        }

    async def turn_on(self) -> bool:
        """Turn the machine on.

        Returns:
            True if successful.
        """
        data = bytes([0x02, 0x01, 0x55, 0x12])
        await self.send_command(self.APP_CONTROL, data)
        await asyncio.sleep(1)
        return True

    async def turn_off(self) -> bool:
        """Turn the machine off.

        Returns:
            True if successful.
        """
        data = bytes([0x02, 0x02, 0x55, 0x12])
        await self.send_command(self.APP_CONTROL, data)
        return True

    async def brew_beverage(
        self,
        beverage_id: int,
        coffee_amount: int = 40,
        taste: int = 3,
        temperature: int = 1,
    ) -> bool:
        """Start brewing a beverage.

        Args:
            beverage_id: The beverage ID to brew.
            coffee_amount: Coffee amount (0-250).
            taste: Taste level (0-5).
            temperature: Temperature setting (0-3).

        Returns:
            True if brewing started successfully.
        """
        data = bytes(
            [
                0x01,  # Start
                beverage_id,
                coffee_amount & 0xFF,
                (coffee_amount >> 8) & 0xFF,
                taste,
                temperature,
            ]
        )
        await self.send_command(self.BEVERAGE_DISPENSING, data)
        return True

    async def stop_brewing(self, beverage_id: int = 1) -> bool:
        """Stop the current brewing operation.

        Args:
            beverage_id: The beverage ID to stop.

        Returns:
            True if stopped successfully.
        """
        data = bytes([0x02, beverage_id])
        await self.send_command(self.BEVERAGE_DISPENSING, data)
        return True

    async def set_cup_light(self, enabled: bool) -> bool:
        """Control the cup light.

        Args:
            enabled: True to turn on, False to turn off.

        Returns:
            True if successful.
        """
        light_state = 0x99 if enabled else 0x91
        data = bytes([0x0F, 0x00, 0x3F, 0x00, 0x00, 0x00, light_state & 0xFF])
        await self.send_command(self.PARAMETER_WRITE, data)
        return True

    async def set_cup_warmer(self, enabled: bool) -> bool:
        """Control the cup warmer.

        Args:
            enabled: True to turn on, False to turn off.

        Returns:
            True if successful.
        """
        warmer_state = 0xB1 if enabled else 0x91
        data = bytes([0x0F, 0x00, 0x3F, 0x00, 0x00, 0x00, warmer_state & 0xFF])
        await self.send_command(self.PARAMETER_WRITE, data)
        return True

    async def get_statistics(self) -> dict[str, int]:
        """Get machine statistics.

        Returns:
            Dictionary containing usage statistics.
        """
        data = bytes([0x00])
        result = await self.send_command(self.STATISTICS_READ, data)
        raw_data = result.get("data", b"")

        if len(raw_data) < 20:
            return {
                "total_coffees": 0,
                "total_cappuccinos": 0,
                "total_lattes": 0,
                "total_water": 0,
                "descaling_needed": False,
                "filter_needed": False,
            }

        return {
            "total_coffees": struct.unpack("<H", raw_data[2:4])[0],
            "total_cappuccinos": struct.unpack("<H", raw_data[4:6])[0],
            "total_lattes": struct.unpack("<H", raw_data[6:8])[0],
            "total_water": struct.unpack("<H", raw_data[8:10])[0],
            "descaling_needed": bool(raw_data[10] & 0x01),
            "filter_needed": bool(raw_data[10] & 0x02),
        }


async def discover_machines(timeout: float = 5.0) -> list[dict[str, str]]:  # noqa: ARG001
    """Discover ECAM machines on the local network using UDP broadcast.

    Args:
        timeout: Timeout in seconds for discovery.

    Returns:
        List of discovered machines with IP and info.
    """
    machines: list[dict[str, str]] = []

    # Common IP ranges for DeLonghi machines
    # In practice, you'd need to scan the local network
    # This is a placeholder for network discovery
    return machines
