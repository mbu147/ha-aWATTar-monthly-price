import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

@callback
def configured_instances(hass):
    """Return a set of configured aWATTar instances."""
    return set(entry.title for entry in hass.config_entries.async_entries(DOMAIN))

class AwattarMonthlyPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for aWATTar Monthly Price."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLLING

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            if user_input["name"] not in configured_instances(self.hass):
                return self.async_create_entry(title=user_input["name"], data=user_input)
            errors["base"] = "name_exists"

        data_schema = vol.Schema({
            vol.Required("name"): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
