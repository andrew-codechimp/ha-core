"""The T-Smart integration."""

from __future__ import annotations

from dataclasses import dataclass

from aiotsmart import Configuration, TSmartClient, TSmartError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import TsmartCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.CLIMATE]


@dataclass
class TsmartData:
    """Tsmart data type."""

    client: TSmartClient
    configuration: Configuration
    coordinator: TsmartCoordinator


type TsmartConfigEntry = ConfigEntry[TsmartData]


async def async_setup_entry(hass: HomeAssistant, entry: TsmartConfigEntry) -> bool:
    """Set up T-Smart from a config entry."""

    try:
        client = TSmartClient(entry.data[CONF_IP_ADDRESS])
        configuration = await client.configuration_read()
    except TSmartError as ex:
        raise ConfigEntryNotReady("Failed to connect") from ex

    assert entry.unique_id

    coordinator = TsmartCoordinator(hass, client)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = TsmartData(client, configuration, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: TsmartConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
