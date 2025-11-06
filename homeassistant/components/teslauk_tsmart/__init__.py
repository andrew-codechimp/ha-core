"""The T-Smart integration."""

from __future__ import annotations

from aiotsmart import TSmartClient

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import TSmartConfigEntry, TSmartCoordinator, TSmartData, TSmartError

_PLATFORMS: list[Platform] = [Platform.WATER_HEATER]


async def async_setup_entry(hass: HomeAssistant, entry: TSmartConfigEntry) -> bool:
    """Set up T-Smart from a config entry."""

    client = TSmartClient(entry.data["host"])

    try:
        configuration = await client.configuration_read()
    except TSmartError as error:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="setup_failed",
        ) from error

    coordinator = TSmartCoordinator(hass, entry, client)

    entry.runtime_data = TSmartData(client, configuration, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: TSmartConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
