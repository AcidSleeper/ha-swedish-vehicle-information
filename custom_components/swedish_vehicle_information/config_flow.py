from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_REG_NUMBERS, DOMAIN


class SwedishVehicleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swedish Vehicle Information."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            raw = user_input.get(CONF_REG_NUMBERS, "").strip()

            if not raw:
                errors[CONF_REG_NUMBERS] = "empty"
            else:
                plates = [p.strip() for p in raw.split(",") if p.strip()]
                valid = bool(plates) and all(
                    p.replace(" ", "").isalnum() for p in plates
                )

                if not valid:
                    errors[CONF_REG_NUMBERS] = "invalid"
                else:
                    return self.async_create_entry(
                        title="Swedish Vehicle Information",
                        data={CONF_REG_NUMBERS: ", ".join(plates)},
                    )

        schema = vol.Schema({vol.Required(CONF_REG_NUMBERS): str})

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )