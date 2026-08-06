from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    plate = entry.data["plate"]
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VehicleInfoSensor(coordinator, plate)])


class VehicleInfoSensor(SensorEntity):
    def __init__(self, coordinator, plate: str):
        self.coordinator = coordinator
        self._plate = plate
        self._attr_unique_id = f"{DOMAIN}_{plate}"
        self._attr_name = f"Vehicle {plate}"

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def state(self):
        return self.coordinator.data.get("status")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "registreringsnummer": self._plate,
            "status": data.get("status"),
            "besiktad": data.get("lastInspection"),
            "besiktas_senast": data.get("nextInspection"),
        }

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._plate)},
            name=f"Vehicle {self._plate}",
            manufacturer="Swedish Vehicle Information",
        )

    async def async_added_to_hass(self):
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self.coordinator.async_remove_listener(self.async_write_ha_state)
