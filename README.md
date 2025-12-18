# Prague Parking Integration for Home Assistant

This custom integration provides real-time parking information for Prague parking locations using the Golemio API.

## Features

- **Available Spaces**: Shows the number of available parking spaces
- **Total Capacity**: Shows the total parking capacity
- **Occupancy Percentage**: Shows the current occupancy as a percentage

## Installation

1. Copy the `prague_parking` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Configure the integration either via UI or YAML

## Configuration

You can configure this integration in two ways:

### Option 1: UI Configuration (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Prague Parking"
4. Enter your Golemio API key and parking ID
5. Optionally provide a custom name for the parking location
6. Optionally adjust the scan interval (default: 60 seconds)
7. Repeat steps 2-6 to add multiple parking locations

To enable the optional API request duration sensor after installation:

1. Go to **Settings** → **Devices & Services** → **Integrations**
2. Locate your **Prague Parking** integration entry and click it
3. Click **Options**
4. Toggle **Show API request duration sensor** and click **Save**

### Option 2: YAML Configuration

Add the following to your `configuration.yaml`:

#### Single Parking Location (Legacy)

```yaml
prague_parking:
  api_key: YOUR_GOLEMIO_API_KEY
  parking_id: YOUR_PARKING_ID
  scan_interval: 60  # Optional, defaults to 60 seconds
```

#### Multiple Parking Locations

```yaml
prague_parking:
  api_key: YOUR_GOLEMIO_API_KEY
  scan_interval: 60  # Optional, defaults to 60 seconds
  parkings:
    - parking_id: tsk-offstreet-6b737fe9-6f24-450c-9868-819cb9377ad8
      name: "City Center Parking"
    - parking_id: tsk-offstreet-another-parking-id
      name: "Airport Parking"
    - parking_id: tsk-offstreet-yet-another-id
      name: "Shopping Mall"
```

### Configuration Variables

- **api_key** (Required): Your Golemio API access token
- **scan_interval** (Optional): Update interval in seconds (default: 60)
- **parking_id** (Optional, Legacy): Single parking location ID
- **parkings** (Optional): List of parking locations
  - **parking_id** (Required): The parking location ID
  - **name** (Optional): Custom name for the parking location
 - **show_api_duration** (Optional): Set to `true` to enable an optional sensor that reports the API request duration in milliseconds. Can be set during UI setup (Options) or in YAML.

### Example Configuration

#### Single Parking

```yaml
prague_parking:
  api_key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDAyMCwiaWF0IjoxNzYwNDI1MzMwLCJleHAiOjExNzYwNDI1MzMwLCJpc3MiOiJnb2xlbWlvIiwianRpIjoiODRhN2E1ZGYtMTcxMC00OTYyLWE1M2YtMTAxOTYyNWM1M2YzIn0.XW6gwaDkf2yFYZjQjYRvaN8MkM_dPgfaWvBTizKAlhk
  parking_id: tsk-offstreet-6b737fe9-6f24-450c-9868-819cb9377ad8
  show_api_duration: true
```

#### Multiple Parkings

```yaml
prague_parking:
  api_key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDAyMCwiaWF0IjoxNzYwNDI1MzMwLCJleHAiOjExNzYwNDI1MzMwLCJpc3MiOiJnb2xlbWlvIiwianRpIjoiODRhN2E1ZGYtMTcxMC00OTYyLWE1M2YtMTAxOTYyNWM1M2YzIn0.XW6gwaDkf2yFYZjQjYRvaN8MkM_dPgfaWvBTizKAlhk
  scan_interval: 60
  show_api_duration: true
  parkings:
    - parking_id: tsk-offstreet-6b737fe9-6f24-450c-9868-819cb9377ad8
      name: "Parking Anděl"
    - parking_id: tsk-offstreet-another-id
      name: "Parking Chodov"
```

## Sensors

The integration creates three sensors **for each parking location**:

1. **{Parking Name} Available Spaces** (e.g., `sensor.city_center_parking_available_spaces`)
   - Shows the number of available parking spaces
   - Unit: spaces

2. **{Parking Name} Total Capacity** (e.g., `sensor.city_center_parking_total_capacity`)
   - Shows the total parking capacity
   - Unit: spaces

3. **{Parking Name} Occupancy** (e.g., `sensor.city_center_parking_occupancy_percentage`)
   - Shows the occupancy percentage
   - Unit: %

4. **{Parking Name} API Request Duration** (e.g., `sensor.city_center_parking_api_request_duration_ms`) - *optional*
  - Shows the duration of the last API request to Golemio in milliseconds
  - Unit: ms

**Note:** The parking name in the sensor entity is based on:
- The custom `name` you provide in the configuration, or
- The parking name from the Golemio API, or
- The `parking_id` if no name is available

### Sensor Attributes

Each sensor includes the following attributes:
- `parking_id`: The parking location ID
- `parking_name`: The name of the parking location
- `address`: The street address of the parking location
- `last_updated`: Timestamp of the last data update

## Getting a Golemio API Key

1. Visit [https://api.golemio.cz/api-keys](https://api.golemio.cz/api-keys)
2. Register for a free API key
3. Use the provided access token in your configuration

## Finding Parking IDs

You can find parking IDs by querying the Golemio API:
```bash
curl -X 'GET' \
  'https://api.golemio.cz/v3/parkings' \
  -H 'accept: application/json' \
  -H 'X-Access-Token: YOUR_API_KEY'
```

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/krazy350/ha_prague_parking).

