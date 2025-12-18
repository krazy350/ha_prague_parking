"""Config flow for Prague Parking integration."""
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_PARKING_ID, API_BASE_URL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_PARKING_ID): str,
        vol.Optional("name"): str,
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=3600)
        ),
        vol.Optional("show_api_duration", default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    api_key = data[CONF_API_KEY]
    parking_id = data[CONF_PARKING_ID]

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "accept": "application/json; charset=utf-8",
                "X-Access-Token": api_key,
            }
            params = {
                "parkingId": parking_id,
                "limit": 1,
                "offset": 0,
            }

            async with session.get(
                API_BASE_URL, headers=headers, params=params, timeout=10
            ) as response:
                if response.status == 401:
                    raise InvalidAuth
                if response.status != 200:
                    raise CannotConnect

                result = await response.json()

                # API returns a list of measurements
                if not isinstance(result, list) or len(result) == 0:
                    raise InvalidParkingId

                # Get parking name from user input or API response
                parking_data = result[0]
                parking_name = data.get("name") or parking_data.get("name", "Prague Parking")

                return {"title": parking_name}

    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to Golemio API: %s", err)
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Prague Parking."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except InvalidParkingId:
                errors["base"] = "invalid_parking_id"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on parking_id
                await self.async_set_unique_id(user_input[CONF_PARKING_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    async def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class InvalidParkingId(HomeAssistantError):
    """Error to indicate the parking ID is invalid."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Prague Parking."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options
        data_schema = vol.Schema(
            {
                vol.Optional(
                    "show_api_duration", default=current.get("show_api_duration", False)
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)

