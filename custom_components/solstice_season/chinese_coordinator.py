"""DataUpdateCoordinator for Chinese Solar Terms calendar."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .calculations import ChineseSolarTermsData, calculate_chinese_solar_terms_data
from .const import CONF_SCOPE, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Update once per day
UPDATE_INTERVAL = timedelta(days=1)


class ChineseSolarTermsCoordinator(DataUpdateCoordinator[ChineseSolarTermsData]):
    """Coordinator for Chinese Solar Terms calendar data.

    This coordinator manages data updates for all Chinese Solar Terms sensors.
    It calculates all solar term-related data once per day.
    """

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance.
            config_entry: The config entry for this integration instance.
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_chinese_solar_terms",
            update_interval=UPDATE_INTERVAL,
        )
        self.config_entry = config_entry
        self.scope: str = config_entry.data.get(CONF_SCOPE, "all_24")

    async def _async_update_data(self) -> ChineseSolarTermsData:
        """Fetch data from calculations.

        This method is called by the coordinator at the configured interval.
        It runs the calculation in an executor to avoid blocking the event loop.

        Returns:
            Dictionary containing all calculated Chinese Solar Terms data.
        """
        now = dt_util.utcnow()
        _LOGGER.debug(
            "Updating Chinese Solar Terms data for %s (scope=%s)",
            self.config_entry.title,
            self.scope,
        )

        # Run calculation in executor as it may be CPU-intensive
        return await self.hass.async_add_executor_job(
            calculate_chinese_solar_terms_data,
            self.scope,
            now,
        )
