"""Edge-case and unit tests to close coverage gaps.

Covers meteorological southern-hemisphere branches, the solstice-day trend,
coordinator event/unload helpers, and the sensor None-guards.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from solsticehub import calculations as calc  # noqa: E402


# --------------------------------------------------------------------------- #
# Calculation edge cases
# --------------------------------------------------------------------------- #


def test_meteorological_southern_summer() -> None:
    """Southern meteorological December resolves to summer."""
    data = calc.calculate_season_data(
        "southern", "meteorological", datetime(2026, 12, 15, 12, tzinfo=timezone.utc)
    )
    assert data["current_season"] == "summer"


def test_meteorological_southern_autumn() -> None:
    """Southern meteorological April resolves to autumn."""
    data = calc.calculate_season_data(
        "southern", "meteorological", datetime(2026, 4, 15, 12, tzinfo=timezone.utc)
    )
    assert data["current_season"] == "autumn"


def test_meteorological_southern_spring() -> None:
    """Southern meteorological October resolves to spring."""
    data = calc.calculate_season_data(
        "southern", "meteorological", datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
    )
    assert data["current_season"] == "spring"


def test_astronomical_southern_summer() -> None:
    """Southern astronomical late December (after the solstice) is summer."""
    data = calc.calculate_season_data(
        "southern", "astronomical", datetime(2026, 12, 25, 12, tzinfo=timezone.utc)
    )
    assert data["current_season"] == "summer"


def test_astronomical_southern_autumn() -> None:
    """Southern astronomical April (after the March equinox) is autumn."""
    data = calc.calculate_season_data(
        "southern", "astronomical", datetime(2026, 4, 15, 12, tzinfo=timezone.utc)
    )
    assert data["current_season"] == "autumn"


def test_cross_quarter_next_event_fallback() -> None:
    """get_next_cross_quarter_event falls back to Yule when all events are past."""
    current = calc.get_cross_quarter_events_astronomical(2026)
    nxt = calc.get_cross_quarter_events_astronomical(2027)
    far_future = datetime(2030, 1, 1, tzinfo=timezone.utc)
    event_date, event_name = calc.get_next_cross_quarter_event(far_future, current, nxt)
    assert event_name == "yule"
    assert event_date is not None


def test_trend_on_solstice_day() -> None:
    """On the exact June solstice day the trend is 'solstice_today'."""
    june = calc.get_astronomical_events(2026)["june_solstice"]
    data = calc.calculate_season_data("northern", "astronomical", june)
    assert data["daylight_trend"] == "solstice_today"


def test_cross_quarter_before_first_event_of_year() -> None:
    """Early January is before the first cross-quarter event of the year."""
    data = calc.calculate_cross_quarter_data(
        "northern", "astronomical", datetime(2026, 1, 5, 12, tzinfo=timezone.utc)
    )
    # Period started in the previous year (Yule).
    assert data["current_period"] == "yule"
    assert data["period_age"] >= 0


def test_chinese_after_last_term_of_year() -> None:
    """Late December is after the last solar term and before next year's first."""
    data = calc.calculate_chinese_solar_terms_data(
        "northern", "all_24", datetime(2026, 12, 30, 12, tzinfo=timezone.utc)
    )
    assert data["current_term"] == "dongzhi"
    assert data["days_until_next_change"] >= 0


# --------------------------------------------------------------------------- #
# Coordinator helpers (all device types)
# --------------------------------------------------------------------------- #

COORDINATOR_MODULES = [
    "solsticehub.coordinator",
    "solsticehub.cross_quarter_coordinator",
    "solsticehub.chinese_coordinator",
]


@pytest.mark.parametrize("module", COORDINATOR_MODULES)
def test_time_until_midnight_minimum(module) -> None:
    """Less than a minute to midnight falls back to a full day."""
    mod = __import__(module, fromlist=["_calculate_time_until_midnight"])
    with patch.object(mod, "dt_util") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 2, 15, 23, 59, 40)
        assert mod._calculate_time_until_midnight() == timedelta(days=1)


COORDINATOR_CLASSES = [
    ("solsticehub.coordinator", "SolsticeHubCoordinator"),
    ("solsticehub.cross_quarter_coordinator", "CrossQuarterCoordinator"),
    ("solsticehub.chinese_coordinator", "ChineseSolarTermsCoordinator"),
]


