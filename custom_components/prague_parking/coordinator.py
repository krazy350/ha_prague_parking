"""DataUpdateCoordinator for Prague Parking."""
import logging
import time
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PragueParkingCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Prague Parking data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        parking_id: str,
        parking_name: str | None = None,
        update_interval: timedelta = timedelta(seconds=60),
    ) -> None:
        """Initialize."""
        self.api_key = api_key
        self.parking_id = parking_id
        self.parking_name = parking_name

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{parking_id}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "accept": "application/json; charset=utf-8",
                    "X-Access-Token": self.api_key,
                }
                params = {
                    "parkingId": self.parking_id,
                    "limit": 1,
                    "offset": 0,
                }

                start = time.perf_counter()
                async with session.get(
                    API_BASE_URL, headers=headers, params=params, timeout=10
                ) as response:
                    duration_ms = int((time.perf_counter() - start) * 1000)
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching data: %s (request duration: %sms)",
                            response.status,
                            duration_ms,
                        )
                        raise UpdateFailed(f"Error fetching data: {response.status}")

                    data = await response.json()

                    # API returns a list of measurements
                    if not isinstance(data, list) or len(data) == 0:
                        raise UpdateFailed("No parking data available")

                    parking_data = data[0]

                    # Extract the latest measurement
                    available_spaces = parking_data.get("free_spot_number")
                    occupied_spaces = parking_data.get("occupied_spot_number")
                    closed_spaces = parking_data.get("closed_spot_number", 0)
                    total_spaces = parking_data.get("total_spot_number")

                    if available_spaces is None or occupied_spaces is None or total_spaces is None:
                        _LOGGER.error(
                            "Missing parking data in API response. Available keys: %s, Data: %s",
                            list(parking_data.keys()),
                            parking_data
                        )
                        raise UpdateFailed("Missing parking data in API response")

                    # Calculate occupancy percentage
                    occupancy_percentage = (
                        (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
                    )

                    # Use custom name if provided, otherwise use API name
                    display_name = self.parking_name or parking_data.get("name", "Prague Parking")

                    return {
                        "available_spaces": available_spaces,
                        "total_capacity": total_spaces,
                        "occupancy_percentage": round(occupancy_percentage, 1),
                        "occupied_spaces": occupied_spaces,
                        "closed_spaces": closed_spaces,
                        "parking_id": parking_data.get("parking_id"),
                        "name": display_name,
                        "address": parking_data.get("address", ""),
                        "last_updated": parking_data.get("last_updated"),
                        "api_request_duration_ms": duration_ms,
                    }

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

