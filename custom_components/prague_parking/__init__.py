"""The Prague Parking integration."""
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_PARKING_ID, DEFAULT_SCAN_INTERVAL
from .coordinator import PragueParkingCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

PARKING_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PARKING_ID): cv.string,
        vol.Optional("name"): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
                vol.Optional("parkings"): vol.All(cv.ensure_list, [PARKING_SCHEMA]),
                # Legacy single parking support
                vol.Optional(CONF_PARKING_ID): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Prague Parking component from YAML."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    api_key = conf[CONF_API_KEY]
    scan_interval = timedelta(seconds=conf.get("scan_interval", DEFAULT_SCAN_INTERVAL))

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinators"] = []
    # YAML option to enable API duration sensor
    hass.data[DOMAIN]["show_api_duration"] = bool(conf.get("show_api_duration", False))

    # Support for multiple parkings
    parkings = conf.get("parkings", [])

    # Legacy support for single parking_id
    if CONF_PARKING_ID in conf:
        parkings.append({
            CONF_PARKING_ID: conf[CONF_PARKING_ID],
            "name": None,
        })

    if not parkings:
        _LOGGER.error("No parking locations configured")
        return False

    # Create a coordinator for each parking location
    for parking_config in parkings:
        parking_id = parking_config[CONF_PARKING_ID]
        parking_name = parking_config.get("name")

        coordinator = PragueParkingCoordinator(
            hass,
            api_key=api_key,
            parking_id=parking_id,
            parking_name=parking_name,
            update_interval=scan_interval,
        )

        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN]["coordinators"].append(coordinator)

    await hass.helpers.discovery.async_load_platform(Platform.SENSOR, DOMAIN, {}, config)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Prague Parking from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    parking_id = entry.data[CONF_PARKING_ID]
    parking_name = entry.data.get("name")
    scan_interval = timedelta(seconds=entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))

    coordinator = PragueParkingCoordinator(
        hass,
        api_key=api_key,
        parking_id=parking_id,
        parking_name=parking_name,
        update_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry.

    This allows reloading the integration from the Integrations UI without
    restarting Home Assistant. Call through the Integrations page → ⋮ → Reload.
    """
    await hass.config_entries.async_reload(entry.entry_id)

