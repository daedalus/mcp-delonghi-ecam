"""MCP server for DeLonghi ECAM coffee machines."""

import ipaddress

from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from mcp_delonghi_ecam.core import (
    BeverageType,
    ResponseFormat,
    Taste,
    Temperature,
)
from mcp_delonghi_ecam.services import get_service

mcp = FastMCP("mcp-delonghi-ecam")


class ConnectInput(BaseModel):
    """Input model for connecting to a coffee machine."""

    ip_address: str = Field(
        ...,
        description="IP address of the coffee machine on local network (e.g., '192.168.1.100')",
    )

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address format."""
        try:
            ipaddress.IPv4Address(v)
        except ValueError:
            raise ValueError("Invalid IP address format")
        return v


class BrewBeverageInput(BaseModel):
    """Input model for brewing a beverage."""

    beverage: BeverageType = Field(
        default=BeverageType.ESPRESSO,
        description="Type of beverage to brew",
    )
    coffee_amount: int = Field(
        default=40,
        description="Coffee amount in units (0-250)",
        ge=0,
        le=250,
    )
    taste: Taste = Field(
        default=Taste.NORMAL,
        description="Coffee strength/taste level",
    )
    temperature: Temperature = Field(
        default=Temperature.MEDIUM,
        description="Beverage temperature",
    )


class StatusInput(BaseModel):
    """Input model for getting status."""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class CupControlInput(BaseModel):
    """Input model for cup light/warmer control."""

    enabled: bool = Field(
        default=True,
        description="Enable (true) or disable (false) the feature",
    )


class GetRecipeInput(BaseModel):
    """Input model for getting beverage recipe."""

    beverage: BeverageType = Field(
        default=BeverageType.ESPRESSO,
        description="Type of beverage",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class MachineInfoInput(BaseModel):
    """Input model for getting machine info."""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class StatisticsInput(BaseModel):
    """Input model for getting statistics."""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


@mcp.tool(
    name="connect",
    annotations={
        "title": "Connect to Coffee Machine",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def connect(params: ConnectInput) -> str:
    """Connect to a DeLonghi ECAM coffee machine on the local network.

    This tool establishes a connection to the coffee machine using its IP address.
    The machine must be on the same local network as this server. The default
    port is 10280, which is the standard port for DeLonghi local API server.

    Args:
        params (ConnectInput): Connection parameters containing:
            - ip_address (str): IPv4 address of the coffee machine (e.g., "192.168.1.100")

    Returns:
        str: Success or error message.

    Example:
        >>> connect("192.168.1.100")
        "Connected to coffee machine at 192.168.1.100"
    """
    service = get_service()
    return await service.connect(params.ip_address)


@mcp.tool(
    name="disconnect",
    annotations={
        "title": "Disconnect from Coffee Machine",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def disconnect() -> str:
    """Disconnect from the currently connected coffee machine.

    This tool disconnects from the machine if a connection is active.
    It is safe to call even when not connected.

    Args:
        None

    Returns:
        str: Success message.

    Example:
        >>> disconnect()
        "Disconnected from coffee machine"
    """
    service = get_service()
    return await service.disconnect()


@mcp.tool(
    name="get_status",
    annotations={
        "title": "Get Machine Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_status(params: StatusInput) -> str:
    """Get the current status of the connected coffee machine.

    Returns information about the machine's current state including whether
    it's brewing, any active alarms, temperature, and switch states.

    Args:
        params (StatusInput): Parameters containing:
            - response_format (ResponseFormat): Output format - 'markdown' (default) or 'json'

    Returns:
        str: Formatted status information.

    Example:
        >>> get_status("markdown")
        "# Coffee Machine Status\n\n**State**: ReadyOrDispensing\n..."
    """
    service = get_service()
    return await service.get_status(params.response_format)


@mcp.tool(
    name="brew_beverage",
    annotations={
        "title": "Brew Beverage",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def brew_beverage(params: BrewBeverageInput) -> str:
    """Start brewing a beverage on the connected coffee machine.

    This command starts the brewing process for the specified beverage
    with the given parameters. The machine must be powered on and ready.

    Args:
        params (BrewBeverageInput): Brewing parameters containing:
            - beverage (BeverageType): Type of beverage (espresso, coffee, cappuccino, etc.)
            - coffee_amount (int): Coffee amount in units 0-250 (default: 40)
            - taste (Taste): Taste level - extra_mild, mild, normal, strong, extra_strong (default: normal)
            - temperature (Temperature): Temperature - low, medium, high (default: medium)

    Returns:
        str: Result message indicating success or error.

    Example:
        >>> brew_beverage("cappuccino", 40, "normal", "medium")
        "Started brewing cappuccino"
    """
    service = get_service()
    return await service.brew_beverage(
        params.beverage, params.coffee_amount, params.taste, params.temperature
    )


@mcp.tool(
    name="stop_brewing",
    annotations={
        "title": "Stop Brewing",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def stop_brewing() -> str:
    """Stop the currently brewing beverage.

    If a beverage is currently being prepared, this command stops it.
    Safe to call when not brewing.

    Args:
        None

    Returns:
        str: Result message.

    Example:
        >>> stop_brewing()
        "Brewing stopped"
    """
    service = get_service()
    return await service.stop_brewing()


@mcp.tool(
    name="turn_on",
    annotations={
        "title": "Turn Machine On",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def turn_on() -> str:
    """Turn the coffee machine on.

    Powers on the connected coffee machine. The machine will go through
    its normal startup sequence including heating and rinsing.

    Args:
        None

    Returns:
        str: Result message.

    Example:
        >>> turn_on()
        "Machine turned on"
    """
    service = get_service()
    return await service.turn_on()


@mcp.tool(
    name="turn_off",
    annotations={
        "title": "Turn Machine Off",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def turn_off() -> str:
    """Turn the coffee machine off.

    Powers off the connected coffee machine. The machine will perform
    a shutdown cycle.

    Args:
        None

    Returns:
        str: Result message.

    Example:
        >>> turn_off()
        "Machine turned off"
    """
    service = get_service()
    return await service.turn_off()


@mcp.tool(
    name="set_cup_light",
    annotations={
        "title": "Set Cup Light",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def set_cup_light(params: CupControlInput) -> str:
    """Control the cup illumination light.

    Turns the cup light on or off. The cup light illuminates the
    dispensing area.

    Args:
        params (CupControlInput): Parameters containing:
            - enabled (bool): True to turn on, False to turn off

    Returns:
        str: Result message.

    Example:
        >>> set_cup_light(true)
        "Cup light ON"
    """
    service = get_service()
    return await service.set_cup_light(params.enabled)


@mcp.tool(
    name="set_cup_warmer",
    annotations={
        "title": "Set Cup Warmer",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def set_cup_warmer(params: CupControlInput) -> str:
    """Control the cup warmer plate.

    Turns the cup warmer on or off. The cup warmer keeps cups and mugs
    warm while not in use.

    Args:
        params (CupControlInput): Parameters containing:
            - enabled (bool): True to turn on, False to turn off

    Returns:
        str: Result message.

    Example:
        >>> set_cup_warmer(true)
        "Cup warmer ON"
    """
    service = get_service()
    return await service.set_cup_warmer(params.enabled)


@mcp.tool(
    name="get_machine_info",
    annotations={
        "title": "Get Machine Info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_machine_info(params: MachineInfoInput) -> str:
    """Get machine information including serial number and model.

    Returns detailed information about the connected coffee machine
    such as serial number, model, software version, and bean system type.

    Args:
        params (MachineInfoInput): Parameters containing:
            - response_format (ResponseFormat): Output format - 'markdown' or 'json'

    Returns:
        str: Formatted machine information.

    Example:
        >>> get_machine_info("markdown")
        "# Machine Information\n\n**Serial Number**: 012345678901\n..."
    """
    service = get_service()
    return await service.get_machine_info(params.response_format)


@mcp.tool(
    name="get_statistics",
    annotations={
        "title": "Get Machine Statistics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_statistics(params: StatisticsInput) -> str:
    """Get machine usage statistics.

    Returns statistics about the machine's usage including total coffees
    brewed, maintenance indicators, etc.

    Args:
        params (StatisticsInput): Parameters containing:
            - response_format (ResponseFormat): Output format - 'markdown' or 'json'

    Returns:
        str: Formatted statistics.

    Example:
        >>> get_statistics("markdown")
        "# Machine Statistics\n\n**Total Coffees**: 150\n..."
    """
    service = get_service()
    return await service.get_statistics(params.response_format)


@mcp.tool(
    name="list_beverages",
    annotations={
        "title": "List Available Beverages",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_beverages() -> str:
    """List all beverages available on the connected machine.

    Returns a list of all beverage types that can be brewed on this
    specific coffee machine model.

    Args:
        None

    Returns:
        str: Formatted list of beverages.

    Example:
        >>> list_beverages()
        "# Available Beverages\n\n1. Espresso\n2. Coffee\n..."
    """
    service = get_service()
    return await service.list_beverages()


@mcp.tool(
    name="get_recipe",
    annotations={
        "title": "Get Beverage Recipe",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_recipe(params: GetRecipeInput) -> str:
    """Get the recipe parameters for a specific beverage.

    Returns the default recipe settings for a beverage including
    coffee amount, taste, temperature, and brew time.

    Args:
        params (GetRecipeInput): Parameters containing:
            - beverage (BeverageType): Type of beverage
            - response_format (ResponseFormat): Output format - 'markdown' or 'json'

    Returns:
        str: Formatted recipe information.

    Example:
        >>> get_recipe("espresso", "markdown")
        "# Recipe: Espresso\n\n**Coffee Amount**: 40\n..."
    """
    service = get_service()
    return await service.get_recipe(params.beverage, params.response_format)
