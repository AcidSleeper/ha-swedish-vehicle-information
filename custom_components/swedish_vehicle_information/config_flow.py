from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class SwedishVehicleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swedish Vehicle Information."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            reg_numbers = user_input.get("reg_numbers", "").strip()

            if not reg_numbers:
                errors["reg_numbers"] = "empty"

            else:
                valid = all(
                    part.strip().replace(" ", "").isalnum()
                    for part in reg_numbers.split(",")
                )

                if not valid:
                    errors["reg_numbers"] = "invalid"
                else:
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
