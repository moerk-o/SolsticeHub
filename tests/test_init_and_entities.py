"""Integration tests: set up each device type and verify entities.

These cover __init__ (setup/unload), all sensor platforms, base sensors,
and the per-device coordinators end to end.
"""

import sys
from pathlib import Path

import pytest
from freezegun import freeze_time
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from solsticehub.const import DOMAIN  # noqa: E402

FROZEN = "2026-06-22 12:00:00+00:00"

BASE_SUFFIXES = {"solar_longitude", "daylight_trend", "next_daylight_trend_change"}
FOUR_SEASONS_SUFFIXES = {
    "current_season",
    "spring_equinox",
    "summer_solstice",
    "autumn_equinox",
    "winter_solstice",
    "next_season_change",
} | BASE_SUFFIXES
CROSS_QUARTER_SUFFIXES = {"current_period", "next_period_change"} | BASE_SUFFIXES
CHINESE_SUFFIXES = {"current_term", "next_term_change"} | BASE_SUFFIXES


async def _setup(hass: HomeAssistant, data: dict) -> MockConfigEntry:
    """Create and set up a config entry, return it."""
    entry = MockConfigEntry(
        domain=DOMAIN, data=data, unique_id=data["name"].lower(), version=1
    )
    entry.add_to_hass(hass)
    with freeze_time(FROZEN):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


def _suffixes(hass: HomeAssistant, entry: MockConfigEntry) -> set[str]:
    """Return the unique-id suffixes registered for the entry."""
    registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(registry, entry.entry_id)
    return {e.unique_id.split("_", 1)[1] for e in entities}


def _state_for(hass: HomeAssistant, entry: MockConfigEntry, suffix: str):
    """Return the state object for the entity whose unique id ends with suffix."""
    registry = er.async_get(hass)
    for e in er.async_entries_for_config_entry(registry, entry.entry_id):
        if e.unique_id.endswith(suffix):
            return hass.states.get(e.entity_id)
    return None


@pytest.mark.parametrize("language", ["en", "de"])
async def test_entity_ids_are_fully_english(hass: HomeAssistant, language) -> None:
    """Entity IDs are fully English and independent of the localized device name.

    Even with a non-English device name and a German system, the entity_id is
    built from the English device type/mode label, not the device name.
    """
    hass.config.language = language
    entry = await _setup(
        hass,
        {
            "name": "Schöner Garten",  # non-English device name
            "device_type": "four_seasons",
            "hemisphere": "northern",
            "mode": "astronomical",
        },
    )

    registry = er.async_get(hass)
    entity_ids = [
        e.entity_id
        for e in er.async_entries_for_config_entry(registry, entry.entry_id)
    ]
    # Every entity ID is the English type/mode prefix + English sensor key.
    for suffix in FOUR_SEASONS_SUFFIXES:
        assert f"sensor.four_seasons_astronomical_{suffix}" in entity_ids, (
            suffix,
            entity_ids,
        )
    # Neither the device name nor a translated entity name leaked into the IDs.
    joined = " ".join(entity_ids)
    assert "garten" not in joined
    assert "jahreszeit" not in joined
    assert "sonnenwende" not in joined


async def test_device_model_stays_english_on_german_system(hass: HomeAssistant) -> None:
    """The device model is a stable English identifier, never localized."""
    hass.config.language = "de"
    entry = await _setup(
        hass,
        {
            "name": "Home",
            "device_type": "four_seasons",
            "hemisphere": "northern",
            "mode": "astronomical",
        },
    )
    device = dr.async_get(hass).async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert device.model == "Four Seasons (Astronomical)"


@pytest.mark.parametrize("hemisphere", ["northern", "southern"])
@pytest.mark.parametrize("mode", ["astronomical", "meteorological"])
async def test_four_seasons_setup(hass: HomeAssistant, hemisphere, mode) -> None:
    """Four Seasons sets up all entities for both hemispheres and modes."""
    entry = await _setup(
        hass,
        {
            "name": f"Home {hemisphere} {mode}",
            "device_type": "four_seasons",
            "hemisphere": hemisphere,
            "mode": mode,
        },
    )
    assert entry.state is ConfigEntryState.LOADED
    assert _suffixes(hass, entry) == FOUR_SEASONS_SUFFIXES

    season = _state_for(hass, entry, "current_season")
    assert season.state in {"spring", "summer", "autumn", "winter"}
    assert season.attributes["mode"] == mode
    assert season.attributes["hemisphere"] == hemisphere

    trend = _state_for(hass, entry, "daylight_trend")
    assert trend.state in {
        "days_getting_longer",
        "days_getting_shorter",
        "solstice_today",
    }

    # solar_longitude is a diagnostic sensor, disabled by default (no state).
    registry = er.async_get(hass)
    sol = next(
        e
        for e in er.async_entries_for_config_entry(registry, entry.entry_id)
        if e.unique_id.endswith("solar_longitude")
    )
    assert sol.disabled_by is not None

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.parametrize("mode", ["astronomical", "traditional"])
async def test_cross_quarter_setup(hass: HomeAssistant, mode) -> None:
    """Cross-Quarter sets up its entities for both modes."""
    entry = await _setup(
        hass,
        {
            "name": f"Wheel {mode}",
            "device_type": "cross_quarter",
            "hemisphere": "northern",
            "mode": mode,
            "naming": "celtic",
        },
    )
    assert entry.state is ConfigEntryState.LOADED
    assert _suffixes(hass, entry) == CROSS_QUARTER_SUFFIXES

    period = _state_for(hass, entry, "current_period")
    assert period.state in {
        "yule",
        "imbolc",
        "ostara",
        "beltane",
        "litha",
        "lughnasadh",
        "mabon",
        "samhain",
    }
    assert period.attributes["mode"] == mode


@pytest.mark.parametrize("scope", ["all_24", "8_major"])
async def test_chinese_setup(hass: HomeAssistant, scope) -> None:
    """Chinese Solar Terms sets up its entities for both scopes."""
    entry = await _setup(
        hass,
        {
            "name": f"Terms {scope}",
            "device_type": "chinese",
            "hemisphere": "northern",
            "scope": scope,
            "naming": "system",
        },
    )
    assert entry.state is ConfigEntryState.LOADED
    assert _suffixes(hass, entry) == CHINESE_SUFFIXES

    term = _state_for(hass, entry, "current_term")
    assert term.state  # a non-empty solar-term key
    assert term.attributes["scope"] == scope


async def test_legacy_entry_without_device_type_defaults_to_four_seasons(
    hass: HomeAssistant,
) -> None:
    """An entry lacking device_type falls back to Four Seasons (back-compat)."""
    entry = await _setup(
        hass,
        {"name": "Legacy", "hemisphere": "northern", "mode": "astronomical"},
    )
    assert entry.state is ConfigEntryState.LOADED
    assert _suffixes(hass, entry) == FOUR_SEASONS_SUFFIXES
