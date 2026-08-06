from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwedishVehicleCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: SwedishVehicleCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        VehicleInfoSensor(coordinator, plate) for plate in coordinator.plates
    )


class VehicleInfoSensor(CoordinatorEntity, SensorEntity):
    """Represents a single vehicle looked up on car.info."""

    def __init__(self, coordinator: SwedishVehicleCoordinator, plate: str) -> None:
        super().__init__(coordinator)
        self._plate = plate
        self._attr_unique_id = f"{DOMAIN}_{plate}"
        self._attr_name = f"Vehicle {plate}"

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get(self._plate, {})

    @property
    def state(self):
        return self._data.get("status")

    @property
    def extra_state_attributes(self):
        data = self._data
        return {
            "registreringsnummer": self._plate,
            "i_trafik": data.get("status"),
            "besiktad": data.get("lastInspection"),
            "besiktas_senast": data.get("nextInspection"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._plate)},
            name=f"Vehicle {self._plate}",
            manufacturer="Swedish Vehicle Information",
        )
