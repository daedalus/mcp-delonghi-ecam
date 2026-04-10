"""Core domain models and enums for DeLonghi ECAM coffee machines."""

from enum import StrEnum
from typing import TypedDict


class BeverageType(StrEnum):
    """Types of beverages available on ECAM machines."""

    ESPRESSO = "espresso"
    REGULAR_COFFEE = "coffee"
    LONG_COFFEE = "long_coffee"
    ESPRESSO_2X = "espresso_2x"
    DOPPIO_PLUS = "doppio_plus"
    AMERICANO = "americano"
    CAPPUCCINO = "cappuccino"
    LATTE_MACCHIATO = "latte_macchiato"
    CAFFE_LATTE = "caffe_latte"
    FLAT_WHITE = "flat_white"
    ESPRESSO_MACCHIATO = "espresso_macchiato"
    HOT_MILK = "hot_milk"
    HOT_WATER = "hot_water"
    STEAM = "steam"
    CHOCOLATE = "chocolate"


class Taste(StrEnum):
    """Coffee strength/taste levels."""

    EXTRA_MILD = "extra_mild"
    MILD = "mild"
    NORMAL = "normal"
    STRONG = "strong"
    EXTRA_STRONG = "extra_strong"


class Temperature(StrEnum):
    """Beverage temperature settings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResponseFormat(StrEnum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


class EcamMachineState(StrEnum):
    """ECAM machine states."""

    STANDBY = "StandBy"
    TURNING_ON = "TurningOn"
    SHUTTING_DOWN = "ShuttingDown"
    DESCALE = "Descaling"
    STEAM_PREP = "SteamPreparation"
    RECOVERY = "Recovery"
    READY = "ReadyOrDispensing"
    RINSING = "Rinsing"
    MILK_PREP = "MilkPreparation"
    HOT_WATER = "HotWaterDelivery"
    MILK_CLEAN = "MilkCleaning"
    CHOCOLATE = "ChocolatePreparation"


# Beverage type to protocol ID mapping
BEVERAGE_TO_ID: dict[BeverageType, int] = {
    BeverageType.ESPRESSO: 1,
    BeverageType.REGULAR_COFFEE: 2,
    BeverageType.LONG_COFFEE: 3,
    BeverageType.ESPRESSO_2X: 4,
    BeverageType.DOPPIO_PLUS: 5,
    BeverageType.AMERICANO: 6,
    BeverageType.CAPPUCCINO: 7,
    BeverageType.LATTE_MACCHIATO: 8,
    BeverageType.CAFFE_LATTE: 9,
    BeverageType.FLAT_WHITE: 10,
    BeverageType.ESPRESSO_MACCHIATO: 11,
    BeverageType.HOT_MILK: 12,
    BeverageType.CAPPUCCINO: 13,
    BeverageType.HOT_WATER: 16,
    BeverageType.STEAM: 17,
    BeverageType.CHOCOLATE: 18,
}

# Taste to protocol value mapping
TASTE_TO_VALUE: dict[Taste, int] = {
    Taste.EXTRA_MILD: 1,
    Taste.MILD: 2,
    Taste.NORMAL: 3,
    Taste.STRONG: 4,
    Taste.EXTRA_STRONG: 5,
}

# Temperature to protocol value mapping
TEMP_TO_VALUE: dict[Temperature, int] = {
    Temperature.LOW: 0,
    Temperature.MEDIUM: 1,
    Temperature.HIGH: 2,
}


class MachineStatus(TypedDict):
    """Current status of the coffee machine."""

    state: str
    state_code: int
    temperature: str
    switches: dict[str, bool]
    alarms: list[str]
    is_brewing: bool
    progress: int


class MachineInfo(TypedDict):
    """Machine information."""

    serial_number: str
    model: str
    software_version: str
    bean_system: str


class MachineStatistics(TypedDict):
    """Machine usage statistics."""

    total_coffees: int
    total_cappuccinos: int
    total_lattes: int
    total_water: int
    descaling_needed: bool
    filter_needed: bool


class Recipe(TypedDict):
    """Beverage recipe configuration."""

    beverage: str
    coffee_amount: int
    taste: int
    temperature: int
    milk_amount: int
    brew_time: int
