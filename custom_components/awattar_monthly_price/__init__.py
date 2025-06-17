"""The aWATTar Monthly Price integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# List of platforms that this integration will set up (in this case, only 'sensor').
PLATFORMS = ["sensor"] 

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the aWATTar Monthly Price component.
    
    This function is called by Home Assistant if the integration is configured
    in `configuration.yaml`. While this integration primarily uses UI-based
    configuration (config flow), including `async_setup` is a common pattern.
    It ensures that the `hass.data[DOMAIN]` dictionary is initialized.
    """
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.debug(f"{DOMAIN} component setup initiated.")
    return True # Return True to indicate successful setup.

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up aWATTar Monthly Price from a config entry (UI-based setup).
    
    This function is called when a config entry (created via the UI) is being set up.
    """
    _LOGGER.debug(f"Setting up config entry {entry.entry_id} for domain {DOMAIN}.")
    
    # Ensure the domain-specific dictionary exists in hass.data.
    # This dictionary can be used to store shared objects, like the DataUpdateCoordinator.
    hass.data.setdefault(DOMAIN, {}) 

    # Forward the setup of this config entry to the sensor platform.
    # This will trigger the `async_setup_entry` function in `sensor.py`.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Note: The options update listener (entry.add_update_listener) is now added 
    # within sensor.py's async_setup_entry. This is because the listener needs 
    # access to the DataUpdateCoordinator instance, which is created in sensor.py.
    
    _LOGGER.info(f"Successfully set up config entry {entry.entry_id} for {DOMAIN}.")
    return True # Return True to indicate successful setup of the config entry.

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.
    
    This function is called when the integration instance (config entry) is being removed
    or when Home Assistant is shutting down.
    """
    _LOGGER.debug(f"Unloading config entry {entry.entry_id} for domain {DOMAIN}.")
    
    # Forward the unloading process to the sensor platform.
    # This allows the sensor platform to clean up its entities and resources.
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    
    if unload_ok:
        # If unloading was successful, remove any data stored for this config entry
        # in `hass.data[DOMAIN]` to prevent memory leaks.
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info(f"Successfully unloaded config entry {entry.entry_id} for {DOMAIN}.")

    return unload_ok
