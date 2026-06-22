"""Tests for the SolsticeHub config flow.

Covers the entry step (name + device type) and each device-specific step
(four_seasons, cross_quarter, chinese), plus duplicate prevention.
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


async def _start(hass: HomeAssistant, name: str, device_type: str):
    """Run the first step and return the resulting flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    return await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: name, CONF_DEVICE_TYPE: device_type},
    )


async def test_four_seasons_flow(hass: HomeAssistant) -> None:
    """Full four_seasons flow creates an entry with the right data."""
    result = await _start(hass, "Home", DEVICE_FOUR_SEASONS)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "four_seasons"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HEMISPHERE: "northern", CONF_MODE: "astronomical"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Home"
    assert result["data"] == {
        CONF_NAME: "Home",
        CONF_DEVICE_TYPE: DEVICE_FOUR_SEASONS,
        CONF_HEMISPHERE: "northern",
        CONF_MODE: "astronomical",
    }


async def test_cross_quarter_flow(hass: HomeAssistant) -> None:
    """Cross-quarter flow creates an entry and forces northern hemisphere."""
    result = await _start(hass, "Wheel", DEVICE_CROSS_QUARTER)
    assert result["step_id"] == "cross_quarter"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_MODE: "traditional", CONF_NAMING: "celtic"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_DEVICE_TYPE] == DEVICE_CROSS_QUARTER
    assert result["data"][CONF_MODE] == "traditional"
    assert result["data"][CONF_NAMING] == "celtic"
    assert result["data"][CONF_HEMISPHERE] == "northern"


async def test_chinese_flow(hass: HomeAssistant) -> None:
    """Chinese flow creates an entry with scope and naming."""
    result = await _start(hass, "Terms", DEVICE_CHINESE)
    assert result["step_id"] == "chinese"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_SCOPE: "8_major", CONF_NAMING: "pinyin"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_DEVICE_TYPE] == DEVICE_CHINESE
    assert result["data"][CONF_SCOPE] == "8_major"
    assert result["data"][CONF_NAMING] == "pinyin"
    assert result["data"][CONF_HEMISPHERE] == "northern"


async def test_duplicate_name_aborts(hass: HomeAssistant) -> None:
    """A second entry with the same (slugified) name aborts."""
    result = await _start(hass, "Home", DEVICE_FOUR_SEASONS)
    await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HEMISPHERE: "northern", CONF_MODE: "astronomical"},
    )

    # Second flow with the same name must abort on the first step.
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Home", CONF_DEVICE_TYPE: DEVICE_FOUR_SEASONS},
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_default_hemisphere_from_location(hass: HomeAssistant) -> None:
    """The four_seasons step pre-fills hemisphere from the HA latitude."""
    hass.config.latitude = -33.0  # Southern
    result = await _start(hass, "Down Under", DEVICE_FOUR_SEASONS)
    schema = result["data_schema"].schema
    hemisphere_default = next(
        key.default() for key in schema if getattr(key, "schema", None) == CONF_HEMISPHERE
    )
    assert hemisphere_default == "southern"
