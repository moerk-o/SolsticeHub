"""DataUpdateCoordinator for Cross-Quarter calendar."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .calculations import CrossQuarterData, calculate_cross_quarter_data
from .const import CONF_MODE, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _calculate_time_until_midnight() -> timedelta:
    """Calculate time until next local midnight.

    Returns:
        Timedelta until next midnight (minimum 1 minute to prevent rapid updates).
    """
    now = dt_util.now()  # Local time
    next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_until = next_midnight - now

    # Ensure minimum interval of 1 minute to prevent rapid updates
    if time_until < timedelta(minutes=1):
        time_until = timedelta(days=1)

    return time_until


class CrossQuarterCoordinator(DataUpdateCoordinator[CrossQuarterData]):
    """Coordinator for Cross-Quarter calendar data.

    This coordinator manages data updates for all Cross-Quarter sensors.
    Updates occur at local midnight for clean day transitions.
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
            name=f"{DOMAIN}_cross_quarter",
            update_interval=_calculate_time_until_midnight(),
        )
        self.config_entry = config_entry
        self.mode: str = config_entry.data[CONF_MODE]

    async def _async_update_data(self) -> CrossQuarterData:
        """Fetch data from calculations.

        This method is called by the coordinator at local midnight.
        It runs the calculation in an executor to avoid blocking the event loop.

        Returns:
            Dictionary containing all calculated Cross-Quarter data.
        """
        # Schedule next update for midnight
        self.update_interval = _calculate_time_until_midnight()

        now = dt_util.utcnow()
        _LOGGER.debug(
            "Updating Cross-Quarter data for %s (mode=%s), next update in %s",
            self.config_entry.title,
            self.mode,
            self.update_interval,
        )

        # Run calculation in executor as it may be CPU-intensive
        return await self.hass.async_add_executor_job(
            calculate_cross_quarter_data,
            self.mode,
            now,
        )
