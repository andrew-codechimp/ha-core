"""Config flow for T-Smart."""

from __future__ import annotations

import logging
from typing import Any

from aiotsmart import Configuration, TSmartClient, TSmartDiscovery, TSmartError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_IP_ADDRESS

from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
    }
)


def _base_schema(
    discovery_info: dict[str, Any] | None = None,
) -> vol.Schema:
    """Generate base schema."""
    base_schema: dict[Any, Any] = {}
    if discovery_info and CONF_IP_ADDRESS in discovery_info:
        base_schema.update(
            {
                vol.Required(
                    CONF_IP_ADDRESS,
                    description={"suggested_value": discovery_info[CONF_IP_ADDRESS]},
                ): str,
            }
        )
    else:
        base_schema.update({vol.Required(CONF_IP_ADDRESS): str})

    return vol.Schema(base_schema)


class TSmartConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TSmart Thermostat."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize an instance of the TSmart config flow."""
        self.data_schema = _base_schema()
        self.discovery_info = None

    async def _discover(self):
        """Discover an unconfigured TSmart thermostat."""
        self.discovery_info = None

        discovery = TSmartDiscovery()
        devices = await discovery.discover()

        for device in devices:
            existing_entries = [
                entry
                for entry in self.hass.config_entries.async_entries(DOMAIN)
                if entry.unique_id == device.device_id
            ]
            if existing_entries:
                _LOGGER.debug(
                    "%s: Already setup, skipping new discovery",
                    device.device_id,
                )
                continue

            self.discovery_info = {
                CONF_IP_ADDRESS: device.ip_address,
                CONF_DEVICE_ID: device.device_id,
                CONF_DEVICE_NAME: device.device_name,
            }
            _LOGGER.debug("Discovered thermostat: %s", self.discovery_info)

            # update with suggested values from discovery
            self.data_schema = _base_schema(self.discovery_info)

    async def check_connection(
        self, ip_address: str
    ) -> tuple[dict[str, str], Configuration | None]:
        """Check connection to the thermostat."""
        client = TSmartClient(ip_address=ip_address)

        try:
            configuration = await client.configuration_read()
        except TSmartError:
            return {"base": "no_thermostat_found"}, None

        return {}, configuration

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input:
            errors, configuration = await self.check_connection(
                user_input[CONF_IP_ADDRESS]
            )

            if not errors:
                user_input[CONF_DEVICE_ID] = configuration.device_id
                user_input[CONF_DEVICE_NAME] = configuration.device_name

                await self.async_set_unique_id(configuration.device_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=configuration.device_id, data=user_input
                )

        # no device specified, see if we can discover an unconfigured thermostat
        await self._discover()
        if self.discovery_info:
            await self.async_set_unique_id(self.discovery_info[CONF_DEVICE_ID])
            user_input = {}
            user_input[CONF_IP_ADDRESS] = self.discovery_info[CONF_IP_ADDRESS]
            user_input[CONF_DEVICE_ID] = self.discovery_info[CONF_DEVICE_ID]
            user_input[CONF_DEVICE_NAME] = self.discovery_info[CONF_DEVICE_NAME]
            return await self.async_step_edit(user_input)

        # no discovered devices, show the form for manual entry
        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )
