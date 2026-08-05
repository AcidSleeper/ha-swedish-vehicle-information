from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    vehicles = data["vehicles"]

    entities: list[SensorEntity] = [
        VehicleSensor(coordinator, plate) for plate in vehicles
    ]

    async_add_entities(entities)


class VehicleSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, plate: str) -> None:
        super().__init__(coordinator)
        self._plate = plate

    @property
    def name(self) -> str:
        return f"{self._plate} Vehicle Information"

    @property
    def unique_id(self) -> str:
        return f"svinfo_{self._plate}"

    @property
    def state(self) -> str | None:
        d = self.coordinator.data.get(self._plate, {})
        return d.get("status")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data.get(self._plate, {})
        raw = d.get("raw", {})
        return {
            "plate": d.get("plate"),
            "status": d.get("status"),
            "last_inspection": d.get("last_inspection"),
            "next_inspection": d.get("next_inspection"),
            "tax": d.get("tax"),
            "owner": d.get("owner"),
            "vehicle_type": d.get("vehicle_type"),
            "transportstyrelsen": raw.get("transportstyrelsen"),
            "biluppgifter": raw.get("biluppgifter"),
        }
