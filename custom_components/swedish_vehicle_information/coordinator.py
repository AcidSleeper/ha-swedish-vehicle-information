from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_VEHICLES, DEFAULT_SCAN_INTERVAL_DAYS
from .api.transportstyrelsen import fetch_ts
from .api.fordonsuppgifter import fetch_fu
from .api.biluppgifter import fetch_bu


async def safe_fetch(fetch_func, plate: str) -> dict:
    try:
        return await fetch_func(plate)
    except Exception:
        return {}


def merge_data(ts: dict, fu: dict, bu: dict, plate: str) -> dict:
    status = (
        ts.get("status")
        or fu.get("status")
        or bu.get("status")
    )

    last_inspection = (
        ts.get("lastInspection")
        or fu.get("inspection", {}).get("last")
        or bu.get("inspection", {}).get("last")
    )

    next_inspection = (
        ts.get("nextInspection")
        or fu.get("inspection", {}).get("next")
        or bu.get("inspection", {}).get("next")
    )

    tax = ts.get("tax") or fu.get("tax") or bu.get("tax")
    owner = fu.get("owner") or bu.get("owner")
    vehicle_type = fu.get("type") or bu.get("type")

    return {
        "plate": plate,
        "status": status,
        "last_inspection": last_inspection,
        "next_inspection": next_inspection,
        "tax": tax,
        "owner": owner,
        "vehicle_type": vehicle_type,
        "raw": {
            "transportstyrelsen": ts,
            "fordonsuppgifter": fu,
            "biluppgifter": bu,
        },
    }


def calculate_interval(next_inspection: str | None) -> timedelta:
    if not next_inspection:
        return timedelta(days=DEFAULT_SCAN_INTERVAL_DAYS)

    try:
        next_date = datetime.fromisoformat(next_inspection)
    except ValueError:
        return timedelta(days=DEFAULT_SCAN_INTERVAL_DAYS)

    days_left = (next_date - datetime.now()).days

    if days_left <= 14:
        return timedelta(days=1)
    else:
        return timedelta(days=7)


class SwedishVehicleCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, vehicles: list[str]) -> None:
        super().__init__(
            hass,
            logger=hass.logger,
            name="Swedish Vehicle Information",
            update_interval=timedelta(days=DEFAULT_SCAN_INTERVAL_DAYS),
        )
        self.vehicles = vehicles

    async def _async_update_data(self) -> dict[str, Any]:
        data: dict[str, Any] = {}

        try:
            for plate in self.vehicles:
                ts = await safe_fetch(fetch_ts, plate)
                fu = await safe_fetch(fetch_fu, plate)
                bu = await safe_fetch(fetch_bu, plate)

                merged = merge_data(ts, fu, bu, plate)
                data[plate] = merged

            # Dynamisk intervall baserat på första fordonet
            if data:
                first = next(iter(data.values()))
                interval = calculate_interval(first.get("next_inspection"))
                self.update_interval = interval

            return data
        except Exception as err:
            raise UpdateFailed(f"Error updating vehicle data: {err}") from err
