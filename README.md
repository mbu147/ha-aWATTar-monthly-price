# aWATTar Monthly Price for Home Assistant

This Home Assistant integration fetches the monthly energy prices (net and gross) from the aWATTar Austria website (`https://www.awattar.at/tariffs/monthly`) and provides them as sensors.

## Features

*   Provides two sensors:
    *   `sensor.awattar_monthly_net_price`: The net energy price in EUR/kWh.
    *   `sensor.awattar_monthly_gross_price`: The gross energy price in EUR/kWh.
*   Prices are updated periodically.
*   The update interval (scan interval) can be configured via the integration's options in the Home Assistant UI.

## Installation

### Via HACS (Recommended)

1.  Ensure you have [HACS (Home Assistant Community Store)](https://hacs.xyz/) installed.
2.  Go to HACS > Integrations.
3.  Click the three dots in the top right corner and select "Custom repositories".
4.  Add the URL to this repository: `https://github.com/mbu147/ha-aWATTar-monthly-price` and select "Integration" as the category.
5.  Click "ADD".
6.  You should now be able to find "aWATTar Monthly Price" in the HACS integrations list. Click "INSTALL".
7.  Restart Home Assistant.

### Manual Installation

1.  Download the latest release or clone the repository: `https://github.com/mbu147/ha-aWATTar-monthly-price`.
2.  Copy the `custom_components/awattar_monthly_price` directory into your Home Assistant `custom_components` directory.
    *   If the `custom_components` directory doesn't exist, create it in your Home Assistant configuration directory.
3.  Restart Home Assistant.

## Configuration

1.  Go to **Settings > Devices & Services** in Home Assistant.
2.  Click the **+ ADD INTEGRATION** button in the bottom right.
3.  Search for "aWATTar Monthly Price" and select it.
4.  The integration will be added. No further configuration is required during this step.

### Configuring the Update Interval

Once the integration is added, you can configure the update interval:

1.  Go to **Settings > Devices & Services**.
2.  Find the "aWATTar Monthly Price" integration card.
3.  Click on **CONFIGURE** (or the three-dot menu and then "Options").
4.  You will see an option to set the "Scan interval in hours". Enter your desired interval (e.g., `6` for every 6 hours, default is 6).
5.  Click **SUBMIT**. The new interval will take effect.

## Sensors

The integration will create the following sensors:

*   **`sensor.awattar_monthly_net_price`**
    *   State: Current net price in EUR/kWh.
    *   Attributes:
        *   `price_cent_per_kwh`: Net price in Cent/kWh.
*   **`sensor.awattar_monthly_gross_price`**
    *   State: Current gross price in EUR/kWh.
    *   Attributes:
        *   `price_cent_per_kwh`: Gross price in Cent/kWh.

## Troubleshooting

*   Check the Home Assistant logs for any error messages related to `awattar_monthly_price` or `custom_components.awattar_monthly_price`.
*   Ensure the aWATTar website (`https://www.awattar.at/tariffs/monthly`) is accessible from your Home Assistant instance.
*   If you encounter issues after an update, try removing and re-adding the integration.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub: `https://github.com/mbu147/ha-aWATTar-monthly-price`

## Disclaimer

This integration scrapes data from the aWATTar website. Changes to the website structure may break this integration. The maintainers of this integration are not affiliated with aWATTar. Use at your own risk.