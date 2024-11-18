from homeassistant import config_entries
from .const import DOMAIN

class AwattarMonthlyPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for aWATTar Monthly Price."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Automatically create the entry without user input
        return self.async_create_entry(title="aWATTar Monthly Price", data={})
