"""Constants for the aWATTar Monthly Price integration.

This file defines static values used throughout the integration
to ensure consistency and ease of maintenance.
"""

# The domain of the integration, used as a unique identifier within Home Assistant.
# It's also used for namespacing logs, services, and hass.data entries.
DOMAIN = "awattar_monthly_price"

# Default scan interval in hours for the DataUpdateCoordinator.
# This value is used if the user does not configure a custom interval
# via the integration's options flow.
DEFAULT_SCAN_INTERVAL_HOURS = 6
