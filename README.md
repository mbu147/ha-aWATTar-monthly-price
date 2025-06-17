# aWATTar Monthly Price for Home Assistant

This Home Assistant integration fetches the monthly energy prices (net and gross) from the aWATTar Austria website (`https://www.awattar.at/tariffs/monthly`) and provides them as sensors. It polls the aWATTar website periodically to update these prices.

## Features

*   Provides two sensor entities for Home Assistant:
    *   `sensor.awattar_monthly_net_price`: Displays the net energy price in EUR/kWh.
    *   `sensor.awattar_monthly_gross_price`: Displays the gross energy price in EUR/kWh.
*   Prices are automatically updated from the aWATTar website at a configurable interval.
*   The update interval (scan interval) can be easily configured via the integration's options in the Home Assistant UI (default is 6 hours).

## Prerequisites

*   A running Home Assistant instance.
*   [HACS (Home Assistant Community Store)](https://hacs.xyz/) is recommended for straightforward installation and updates.

## Installation

### Via HACS (Recommended Method)

1.  Ensure HACS is installed and operational in your Home Assistant setup.
2.  Navigate to **HACS > Integrations** in your Home Assistant UI.
3.  Click the three dots (vertical menu) in the top right corner and select **"Custom repositories"**.
4.  In the dialog, enter the repository URL: `https://github.com/mbu147/ha-aWATTar-monthly-price`
5.  Select **"Integration"** as the category.
6.  Click **"ADD"**.
7.  The "aWATTar Monthly Price" integration should now appear in your HACS integrations list (you might need to use the search function).
8.  Click **"INSTALL"** and follow the on-screen prompts.
9.  After installation, **restart Home Assistant** to load the integration.

### Manual Installation

1.  Download the latest release or clone the repository from `https://github.com/mbu147/ha-aWATTar-monthly-price`.
2.  Locate your Home Assistant configuration directory (this is the directory where your `configuration.yaml` file is located).
3.  If a `custom_components` directory does not exist within your configuration directory, create it.
4.  Copy the `awattar_monthly_price` directory (found within the `custom_components` folder of the downloaded/cloned repository) into the `custom_components` directory in your Home Assistant configuration.
    *   The final directory structure should be: `<config_directory>/custom_components/awattar_monthly_price/`.
5.  **Restart Home Assistant** to load the new integration.

## Configuration

Once the integration is installed and Home Assistant has been restarted:

1.  Navigate to **Settings > Devices & Services** in your Home Assistant UI.
2.  Click the **+ ADD INTEGRATION** button (typically located in the bottom right corner).
3.  Search for "aWATTar Monthly Price" and select it from the search results.
4.  The integration will be added. No further configuration fields are required during this initial setup step.

### Configuring the Update Interval

After adding the integration, you can customize how frequently it checks the aWATTar website for price updates:

1.  Go to **Settings > Devices & Services**.
2.  Find the "aWATTar Monthly Price" integration card.
3.  Click on **CONFIGURE** (or click the three-dot menu on the card and then select "Options").
4.  You will be presented with an option to set the "Scan interval in hours". Enter your desired interval (e.g., `6` for every 6 hours). The default value is 6 hours.
5.  Click **SUBMIT**. The new update interval will take effect for subsequent data fetches.

## Sensor Entities

This integration creates the following sensor entities:

*   **`sensor.awattar_monthly_net_price`**
    *   **State**: The current net energy price in EUR/kWh.
    *   **Attributes**:
        *   `price_cent_per_kwh`: The net price expressed in Cent/kWh.
*   **`sensor.awattar_monthly_gross_price`**
    *   **State**: The current gross energy price in EUR/kWh.
    *   **Attributes**:
        *   `price_cent_per_kwh`: The gross price expressed in Cent/kWh.

## Troubleshooting

*   **Check Home Assistant Logs**: If you encounter issues, the first step is to review the Home Assistant logs for any error messages related to `awattar_monthly_price` or `custom_components.awattar_monthly_price`. Logs can usually be found under Settings > System > Logs.
*   **Website Accessibility**: Verify that the aWATTar website (`https://www.awattar.at/tariffs/monthly`) is accessible from the machine or network where your Home Assistant instance is running. Network connectivity problems or changes to the website's availability can impact the integration.
*   **Re-add Integration**: In some cases, particularly after updates to Home Assistant or the integration itself, issues might be resolved by removing the integration (from Settings > Devices & Services) and then re-adding it.
*   **HACS Updates**: If you installed the integration via HACS, ensure HACS is up to date. Also, check for any available updates for the "aWATTar Monthly Price" integration within HACS.

## Contributing

Contributions, bug reports, and feature requests are highly welcome! Please feel free to open an issue or submit a pull request on the GitHub repository: `https://github.com/mbu147/ha-aWATTar-monthly-price`

## Disclaimer

This is an unofficial, third-party integration and is not affiliated with, endorsed by, or supported by aWATTar GmbH. It relies on scraping data from the publicly accessible aWATTar website. Any changes to the website's HTML structure or content may cause this integration to stop working correctly or entirely, without prior notice. Use this integration at your own risk.