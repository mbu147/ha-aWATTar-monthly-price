import requests
from bs4 import BeautifulSoup
import logging
import functools
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.core import HomeAssistant, callback 
from homeassistant.config_entries import ConfigEntry
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed 

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)

URL = "https://www.awattar.at/tariffs/monthly"

def _clean_price_string(price_str: str, type_label: str = "") -> str:
    """Helper function to clean and prepare price string for float conversion."""
    cleaned = price_str.replace("Cent/kWh", "")
    if type_label:
        cleaned = cleaned.replace(type_label, "")
    cleaned = cleaned.replace(",", ".")
    return cleaned.strip()

async def fetch_prices(hass: HomeAssistant):
    """Scrape the aWATTar website to extract both net and gross prices."""
    _LOGGER.debug(f"Attempting to fetch prices from {URL}")
    try:
        # Create a partial function with URL and timeout already bound to requests.get
        # This ensures timeout is an argument for requests.get, not async_add_executor_job
        func_to_run = functools.partial(requests.get, URL, timeout=10)
        response = await hass.async_add_executor_job(func_to_run)
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table")
        if not tables:
            _LOGGER.warning("No HTML tables found on the aWATTar webpage.")
            return None, None

        net_price, gross_price = extract_prices(tables)

        if net_price is None and gross_price is None:
            _LOGGER.warning("Neither net nor gross price could be extracted from the webpage content.")
        elif net_price is None:
            _LOGGER.info("Net price could not be extracted, but gross price might be available.")
        elif gross_price is None:
            _LOGGER.info("Gross price could not be extracted, but net price might be available.")
        else:
            _LOGGER.debug("Successfully extracted net and gross prices.")
            
        return net_price, gross_price

    except requests.exceptions.Timeout:
        _LOGGER.warning(f"Timeout while fetching prices from {URL}. This may be a temporary issue.")
        return None, None
    except requests.exceptions.RequestException as e:
        _LOGGER.warning(f"Request error while fetching prices from {URL}: {e}. This may be a temporary issue.")
        return None, None
    except Exception as e:
        _LOGGER.error(f"Unexpected error while fetching prices: {e}", exc_info=True)
        return None, None

def extract_prices(tables):
    """
    Extract net and gross prices from the provided HTML table elements.
    Searches for a row containing "Energieverbrauchspreis".
    """
    for table_index, table in enumerate(tables):
        rows = table.find_all("tr")
        for row_index, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 3 and "Energieverbrauchspreis" in row.text:
                _LOGGER.debug(f"Found 'Energieverbrauchspreis' in table {table_index}, row {row_index}")
                raw_net_text = cells[1].get_text(strip=True)
                raw_gross_text = cells[2].get_text(strip=True)

                net_price_str = _clean_price_string(raw_net_text, "netto")
                gross_price_str = _clean_price_string(raw_gross_text, "brutto")
                
                net_price = None
                gross_price = None

                try:
                    if net_price_str:
                        net_price = float(net_price_str)
                except ValueError:
                    _LOGGER.warning(f"Could not parse net price from string: '{net_price_str}' (raw: '{raw_net_text}')")

                try:
                    if gross_price_str:
                        gross_price = float(gross_price_str)
                except ValueError:
                    _LOGGER.warning(f"Could not parse gross price from string: '{gross_price_str}' (raw: '{raw_gross_text}')")
                
                # Return as soon as prices are found
                return net_price, gross_price
                
    _LOGGER.debug("'Energieverbrauchspreis' row not found in any table.")
    return None, None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the aWATTar Monthly Price platform via config entry."""
    
    # Determine scan interval: 1. Options flow, 2. Initial config, 3. Default
    scan_interval_hours = entry.options.get(
        "scan_interval", 
        entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL_HOURS)
    )
    update_interval = timedelta(hours=scan_interval_hours)
    _LOGGER.info(f"aWATTar Monthly Price update interval set to {scan_interval_hours} hours.")

    async def async_update_data():
        """Fetch data from API. Used by DataUpdateCoordinator."""
        _LOGGER.debug("Coordinator: Attempting to fetch aWATTar monthly prices")
        net_price, gross_price = await fetch_prices(hass)
        
        if net_price is None and gross_price is None:
            # This will be logged by the coordinator as an error if it's the first failure,
            # and will prevent updates if it persists.
            raise UpdateFailed("Failed to fetch aWATTar prices: Both net and gross are unavailable after attempting to scrape.")
        
        _LOGGER.debug(f"Coordinator: Fetched prices: Net={net_price}, Gross={gross_price}")
        return {"net": net_price, "gross": gross_price}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_data_coordinator", # More specific coordinator name
        update_method=async_update_data,
        update_interval=update_interval,
    )

    # Store coordinator in hass.data for access by the options flow listener
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Add an options flow listener to update the interval when changed in UI
    entry.async_on_unload(entry.add_update_listener(async_update_options_listener))

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    # Define device_info here, to be passed to sensors
    # It's common to use the config entry's unique ID for the device identifier
    # if the integration represents a single device or service instance.
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="aWATTar Monthly Prices", # Or entry.title if you set a title
        manufacturer="aWATTar",
        model="Monthly Tariff Scraper",
        # sw_version="Your Integration Version", # You can get this from manifest.json
        # entry_type=DeviceEntryType.SERVICE, # If applicable
    )

    async_add_entities([
        AwattarMonthlyNetPriceSensor(coordinator, entry, device_info), # Pass device_info
        AwattarMonthlyGrossPriceSensor(coordinator, entry, device_info) # Pass device_info
    ])
    return True

async def async_update_options_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update from the UI."""
    _LOGGER.debug(f"Options listener called for entry {entry.entry_id}")
    # Retrieve the coordinator instance stored during setup
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if not coordinator:
        _LOGGER.error(f"Coordinator not found for entry {entry.entry_id} during options update.")
        return

    new_scan_interval_hours = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL_HOURS)
    new_update_interval = timedelta(hours=new_scan_interval_hours)
    
    if coordinator.update_interval != new_update_interval:
        coordinator.update_interval = new_update_interval
        _LOGGER.info(f"aWATTar scan interval updated to {new_scan_interval_hours} hours for entry {entry.entry_id}.")
        # Optionally, trigger an immediate refresh to apply new interval logic sooner
        # await coordinator.async_request_refresh()
    else:
        _LOGGER.debug(f"Scan interval unchanged ({new_scan_interval_hours} hours), no update to coordinator needed.")

