"""Define an object to manage fetching Tsmart data."""

from __future__ import annotations

from datetime import timedelta

from aiotsmart import Status, TSmartClient, TSmartError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import LOGGER


class TsmartCoordinator(DataUpdateCoordinator[Status]):
    """Class to manage fetching Tsmart data."""

    def __init__(self, hass: HomeAssistant, client: TSmartClient) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass, logger=LOGGER, name="T-Smart", update_interval=timedelta(seconds=10)
        )
        self.client = client

    async def _async_update_data(self) -> Status:
        try:
            return await self.client.control_read()
        except TSmartError as ex:
            raise UpdateFailed(ex) from ex
