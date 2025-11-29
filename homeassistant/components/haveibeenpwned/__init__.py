"""The HaveIBeenPwned integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import discovery

from .const import CONF_BASE_URL, DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up haveibeenpwned from a config entry."""

    # try:
    #     client, _, _ = await hass.async_add_executor_job(
    #         setup_mastodon,
    #         entry,
    #     )

    # except MastodonError as ex:
    #     raise ConfigEntryNotReady("Failed to connect") from ex

    assert entry.unique_id

    await discovery.async_load_platform(
        hass,
        Platform.SENSOR,
        DOMAIN,
        {CONF_NAME: entry.title, "client": client},
        {},
    )

    return True
