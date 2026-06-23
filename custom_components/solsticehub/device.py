"""Device naming helpers.

The device "model" string (e.g. "Four Seasons (Astronomical)") doubles as the
default instance name in the config flow, so both are derived from this single
place to keep them in sync.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .const import (
    CONF_MODE,
    CONF_SCOPE,
    DEVICE_CHINESE,
    DEVICE_CROSS_QUARTER,
    DEVICE_FOUR_SEASONS,
    MODE_ASTRONOMICAL,
    SCOPE_8_MAJOR,
)


def device_model(device_type: str, data: Mapping[str, Any]) -> str:
    """Return the human-readable model / default name for a device.

    Combines the device type with its primary distinguishing option: the
    calculation mode for Four Seasons and Cross-Quarter, the scope for Chinese.
    """
    if device_type == DEVICE_FOUR_SEASONS:
        if data.get(CONF_MODE) == MODE_ASTRONOMICAL:
            return "Four Seasons (Astronomical)"
        return "Four Seasons (Meteorological)"
    if device_type == DEVICE_CROSS_QUARTER:
        if data.get(CONF_MODE) == MODE_ASTRONOMICAL:
            return "Cross-Quarter (Astronomical)"
        return "Cross-Quarter (Traditional)"
    if device_type == DEVICE_CHINESE:
        if data.get(CONF_SCOPE) == SCOPE_8_MAJOR:
            return "Chinese Solar Terms (8 Major)"
        return "Chinese Solar Terms (All 24)"
    return device_type  # pragma: no cover - unknown device type
