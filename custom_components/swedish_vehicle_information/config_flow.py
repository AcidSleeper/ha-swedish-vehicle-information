from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import DOMAIN


class SwedishVehicleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swedish Vehicle Information."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            reg_numbers = user_input["reg_numbers"]
            return self.async_create_entry(
                title="Swedish Vehicle Information",
                data={"reg_numbers": reg_numbers},
            )

        schema = vol.Schema(
            {
                vol.Required("reg_numbers"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return SwedishVehicleOptionsFlow(config_entry)


class SwedishVehicleOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_options()

    async def async_step_options(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={"reg_numbers": user_input["reg_numbers"]},
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "reg_numbers",
                    default=self.config_entry.data.get("reg_numbers", ""),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="options",
            data_schema=schema,
            errors=errors,
        )
