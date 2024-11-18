# aWATTar Monthly Price

A Home Assistant integration that fetches monthly energy prices from aWATTar and provides them as sensors.

## Installation

### Installation via HACS

1. **Install HACS**: If you haven't already, install HACS (Home Assistant Community Store) following the instructions on the [HACS website](https://hacs.xyz/).

2. **Add the integration**: Open HACS in Home Assistant and navigate to "Integrations". Click the "+" button and then "Custom repositories".

3. **Add the repository URL**: Add the URL of this repository (`https://github.com/mbu147/ha-aWATTar-monthly-price`) and select the type `Integration`.

4. **Complete the installation**: After adding the repository, you will find it under HACS integrations. Install the integration.

5. **Add the configuration**: Add the following line to your `configuration.yaml`:
   ```yaml
   sensor:
     - platform: awattar_monthly_price
   ```

6. **Restart Home Assistant**: Restart Home Assistant to load the integration.

### Manual Installation

1. **Download the files**: Download all the files from this repository and place them in a new directory `custom_components/awattar_monthly_price` in your Home Assistant configuration directory.

2. **Add the configuration**: Add the following line to your `configuration.yaml`:
   ```yaml
   sensor:
     - platform: awattar_monthly_price
   ```

3. **Install dependencies**: Ensure you have the required dependencies installed:
   ```sh
   pip install beautifulsoup4
   ```

4. **Restart Home Assistant**: Restart Home Assistant to load the integration.

## Usage

After installation and configuration, the integration will add two sensors:
- `sensor.awattar_monthly_net_price`: Shows the monthly net price in cents/kWh.
- `sensor.awattar_monthly_gross_price`: Shows the monthly gross price in cents/kWh.

These sensors will automatically appear in your Home Assistant interface and update regularly.