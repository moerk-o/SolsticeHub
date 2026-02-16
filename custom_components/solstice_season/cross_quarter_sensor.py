"""Sensor platform for Cross-Quarter calendar."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .calculations import CrossQuarterData
from .const import (
    CONF_MODE,
    CONF_NAME,
    CROSS_QUARTER_ICONS,
    CROSS_QUARTER_PERIODS,
    DOMAIN,
    ICON_NEXT_PERIOD_CHANGE,
    MODE_ASTRONOMICAL,
    SENSOR_CURRENT_PERIOD,
    SENSOR_NEXT_PERIOD_CHANGE,
)
from .cross_quarter_coordinator import CrossQuarterCoordinator

# Load version from manifest.json
MANIFEST = json.loads((Path(__file__).parent / "manifest.json").read_text())
VERSION = MANIFEST["version"]


@dataclass(frozen=True, kw_only=True)
class CrossQuarterSensorEntityDescription(SensorEntityDescription):
    """Describes a Cross-Quarter sensor entity."""

    value_fn: Callable[[CrossQuarterData], Any]
    extra_state_attributes_fn: Callable[[CrossQuarterData], dict[str, Any]] | None = (
        None
    )
    icon_fn: Callable[[CrossQuarterData], str] | None = None


def get_current_period_icon(data: CrossQuarterData) -> str:
    """Get icon for current Cross-Quarter period."""
    return CROSS_QUARTER_ICONS.get(data["current_period"], "mdi:calendar")


# Cross-Quarter calendar sensor descriptions
CROSS_QUARTER_SENSOR_DESCRIPTIONS: tuple[CrossQuarterSensorEntityDescription, ...] = (
    CrossQuarterSensorEntityDescription(
        key=SENSOR_CURRENT_PERIOD,
        translation_key=SENSOR_CURRENT_PERIOD,
        device_class=SensorDeviceClass.ENUM,
        options=CROSS_QUARTER_PERIODS,
        value_fn=lambda data: data["current_period"],
        extra_state_attributes_fn=lambda data: {
            "period_age": data["period_age"],
            "events": {
                name: dt.isoformat() for name, dt in data["events"].items()
            },
        },
        icon_fn=get_current_period_icon,
    ),
    CrossQuarterSensorEntityDescription(
        key=SENSOR_NEXT_PERIOD_CHANGE,
        translation_key=SENSOR_NEXT_PERIOD_CHANGE,
        device_class=SensorDeviceClass.TIMESTAMP,
        icon=ICON_NEXT_PERIOD_CHANGE,
        value_fn=lambda data: data["next_period_change"],
        extra_state_attributes_fn=lambda data: {
            "days_until": data["days_until_next_change"],
            "event_type": data["next_period_event_type"],
        },
    ),
)


class CrossQuarterSensor(
    CoordinatorEntity[CrossQuarterCoordinator], SensorEntity
):
    """Representation of a Cross-Quarter sensor."""

    entity_description: CrossQuarterSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CrossQuarterCoordinator,
        description: CrossQuarterSensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data update coordinator.
            description: Entity description for this sensor.
            config_entry: The config entry for this integration instance.
        """
        super().__init__(coordinator)
        self.entity_description = description
        self._config_entry = config_entry

        # Set unique_id based on entry_id and sensor key
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information.

        All sensors are grouped under a single device with the user's chosen name.
        """
        mode = self._config_entry.data[CONF_MODE]
        model = (
            "Cross-Quarter (Astronomical)"
            if mode == MODE_ASTRONOMICAL
            else "Cross-Quarter (Traditional)"
        )

        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=self._config_entry.data[CONF_NAME],
            manufacturer="Solstice Season",
            model=model,
            sw_version=VERSION,
        )

    @property
    def native_value(self) -> str | datetime | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return None
        if self.entity_description.extra_state_attributes_fn is None:
            return None

        attrs = self.entity_description.extra_state_attributes_fn(self.coordinator.data)

        # Add mode to current_period sensor attributes
        if self.entity_description.key == SENSOR_CURRENT_PERIOD:
            attrs["mode"] = self._config_entry.data[CONF_MODE]

        return attrs

    @property
    def icon(self) -> str | None:
        """Return the icon for the sensor."""
        if self.entity_description.icon_fn is not None and self.coordinator.data:
            return self.entity_description.icon_fn(self.coordinator.data)
        return self.entity_description.icon
