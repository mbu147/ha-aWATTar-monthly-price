import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.schema_config_entry_flow import SchemaFlowFormStep, SchemaOptionsFlowHandler

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_HOURS

# Schema for the initial setup (user step).
# This integration does not require any user input during the initial setup phase,
# as the target URL is fixed and there are no API keys or similar to configure.
# If future versions needed initial parameters, they would be defined here.
# Example:
# INITIAL_SETUP_SCHEMA = vol.Schema({
#     vol.Required("api_key"): str,
# })
INITIAL_SETUP_SCHEMA = vol.Schema({}) # No initial configuration options needed

# Schema for the options flow (accessed via "CONFIGURE" on the integration card).
# This allows users to customize settings after the initial setup.
OPTIONS_SCHEMA = vol.Schema({
    vol.Required(
        "scan_interval", 
        default=DEFAULT_SCAN_INTERVAL_HOURS # Default value from const.py
    ): vol.All(vol.Coerce(int), vol.Range(min=1)), # Ensures the interval is a positive integer
})

class AwattarMonthlyPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for aWATTar Monthly Price."""

    VERSION = 1 # Schema version, used for migrations if the config entry data structure changes.

    async def async_step_user(self, user_input=None):
        """Handle the initial user setup step.
        
        This step is invoked when the user adds the integration through the UI.
        """
        # Prevent multiple instances of this integration if it's designed to be a singleton.
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # This block is executed if the user has submitted the form.
            # Since INITIAL_SETUP_SCHEMA is empty, user_input will typically be an empty dictionary.
            # We create the config entry with an empty data dictionary, as no specific
            # configuration data is gathered at this stage.
            return self.async_create_entry(title="aWATTar Monthly Price", data={})

        # Show the form to the user.
        # Because INITIAL_SETUP_SCHEMA is empty, this will present a simple confirmation step
        # without any fields to fill in.
        return self.async_show_form(
            step_id="user",
            data_schema=INITIAL_SETUP_SCHEMA # Pass the (empty) schema for the form
            # errors={} # Placeholder for future validation errors, if any
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> SchemaOptionsFlowHandler:
        """Get the options flow for this handler.
        
        This method is called by Home Assistant when the user clicks "CONFIGURE" 
        on an already set up integration instance.
        """
        # Define the steps for the options flow.
        # For a single configuration screen in the options flow, 
        # "init" is the standard key for the first (and only) step.
        options_flow_steps = {
            "init": SchemaFlowFormStep(OPTIONS_SCHEMA) # Use the OPTIONS_SCHEMA for the form fields
        }
        return SchemaOptionsFlowHandler(config_entry, options_flow_steps)
