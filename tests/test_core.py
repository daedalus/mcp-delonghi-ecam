"""Tests for core models."""

from mcp_delonghi_ecam.core import (
    BEVERAGE_TO_ID,
    TASTE_TO_VALUE,
    TEMP_TO_VALUE,
    BeverageType,
    ResponseFormat,
    Taste,
    Temperature,
)


class TestBeverageType:
    """Tests for BeverageType enum."""

    def test_all_beverage_types_defined(self) -> None:
        """Verify all expected beverage types are defined."""
        expected = [
            "espresso",
            "coffee",
            "long_coffee",
            "espresso_2x",
            "doppio_plus",
            "americano",
            "cappuccino",
            "latte_macchiato",
            "caffe_latte",
            "flat_white",
            "espresso_macchiato",
            "hot_milk",
            "hot_water",
            "steam",
            "chocolate",
        ]
        actual = [b.value for b in BeverageType]
        for exp in expected:
            assert exp in actual

    def test_beverage_to_id_mapping_complete(self) -> None:
        """Verify all beverage types have protocol IDs."""
        for beverage in BeverageType:
            assert beverage in BEVERAGE_TO_ID
            assert BEVERAGE_TO_ID[beverage] > 0


class TestTaste:
    """Tests for Taste enum."""

    def test_all_taste_levels_defined(self) -> None:
        """Verify all taste levels are defined."""
        expected = ["extra_mild", "mild", "normal", "strong", "extra_strong"]
        actual = [t.value for t in Taste]
        assert expected == actual

    def test_taste_to_value_mapping(self) -> None:
        """Verify taste mapping."""
        assert TASTE_TO_VALUE[Taste.EXTRA_MILD] == 1
        assert TASTE_TO_VALUE[Taste.NORMAL] == 3
        assert TASTE_TO_VALUE[Taste.EXTRA_STRONG] == 5


class TestTemperature:
    """Tests for Temperature enum."""

    def test_all_temperature_levels_defined(self) -> None:
        """Verify all temperature levels are defined."""
        expected = ["low", "medium", "high"]
        actual = [t.value for t in Temperature]
        assert expected == actual

    def test_temperature_to_value_mapping(self) -> None:
        """Verify temperature mapping."""
        assert TEMP_TO_VALUE[Temperature.LOW] == 0
        assert TEMP_TO_VALUE[Temperature.MEDIUM] == 1
        assert TEMP_TO_VALUE[Temperature.HIGH] == 2


class TestResponseFormat:
    """Tests for ResponseFormat enum."""

    def test_format_options(self) -> None:
        """Verify format options."""
        assert ResponseFormat.MARKDOWN.value == "markdown"
        assert ResponseFormat.JSON.value == "json"
