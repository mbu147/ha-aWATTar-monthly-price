import logging
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.const import CONF_PLATFORM

DOMAIN = "awattar_monthly_price"

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up the aWATTar Monthly Price component."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    # Füge die Konfiguration automatisch hinzu
    config[DOMAIN] = {
        CONF_PLATFORM: "awattar_monthly_price"
    }

    await component.async_setup(config)
    return True

