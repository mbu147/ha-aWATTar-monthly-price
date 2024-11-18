import requests
from bs4 import BeautifulSoup
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

URL = "https://www.awattar.at/tariffs/monthly"


async def fetch_prices():
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
        return net_price, gross_price

    except Exception as e:
        _LOGGER.error(f"Error while fetching prices: {e}")
        return None, None


def extract_prices(tables):
    """Extract net and gross prices from tables."""
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) >= 3 and "Energieverbrauchspreis" in row.text:
                net_price = cells[1].get_text(strip=True).replace("Cent/kWh", "").replace("netto", "").replace(",", ".").strip()
                gross_price = cells[2].get_text(strip=True).replace("brutto", "").replace("Cent/kWh", "").replace(",", ".").strip()
                return net_price, gross_price
    return None, None


async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    async_add_entities([AwattarMonthlyNetPriceSensor(), AwattarMonthlyGrossPriceSensor()])


class AwattarMonthlyNetPriceSensor(Entity):
    """Representation of the aWATTar monthly net price sensor."""

    def __init__(self):
        self._state = None
        self._name = "aWATTar Monthly Net Price"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "cent/kWh"

    async def async_update(self):
        """Fetch the latest net price and update the sensor state."""
        _LOGGER.debug("Updating monthly net price sensor...")
        net_price, _ = await fetch_prices()
        if net_price is not None:
            self._state = net_price
            _LOGGER.info(f"Net price successfully updated: {self._state} cent/kWh")
        else:
            _LOGGER.warning("Net price could not be updated.")


class AwattarMonthlyGrossPriceSensor(Entity):
    """Representation of the aWATTar monthly gross price sensor."""

    def __init__(self):
        self._state = None
        self._name = "aWATTar Monthly Gross Price"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "cent/kWh"

    async def async_update(self):
        """Fetch the latest gross price and update the sensor state."""
        _LOGGER.debug("Updating monthly gross price sensor...")
        _, gross_price = await fetch_prices()
        if gross_price is not None:
            self._state = gross_price
            _LOGGER.info(f"Gross price successfully updated: {self._state} cent/kWh")
        else:
            _LOGGER.warning("Gross price could not be updated.")

