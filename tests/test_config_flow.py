"""Tests for the SolsticeHub config flow.

Covers the entry step (device type only) and each device-specific step
(four_seasons, cross_quarter, chinese). The instance name is no longer asked
in the flow; it defaults to the device type label and is set by the user in
Home Assistant's standard final step.
"""

import sys
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from solsticehub.const import (  # noqa: E402
    CONF_DEVICE_TYPE,
    CONF_HEMISPHERE,
    CONF_MODE,
    CONF_NAME,
    CONF_NAMING,
    CONF_SCOPE,
    DEVICE_CHINESE,
    DEVICE_CROSS_QUARTER,
    DEVICE_FOUR_SEASONS,
    DOMAIN,
)
from solsticehub.device import device_model  # noqa: E402


async def _start(hass: HomeAssistant, device_type: str):
    """Run the first step (device type only) and return the resulting flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    return await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_TYPE: device_type},
    )


def test_device_model_labels() -> None:
    """device_model maps each type + option to its 'Type (Mode)' label."""
    assert (
        device_model(DEVICE_FOUR_SEASONS, {CONF_MODE: "astronomical"})
        == "Four Seasons (Astronomical)"
    )
    assert (
        device_model(DEVICE_FOUR_SEASONS, {CONF_MODE: "meteorological"})
        == "Four Seasons (Meteorological)"
    )
    assert (
        device_model(DEVICE_CROSS_QUARTER, {CONF_MODE: "astronomical"})
        == "Cross-Quarter (Astronomical)"
    )
    assert (
        device_model(DEVICE_CROSS_QUARTER, {CONF_MODE: "traditional"})
        == "Cross-Quarter (Traditional)"
    )
    assert (
        device_model(DEVICE_CHINESE, {CONF_SCOPE: "all_24"})
        == "Chinese Solar Terms (All 24)"
    )
    assert (
        device_model(DEVICE_CHINESE, {CONF_SCOPE: "8_major"})
        == "Chinese Solar Terms (8 Major)"
    )


async def test_first_step_has_no_name_field(hass: HomeAssistant) -> None:
    """The first step asks only for the device type, not a name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    schema_keys = {str(key.schema) for key in result["data_schema"].schema}
    assert schema_keys == {CONF_DEVICE_TYPE}


async def test_four_seasons_flow(hass: HomeAssistant) -> None:
    """Full four_seasons flow creates an entry with the right data."""
    result = await _start(hass, DEVICE_FOUR_SEASONS)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "four_seasons"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HEMISPHERE: "northern", CONF_MODE: "astronomical"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Four Seasons (Astronomical)"
    assert result["data"] == {
        CONF_NAME: "Four Seasons (Astronomical)",
        CONF_DEVICE_TYPE: DEVICE_FOUR_SEASONS,
        CONF_HEMISPHERE: "northern",
        CONF_MODE: "astronomical",
    }


async def test_cross_quarter_flow(hass: HomeAssistant) -> None:
    """Cross-quarter flow creates an entry and forces northern hemisphere."""
    result = await _start(hass, DEVICE_CROSS_QUARTER)
    assert result["step_id"] == "cross_quarter"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_MODE: "traditional", CONF_NAMING: "celtic"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Cross-Quarter (Traditional)"
    assert result["data"][CONF_DEVICE_TYPE] == DEVICE_CROSS_QUARTER
    assert result["data"][CONF_MODE] == "traditional"
    assert result["data"][CONF_NAMING] == "celtic"
    assert result["data"][CONF_HEMISPHERE] == "northern"


async def test_chinese_flow(hass: HomeAssistant) -> None:
    """Chinese flow creates an entry with scope and naming."""
    result = await _start(hass, DEVICE_CHINESE)
    assert result["step_id"] == "chinese"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_SCOPE: "8_major", CONF_NAMING: "pinyin"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Chinese Solar Terms (8 Major)"
    assert result["data"][CONF_DEVICE_TYPE] == DEVICE_CHINESE
    assert result["data"][CONF_SCOPE] == "8_major"
    assert result["data"][CONF_NAMING] == "pinyin"
    assert result["data"][CONF_HEMISPHERE] == "northern"


async def test_multiple_instances_allowed(hass: HomeAssistant) -> None:
    """Without a name field there is no duplicate check; a second identical
    instance can be created (the user names devices in the final step)."""
    result = await _start(hass, DEVICE_FOUR_SEASONS)
    first = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HEMISPHERE: "northern", CONF_MODE: "astronomical"},
    )
    assert first["type"] == FlowResultType.CREATE_ENTRY

    result = await _start(hass, DEVICE_FOUR_SEASONS)
    second = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HEMISPHERE: "northern", CONF_MODE: "astronomical"},
    )
    assert second["type"] == FlowResultType.CREATE_ENTRY


async def test_default_hemisphere_from_location(hass: HomeAssistant) -> None:
    """The four_seasons step pre-fills hemisphere from the HA latitude."""
    hass.config.latitude = -33.0  # Southern
    result = await _start(hass, DEVICE_FOUR_SEASONS)
    schema = result["data_schema"].schema
    hemisphere_default = next(
        key.default() for key in schema if getattr(key, "schema", None) == CONF_HEMISPHERE
    )
    assert hemisphere_default == "southern"
