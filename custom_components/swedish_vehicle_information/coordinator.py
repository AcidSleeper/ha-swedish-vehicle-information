from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL_DAYS, DOMAIN
from .api.carinfo import fetch_carinfo

LOGGER = logging.getLogger(__name__)


class SwedishVehicleCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry) -> None:
        super().__init__(
            hass,
            logger=LOGGER,
            name="Swedish Vehicle Information",
            update_interval=timedelta(days=DEFAULT_SCAN_INTERVAL_DAYS),
        )

        self.hass = hass
        self.entry = entry
        self.vehicles = [
            v.strip().upper()
            for v in entry.data["reg_numbers"].split(",")
            if v.strip()
        ]

    async def _async_update_data(self):
        plate = self.entry.data["plate"]
        return await fetch_carinfo(self.hass, plate)

        try:
            for plate in self.vehicles:
                ci = await fetch_carinfo(self.hass, plate)
                data[plate] = ci

            return data

        except Exception as err:
            raise UpdateFailed(f"Error updating vehicle data: {err}") from err
