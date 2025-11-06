"""Entity classes for the TSmart integration."""

from __future__ import annotations

import logging

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TSmartConfigEntry, TSmartCoordinator

_LOGGER = logging.getLogger(__name__)


class TSmartEntity(CoordinatorEntity[TSmartCoordinator]):
    """Define a TSmart entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TSmartCoordinator,
        entry: TSmartConfigEntry,
        key: str,
    ) -> None:
        """Initialize TSmart entity."""
        super().__init__(coordinator)
        unique_id = entry.unique_id
        if unique_id is None:
            raise HomeAssistantError("Config entry has no unique ID")
        self._attr_unique_id = f"{unique_id}_{key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="Tesla UK",
            model="T-Smart Water Heater",
            serial_number=entry.runtime_data.configuration.device_id,
            name=entry.runtime_data.configuration.device_name,
            sw_version=entry.runtime_data.configuration.firmware_version,
        )
