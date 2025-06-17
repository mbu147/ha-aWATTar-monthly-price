"""The aWATTar Monthly Price integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
# Assuming your sensor setup is in sensor.py
PLATFORMS = ["sensor"] 

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the aWATTar Monthly Price component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up aWATTar Monthly Price from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Add an options flow listener
    # This is now handled in sensor.py's async_setup_entry to have access to the coordinator
    # entry.async_on_unload(entry.add_update_listener(options_update_listener))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Forward the unload to the sensor platform.
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None) # Clean up coordinator if stored

    return unload_ok

# This listener is now better placed in sensor.py where coordinator is accessible
# async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry):
#     """Handle options update."""
#     # This is called when options are updated via the UI.
#     # You might need to reload the entry or update the coordinator directly.
#     # For simplicity, a reload is often easiest if the coordinator isn't easily accessible here.
#     await hass.config_entries.async_reload(entry.entry_id)
