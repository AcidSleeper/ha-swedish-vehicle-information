from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["swedish_vehicle"][entry.entry_id]
    entities = []

    for plate in coordinator.vehicles:
        entities.append(SwedishVehicleSensor(coordinator, plate))

    async_add_entities(entities)


class SwedishVehicleSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, plate: str) -> None:
        super().__init__(coordinator)
        self._plate = plate
        self._attr_name = f"Vehicle {plate}"
        self._attr_unique_id = f"swedish_vehicle_{plate}"

    @property
    def state(self):
        data = self.coordinator.data.get(self._plate, {})
        return data.get("status")  # "I trafik", "Avställd", etc.

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self._plate, {})

        return {
            "registreringsnummer": self._plate,
            "status": data.get("status"),
            "besiktad": data.get("lastInspection"),
            "besiktas_senast": data.get("nextInspection"),
            "raw_html": data.get("raw_html"),
        }
