"""Regression tests for the naming style option (issue #10).

The naming option selects the translation key of the enum sensor, which in
turn selects the displayed state names: "system" uses language-dependent
descriptive names, "celtic"/"pinyin"/"hanzi" language-independent ones.
"""

import json
import sys
from pathlib import Path

import pytest
from freezegun import freeze_time
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from solsticehub.const import (  # noqa: E402
    CHINESE_TERM_NAMES,
    CROSS_QUARTER_PERIODS,
    DOMAIN,
)

FROZEN = "2026-06-22 12:00:00+00:00"

TRANSLATIONS_DIR = (
    Path(__file__).parent.parent
    / "custom_components"
    / "solsticehub"
    / "translations"
)
LANGUAGES = ["en", "de", "nl"]


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


def _translation_key_for(
    hass: HomeAssistant, entry: MockConfigEntry, suffix: str
) -> str | None:
    """Return the registry translation_key of the entity ending with suffix."""
    registry = er.async_get(hass)
    for e in er.async_entries_for_config_entry(registry, entry.entry_id):
        if e.unique_id.endswith(suffix):
            return e.translation_key
    return None


@pytest.mark.parametrize(
    ("naming", "expected_key"),
    [
        ("system", "current_period"),
        ("celtic", "current_period_celtic"),
    ],
)
async def test_cross_quarter_naming_selects_translation_key(
    hass: HomeAssistant, naming, expected_key
) -> None:
    """Cross-Quarter current_period uses the translation key for the naming."""
    entry = await _setup(
        hass,
        {
            "name": "CQ Test",
            "device_type": "cross_quarter",
            "hemisphere": "northern",
            "mode": "astronomical",
            "naming": naming,
        },
    )
    assert _translation_key_for(hass, entry, "current_period") == expected_key


@pytest.mark.parametrize(
    ("naming", "expected_key"),
    [
        ("system", "current_term"),
        ("pinyin", "current_term_pinyin"),
        ("hanzi", "current_term_hanzi"),
    ],
)
async def test_chinese_naming_selects_translation_key(
    hass: HomeAssistant, naming, expected_key
) -> None:
    """Chinese current_term uses the translation key for the naming."""
    entry = await _setup(
        hass,
        {
            "name": "CN Test",
            "device_type": "chinese",
            "hemisphere": "northern",
            "scope": "all_24",
            "naming": naming,
        },
    )
    assert _translation_key_for(hass, entry, "current_term") == expected_key


async def test_missing_naming_falls_back_to_system(hass: HomeAssistant) -> None:
    """Entries without a stored naming behave like naming=system."""
    entry = await _setup(
        hass,
        {
            "name": "CQ Legacy",
            "device_type": "cross_quarter",
            "hemisphere": "northern",
            "mode": "traditional",
        },
    )
    assert _translation_key_for(hass, entry, "current_period") == "current_period"


async def test_naming_does_not_affect_other_sensors(hass: HomeAssistant) -> None:
    """Only the enum sensor's translation key depends on the naming option."""
    entry = await _setup(
        hass,
        {
            "name": "CQ Other",
            "device_type": "cross_quarter",
            "hemisphere": "northern",
            "mode": "astronomical",
            "naming": "celtic",
        },
    )
    assert (
        _translation_key_for(hass, entry, "next_period_change")
        == "next_period_change"
    )


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize(
    ("translation_key", "states"),
    [
        ("current_period", CROSS_QUARTER_PERIODS),
        ("current_period_celtic", CROSS_QUARTER_PERIODS),
        ("current_term", CHINESE_TERM_NAMES),
        ("current_term_pinyin", CHINESE_TERM_NAMES),
        ("current_term_hanzi", CHINESE_TERM_NAMES),
    ],
)
def test_translation_files_cover_all_enum_states(
    language, translation_key, states
) -> None:
    """Every naming translation key has a display name for every enum state."""
    data = json.loads(
        (TRANSLATIONS_DIR / f"{language}.json").read_text(encoding="utf-8")
    )
    sensor = data["entity"]["sensor"][translation_key]
    assert set(sensor["state"]) == set(states)
    assert all(sensor["state"].values())


@pytest.mark.parametrize(
    "translation_key", ["current_period_celtic", "current_term_pinyin", "current_term_hanzi"]
)
def test_language_independent_namings_are_identical_across_languages(
    translation_key,
) -> None:
    """Celtic, Pinyin and Hanzi names do not vary with the system language."""
    states = [
        json.loads(
            (TRANSLATIONS_DIR / f"{language}.json").read_text(encoding="utf-8")
        )["entity"]["sensor"][translation_key]["state"]
        for language in LANGUAGES
    ]
    assert states[0] == states[1] == states[2]
