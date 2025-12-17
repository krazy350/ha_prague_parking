"""Sensor platform for Prague Parking."""
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PragueParkingCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prague Parking sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        PragueParkingAvailableSensor(coordinator, entry.entry_id),
        PragueParkingCapacitySensor(coordinator, entry.entry_id),
        PragueParkingOccupancySensor(coordinator, entry.entry_id),
    ]

    async_add_entities(sensors, True)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Prague Parking sensor platform from YAML."""
    coordinators = hass.data[DOMAIN]["coordinators"]

    sensors = []
    for coordinator in coordinators:
        sensors.extend([
            PragueParkingAvailableSensor(coordinator),
            PragueParkingCapacitySensor(coordinator),
            PragueParkingOccupancySensor(coordinator),
        ])

    async_add_entities(sensors, True)


class PragueParkingBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Prague Parking sensors."""

    def __init__(self, coordinator: PragueParkingCoordinator, entry_id: str | None = None) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = False
        self._entry_id = entry_id

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "parking_id": self.coordinator.data.get("parking_id"),
            "parking_name": self.coordinator.data.get("name"),
            "address": self.coordinator.data.get("address"),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class PragueParkingAvailableSensor(PragueParkingBaseSensor):
    """Sensor for available parking spaces."""

    def __init__(self, coordinator: PragueParkingCoordinator, entry_id: str | None = None) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)

        # Get parking name from coordinator data or use parking_id
        parking_name = coordinator.parking_name or coordinator.parking_id

        self._attr_name = f"{parking_name} Available Spaces"
        unique_id_suffix = f"_{entry_id}" if entry_id else f"_{coordinator.parking_id}"
        self._attr_unique_id = f"{DOMAIN}_available_spaces{unique_id_suffix}"
        self._attr_icon = "mdi:car"
        self._attr_native_unit_of_measurement = "spaces"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("available_spaces")


class PragueParkingCapacitySensor(PragueParkingBaseSensor):
    """Sensor for total parking capacity."""

    def __init__(self, coordinator: PragueParkingCoordinator, entry_id: str | None = None) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)

        # Get parking name from coordinator data or use parking_id
        parking_name = coordinator.parking_name or coordinator.parking_id

        self._attr_name = f"{parking_name} Total Capacity"
        unique_id_suffix = f"_{entry_id}" if entry_id else f"_{coordinator.parking_id}"
        self._attr_unique_id = f"{DOMAIN}_total_capacity{unique_id_suffix}"
        self._attr_icon = "mdi:car-multiple"
        self._attr_native_unit_of_measurement = "spaces"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("total_capacity")


class PragueParkingOccupancySensor(PragueParkingBaseSensor):
    """Sensor for parking occupancy percentage."""

    def __init__(self, coordinator: PragueParkingCoordinator, entry_id: str | None = None) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)

        # Get parking name from coordinator data or use parking_id
        parking_name = coordinator.parking_name or coordinator.parking_id

        self._attr_name = f"{parking_name} Occupancy"
        unique_id_suffix = f"_{entry_id}" if entry_id else f"_{coordinator.parking_id}"
        self._attr_unique_id = f"{DOMAIN}_occupancy_percentage{unique_id_suffix}"
        self._attr_icon = "mdi:percent"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("occupancy_percentage")

