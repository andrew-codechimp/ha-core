"""Tsmart platform for binary_sensor components."""

from collections.abc import Callable
from dataclasses import dataclass
import logging

from aiotsmart import Status

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import TsmartConfigEntry
from .entity import TsmartEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class TsmartBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Tsmart binary sensor entity."""

    value_fn: Callable[[Status], StateType]


ENTITY_DESCRIPTIONS = (
    TsmartBinarySensorEntityDescription(
        key="relay",
        translation_key="relay",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda status: status.relay,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TsmartConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform for entity."""
    coordinator = entry.runtime_data.coordinator

    async_add_entities(
        TsmartBinarySensorEntity(
            coordinator=coordinator,
            entity_description=entity_description,
            data=entry,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class TsmartBinarySensorEntity(TsmartEntity, BinarySensorEntity):
    """A Tsmart sensor entity."""

    entity_description: TsmartBinarySensorEntityDescription

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
