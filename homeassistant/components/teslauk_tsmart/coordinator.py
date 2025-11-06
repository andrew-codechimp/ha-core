"""Define an object to manage fetching TSmart data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from aiotsmart import Configuration, Status, TSmartClient, TSmartError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import LOGGER

TSMART_UPDATE_INTERVAL = 15


@dataclass
class TSmartData:
    """TSmart data type."""

    client: TSmartClient
    configuration: Configuration
    control_coordinator: TSmartCoordinator


type TSmartConfigEntry = ConfigEntry[TSmartData]


class TSmartCoordinator(DataUpdateCoordinator[Status]):
    """Class to manage fetching TSmart control data."""

    config_entry: TSmartConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: TSmartConfigEntry, client: TSmartClient
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            config_entry=config_entry,
            name="TSmart",
            update_interval=timedelta(seconds=TSMART_UPDATE_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> Status:
        """Fetch data from TSmart API."""
        try:
            status = await self.client.control_read()
        except TSmartError as ex:
            raise UpdateFailed(ex) from ex

        return status