@pytest.mark.parametrize("module,cls_name", COORDINATOR_CLASSES)
async def test_handle_event_update_refreshes(module, cls_name) -> None:
    """The event callback triggers a coordinator refresh."""
    mod = __import__(module, fromlist=[cls_name])
    cls = getattr(mod, cls_name)
    coord = cls.__new__(cls)
    coord.config_entry = MagicMock()
    coord.async_refresh = AsyncMock()
    await coord._handle_event_update(datetime(2026, 6, 21, tzinfo=timezone.utc))
    coord.async_refresh.assert_awaited_once()


@pytest.mark.parametrize("module,cls_name", COORDINATOR_CLASSES)
def test_async_unload_cancels_listener(module, cls_name) -> None:
    """async_unload cancels and clears the event listener."""
    mod = __import__(module, fromlist=[cls_name])
    cls = getattr(mod, cls_name)
    coord = cls.__new__(cls)
    unsub = MagicMock()
    coord._unsub_event = unsub
    coord.async_unload()
    unsub.assert_called_once()
    assert coord._unsub_event is None


@pytest.mark.parametrize("module,cls_name", COORDINATOR_CLASSES)
def test_schedule_event_cancels_previous(module, cls_name) -> None:
    """Scheduling a new event cancels the previous listener first."""
    mod = __import__(module, fromlist=[cls_name])
    cls = getattr(mod, cls_name)
    with patch.object(mod, "async_track_point_in_time") as mock_track, patch.object(
        mod, "dt_util"
    ) as mock_dt:
        now = datetime(2026, 3, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_dt.utcnow.return_value = now
        coord = cls.__new__(cls)
        coord.hass = MagicMock()
        coord.config_entry = MagicMock()
        old_unsub = MagicMock()
        coord._unsub_event = old_unsub
        coord._schedule_event_update(now + timedelta(hours=5))
        old_unsub.assert_called_once()
        mock_track.assert_called_once()


# --------------------------------------------------------------------------- #
# Sensor None-guards (coordinator without data)
# --------------------------------------------------------------------------- #


def _make_sensor(module, cls_name, descriptions_first):
    mod = __import__(module, fromlist=[cls_name])
    cls = getattr(mod, cls_name)
    sensor = cls.__new__(cls)
    sensor.coordinator = MagicMock()
    sensor.coordinator.data = None
    sensor.entity_description = descriptions_first
    sensor._config_entry = MagicMock()
    return sensor


def test_four_seasons_sensor_none_data() -> None:
    """Four Seasons sensor returns None when the coordinator has no data."""
    from solsticehub.sensor import FOUR_SEASONS_SENSOR_DESCRIPTIONS

    sensor = _make_sensor(
        "solsticehub.sensor", "FourSeasonsSensor", FOUR_SEASONS_SENSOR_DESCRIPTIONS[0]
    )
    assert sensor.native_value is None
    assert sensor.extra_state_attributes is None
    assert sensor.icon == FOUR_SEASONS_SENSOR_DESCRIPTIONS[0].icon


def test_cross_quarter_sensor_none_data() -> None:
    """Cross-Quarter sensor returns None when the coordinator has no data."""
    from solsticehub.cross_quarter_sensor import CROSS_QUARTER_SENSOR_DESCRIPTIONS

    sensor = _make_sensor(
        "solsticehub.cross_quarter_sensor",
        "CrossQuarterSensor",
        CROSS_QUARTER_SENSOR_DESCRIPTIONS[0],
    )
    assert sensor.native_value is None
    assert sensor.extra_state_attributes is None
    assert sensor.icon == CROSS_QUARTER_SENSOR_DESCRIPTIONS[0].icon


def test_chinese_sensor_none_data() -> None:
    """Chinese sensor returns None when the coordinator has no data."""
    from solsticehub.chinese_sensor import get_chinese_sensor_descriptions

    descriptions = get_chinese_sensor_descriptions("all_24")
    sensor = _make_sensor(
        "solsticehub.chinese_sensor", "ChineseSolarTermsSensor", descriptions[0]
    )
    assert sensor.native_value is None
    assert sensor.extra_state_attributes is None
    assert sensor.icon == descriptions[0].icon
