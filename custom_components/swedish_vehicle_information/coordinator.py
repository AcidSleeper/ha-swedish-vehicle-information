import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api.carinfo import fetch_carinfo
from .const import CONF_REG_NUMBERS, DEFAULT_SCAN_INTERVAL_DAYS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SwedishVehicleCoordinator(DataUpdateCoordinator):
    """Fetches car.info data for every configured registration number."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.plates = [
            plate.strip().upper().replace(" ", "")
            for plate in entry.data[CONF_REG_NUMBERS].split(",")
            if plate.strip()
        ]

        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(days=DEFAULT_SCAN_INTERVAL_DAYS),
        )

    async def _async_update_data(self) -> dict:
        """Return a dict keyed by plate: {"ABC123": {...}, "DEF456": {...}}."""
        data = {}
        for plate in self.plates:
            data[plate] = await fetch_carinfo(self.hass, plate)
        return data