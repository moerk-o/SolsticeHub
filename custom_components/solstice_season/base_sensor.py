"""Base Data sensors for Solstice Season integration.

Sensors:
- solar_longitude: Ecliptic longitude of the Sun (diagnostic, disabled by default)
- daylight_trend: Whether days are getting longer or shorter
- next_daylight_trend_change: Timestamp of the next solstice
"""

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
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEGREE, EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .base_data_coordinator import BaseDataCoordinator
from .calculations import BaseData
from .const import (
    CONF_NAME,
    DOMAIN,
    ICON_NEXT_TREND_CHANGE,
    ICON_SOLAR_LONGITUDE,
    SENSOR_DAYLIGHT_TREND,
    SENSOR_NEXT_TREND_CHANGE,
    SENSOR_SOLAR_LONGITUDE,
    TREND_ICONS,
)

# Load version from manifest.json
MANIFEST = json.loads((Path(__file__).parent / "manifest.json").read_text())
VERSION = MANIFEST["version"]


@dataclass(frozen=True, kw_only=True)
class BaseSensorEntityDescription(SensorEntityDescription):
    """Describes a Base Data sensor entity."""

    value_fn: Callable[[BaseData], Any]
    extra_state_attributes_fn: Callable[[BaseData], dict[str, Any]] | None = None
    icon_fn: Callable[[BaseData], str] | None = None


def get_daylight_trend_icon(data: BaseData) -> str:
    """Get icon for daylight trend."""
    return TREND_ICONS.get(data["daylight_trend"], "mdi:arrow-left-right")


BASE_SENSOR_DESCRIPTIONS: tuple[BaseSensorEntityDescription, ...] = (
    BaseSensorEntityDescription(
        key=SENSOR_SOLAR_LONGITUDE,
        translation_key=SENSOR_SOLAR_LONGITUDE,
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon=ICON_SOLAR_LONGITUDE,
        value_fn=lambda data: data["solar_longitude"],
    ),
    BaseSensorEntityDescription(
        key=SENSOR_DAYLIGHT_TREND,
        translation_key=SENSOR_DAYLIGHT_TREND,
        device_class=SensorDeviceClass.ENUM,
        options=["days_getting_longer", "days_getting_shorter", "solstice_today"],
        value_fn=lambda data: data["daylight_trend"],
        icon_fn=get_daylight_trend_icon,
    ),
    BaseSensorEntityDescription(
        key=SENSOR_NEXT_TREND_CHANGE,
        translation_key=SENSOR_NEXT_TREND_CHANGE,
        device_class=SensorDeviceClass.TIMESTAMP,
        icon=ICON_NEXT_TREND_CHANGE,
        value_fn=lambda data: data["next_trend_change"],
        extra_state_attributes_fn=lambda data: {
            "days_until": data["days_until_trend_change"],
            "event_type": data["next_trend_event_type"],
        },
    ),
)


class BaseDataSensor(
    CoordinatorEntity[BaseDataCoordinator], SensorEntity
):
    """Representation of a Base Data sensor."""

    entity_description: BaseSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BaseDataCoordinator,
        description: BaseSensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the base data sensor.

        Args:
            coordinator: The base data update coordinator.
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
        """Return device information for the Base Data device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=self._config_entry.data[CONF_NAME],
            manufacturer="Solstice Season",
            model="Base Data",
            sw_version=VERSION,
        )

    @property
    def native_value(self) -> str | float | datetime | None:
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
        return self.entity_description.extra_state_attributes_fn(self.coordinator.data)

    @property
    def icon(self) -> str | None:
        """Return the icon for the sensor."""
        if self.entity_description.icon_fn is not None and self.coordinator.data:
            return self.entity_description.icon_fn(self.coordinator.data)
        return self.entity_description.icon
