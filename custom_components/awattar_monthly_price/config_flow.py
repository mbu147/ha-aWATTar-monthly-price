import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.schema_config_entry_flow import SchemaFlowFormStep, SchemaOptionsFlowHandler

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_HOURS

# Schema for the initial setup (if you need any user input at setup)
# For this sensor, it might not need any initial user input if the URL is fixed.
CONFIG_SCHEMA = vol.Schema({
    # vol.Optional("some_initial_config", default=""): str, # Example
})

# Schema for the options flow
OPTIONS_SCHEMA = vol.Schema({
    vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL_HOURS): vol.All(vol.Coerce(int), vol.Range(min=1)),
})

class AwattarMonthlyPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for aWATTar Monthly Price."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Here you would normally validate and store user_input if you had any
            # For this sensor, we might not have initial config, so we just create the entry
            return self.async_create_entry(title="aWATTar Monthly Price", data=user_input or {})

        # If no user input is needed for initial setup, you can show an empty form
        # or directly create the entry.
        # For simplicity, let's assume no initial input is needed.
        # If you already have instances, you might want to prevent creating more.
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        
        return self.async_show_form(
            step_id="user",
            # data_schema=CONFIG_SCHEMA, # Use if you have initial config options
            # For no initial options, you can omit data_schema or use an empty schema
        )


    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> SchemaOptionsFlowHandler:
        """Get the options flow for this handler."""
        # Define the options flow steps as a dictionary.
        # The key "init" is standard for the first or only step.
        options_flow_steps = {
            "init": SchemaFlowFormStep(OPTIONS_SCHEMA)
        }
        return SchemaOptionsFlowHandler(config_entry, options_flow_steps)
