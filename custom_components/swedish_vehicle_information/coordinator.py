from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .carinfo import fetch_carinfo
from .const import DOMAIN


class SwedishVehicleCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        super().__init__(
            hass,
            logger=hass.logger,
            name=DOMAIN,
            update_interval=None,
        )

    async def _async_update_data(self):
        plate = self.entry.data["plate"]
        # Viktigt: returnera EN dict, inte nested per registreringsnummer
        return await fetch_carinfo(self.hass, plate)