class AwattarMonthlyPriceSensorBase(Entity):
    """Base class for aWATTar monthly price sensors."""

    # Tells Home Assistant that the entity should not be polled,
    # as the DataUpdateCoordinator handles updates.
    _attr_should_poll = False 

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry, device_info: DeviceInfo, price_type: str): # Added entry and device_info
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._price_type = price_type # "net" or "gross"
        self._attr_price_cent_per_kwh = None # Initialize attribute
        self._attr_device_info = device_info # Assign the passed device_info
        # Unique ID should be truly unique across all entities of this integration
        # Combining domain, entry_id, and price_type ensures this.
        self._attr_unique_id = f"{entry.entry_id}_{self._price_type}"


    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Available if the coordinator successfully updated and has data for this price_type
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.get(self._price_type) is not None
        )

    @property
    def state(self):
        """Return the current state of the sensor (price in EUR/kWh)."""
        if self.coordinator.data and self.coordinator.data.get(self._price_type) is not None:
            # Price is stored in cents from scraping, convert to EUR for the state
            price_in_cent = self.coordinator.data.get(self._price_type)
            return round(price_in_cent / 100, 5) # Standardize to 5 decimal places for currency
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "price_cent_per_kwh": self._attr_price_cent_per_kwh
        }

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        # This is called when the entity is added to HA.
        # It registers a listener for updates from the coordinator.
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )
        # Perform an initial update of the entity's state.
        self._handle_coordinator_update()

    @callback # Mark as a callback method
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self.coordinator.data.get(self._price_type) is not None:
            price_in_cent = self.coordinator.data.get(self._price_type)
            self._attr_price_cent_per_kwh = price_in_cent
            _LOGGER.debug(f"Sensor '{self.name}' ({self._price_type}) updated to: {self.state} EUR/kWh ({price_in_cent} cent/kWh)")
        else:
            # Data might be unavailable if parsing failed for this specific price type
            # or if the coordinator failed its last update.
            self._attr_price_cent_per_kwh = None
            _LOGGER.debug(f"Sensor '{self.name}' ({self._price_type}) data unavailable from coordinator.")
        self.async_write_ha_state()


class AwattarMonthlyNetPriceSensor(AwattarMonthlyPriceSensorBase):
    """Representation of the aWATTar monthly net price sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry, device_info: DeviceInfo): # Added entry and device_info
        """Initialize the net price sensor."""
        super().__init__(coordinator, entry, device_info, "net") # Pass entry and device_info
        self._attr_name = "aWATTar Monthly Net Price"
        # Unique ID is now set in the base class


class AwattarMonthlyGrossPriceSensor(AwattarMonthlyPriceSensorBase):
    """Representation of the aWATTar monthly gross price sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry, device_info: DeviceInfo): # Added entry and device_info
        """Initialize the gross price sensor."""
        super().__init__(coordinator, entry, device_info, "gross") # Pass entry and device_info
        self._attr_name = "aWATTar Monthly Gross Price"
        # Unique ID is now set in the base class
