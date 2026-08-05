from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_VEHICLES


class SwedishVehicleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="Swedish Vehicle Information",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_VEHICLES): str,  # kommaseparerade regnr
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    @callback
    def async_get_options_flow(self, config_entry):
        return SwedishVehicleOptionsFlow(config_entry)


class SwedishVehicleOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        vehicles = data.get(CONF_VEHICLES, "")

        schema = vol.Schema(
            {
                vol.Optional(CONF_VEHICLES, default=vehicles): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
