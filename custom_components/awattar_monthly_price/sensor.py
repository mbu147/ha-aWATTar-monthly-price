import requests
from bs4 import BeautifulSoup
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed 

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_HOURS # Assuming you'll create a const.py

_LOGGER = logging.getLogger(__name__)

URL = "https://www.awattar.at/tariffs/monthly"
# DEFAULT_SCAN_INTERVAL_HOURS will now come from const.py or be managed by config flow
# SCAN_INTERVAL will be determined dynamically in async_setup_entry

async def fetch_prices(hass: HomeAssistant):
    """Scrape the aWATTar website to extract both net and gross prices."""
    try:
        response = await hass.async_add_executor_job(requests.get, URL, {"timeout": 10})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table")
        if not tables:
            _LOGGER.error("No table found on the webpage.")
            return None, None

        net_price, gross_price = extract_prices(tables)
        if net_price is None or gross_price is None:
            _LOGGER.error("Net and/or gross prices not found.")
            # Still return what we have, one might be valid
        return net_price, gross_price

    except requests.exceptions.Timeout:
        _LOGGER.error(f"Timeout while fetching prices from {URL}")
        return None, None
    except requests.exceptions.RequestException as e:
        _LOGGER.error(f"Error while fetching prices: {e}")
        return None, None
    except Exception as e:
        _LOGGER.error(f"Unexpected error while fetching prices: {e}")
        return None, None

def extract_prices(tables):
    """Extract net and gross prices from tables."""
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) >= 3 and "Energieverbrauchspreis" in row.text:
                net_price_str = cells[1].get_text(strip=True).replace("Cent/kWh", "").replace("netto", "").replace(",", ".").strip()
                gross_price_str = cells[2].get_text(strip=True).replace("brutto", "").replace("Cent/kWh", "").replace(",", ".").strip()
                
                net_price = None
                gross_price = None

                try:
                    if net_price_str:
                        net_price = float(net_price_str)
                except ValueError:
                    _LOGGER.warning(f"Could not parse net price: {net_price_str}")

                try:
                    if gross_price_str:
                        gross_price = float(gross_price_str)
                except ValueError:
                    _LOGGER.warning(f"Could not parse gross price: {gross_price_str}")
                
                return net_price, gross_price
    return None, None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the aWATTar Monthly Price platform via config entry."""
    
    # Get scan interval from options, or from data (if set during initial setup), or default
    scan_interval_hours = entry.options.get(
        "scan_interval", 
        entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL_HOURS)
    )
    update_interval = timedelta(hours=scan_interval_hours)

    async def async_update_data():
        """Fetch data from API."""
        net_price, gross_price = await fetch_prices(hass)
        if net_price is None and gross_price is None: # Only raise if both are None
            raise UpdateFailed("Failed to fetch prices, both net and gross are unavailable.")
        return {"net": net_price, "gross": gross_price}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="awattar_monthly_price",
        update_method=async_update_data,
        update_interval=update_interval, # Use the configured interval
    )

    # Store coordinator for access in options flow
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Add an options flow listener
    entry.async_on_unload(entry.add_update_listener(async_update_options_listener))

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        AwattarMonthlyNetPriceSensor(coordinator),
        AwattarMonthlyGrossPriceSensor(coordinator)
    ])
    return True

async def async_update_options_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    # This is called when options are updated via the UI.
    # We need to update the coordinator's interval.
    coordinator = hass.data[DOMAIN][entry.entry_id]
    new_scan_interval_hours = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL_HOURS)
    coordinator.update_interval = timedelta(hours=new_scan_interval_hours)
    _LOGGER.info(f"aWATTar scan interval updated to {new_scan_interval_hours} hours.")
    # You might want to trigger an immediate refresh or let the next scheduled update run
    # await coordinator.async_request_refresh() 

class AwattarMonthlyPriceSensorBase(Entity):
    """Base class for aWATTar monthly price sensors."""

    def __init__(self, coordinator: DataUpdateCoordinator, price_type: str):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._price_type = price_type # "net" or "gross"
        self._attr_price_cent_per_kwh = None

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and \
               self.coordinator.data is not None and \
               self.coordinator.data.get(self._price_type) is not None

    @property
    def state(self):
        """Return the current state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get(self._price_type) is not None:
            return self.coordinator.data.get(self._price_type) / 100 # Convert cent to EUR
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "EUR/kWh" # Changed to uppercase EUR

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "price_cent_per_kwh": self._attr_price_cent_per_kwh
        }

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )
        # Initial update
        self._handle_coordinator_update()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self.coordinator.data.get(self._price_type) is not None:
            price_in_cent = self.coordinator.data.get(self._price_type)
            self._attr_price_cent_per_kwh = price_in_cent
            _LOGGER.debug(f"{self.name} updated to: {price_in_cent / 100} EUR/kWh ({price_in_cent} cent/kWh)")
        else:
            self._attr_price_cent_per_kwh = None
            _LOGGER.debug(f"{self.name} data unavailable from coordinator.")
        self.async_write_ha_state()


class AwattarMonthlyNetPriceSensor(AwattarMonthlyPriceSensorBase):
    """Representation of the aWATTar monthly net price sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator):
        """Initialize the net price sensor."""
        super().__init__(coordinator, "net")
        self._attr_name = "aWATTar Monthly Net Price"
        self._attr_unique_id = "awattar_monthly_net_price"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._attr_unique_id


class AwattarMonthlyGrossPriceSensor(AwattarMonthlyPriceSensorBase):
    """Representation of the aWATTar monthly gross price sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator):
        """Initialize the gross price sensor."""
        super().__init__(coordinator, "gross")
        self._attr_name = "aWATTar Monthly Gross Price"
        self._attr_unique_id = "awattar_monthly_gross_price"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._attr_unique_id

# Remove async_setup_platform if it's no longer used or adapt if still needed for YAML config
# For config flow based setup, async_setup_platform is often not required.
# If you still support YAML configuration that uses async_setup_platform,
# you would need to adapt it to also use the coordinator or a similar mechanism.
# For simplicity, assuming config entry is the primary setup method.
# async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
#     """Set up the sensor platform."""
#     # This would need to be adapted if you want to keep YAML support
#     # For now, we assume setup via UI (ConfigEntry)
#     pass
