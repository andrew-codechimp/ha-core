"""Base class for Tsmart entities."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TsmartConfigEntry
from .const import DOMAIN
from .coordinator import TsmartCoordinator


class TsmartEntity(CoordinatorEntity[TsmartCoordinator]):
    """Defines a base Tsmart entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TsmartCoordinator,
        entity_description: EntityDescription,
        data: TsmartConfigEntry,
    ) -> None:
        """Initialize Mastodon entity."""
        super().__init__(coordinator)
        unique_id = data.unique_id
        assert unique_id is not None
        self._attr_unique_id = f"{unique_id}_{entity_description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="Tesla UK Limited",
            model="T-Smart",
            sw_version=data.runtime_data.configuration.firmware_version,
            serial_number=data.runtime_data.configuration.device_id,
            name=data.runtime_data.configuration.device_name,
        )

        self.entity_description = entity_description
