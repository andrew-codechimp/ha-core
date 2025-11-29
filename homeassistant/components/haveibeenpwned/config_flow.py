"""Config flow for HaveIBeenPwned."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_NAME,
    CONF_API_KEY
)
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.helpers.typing import ConfigType

from .const import CONF_BASE_URL, DOMAIN, LOGGER, DEFAULT_NAME

API_KEY_URL = "https://haveibeenpwned.com/API/Key"

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
    }
)

class HaveibeenpwnedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    config_entry: ConfigEntry

    def check_connection(
        self,
        base_url: str,
        api_key: str,
    ) -> tuple[
        dict[str, str] | None,
        dict[str, str] | None,
        dict[str, str],
    ]:
        """Check connection to the Mastodon instance."""
        try:
            client = create_mastodon_client(
                base_url,
                client_id,
                client_secret,
                access_token,
            )
            instance = client.instance()
            account = client.account_verify_credentials()

        except MastodonNetworkError:
            return None, None, {"base": "network_error"}
        except MastodonUnauthorizedError:
            return None, None, {"base": "unauthorized_error"}
        except Exception:  # noqa: BLE001
            LOGGER.exception("Unexpected error")
            return None, None, {"base": "unknown"}
        return instance, account, {}

    def show_user_form(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, str] | None = None,
        description_placeholders: dict[str, str] | None = None,
        step_id: str = "user",
    ) -> ConfigFlowResult:
        """Show the user form."""
        if user_input is None:
            user_input = {}
        return self.async_show_form(
            step_id=step_id,
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, user_input
            ),
            description_placeholders=description_placeholders,
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] | None = None
        if user_input:
            self._async_abort_entries_match(
                {CONF_CLIENT_ID: user_input[CONF_CLIENT_ID]}
            )

            instance, account, errors = await self.hass.async_add_executor_job(
                self.check_connection,
                user_input[CONF_BASE_URL],
                user_input[CONF_CLIENT_ID],
                user_input[CONF_CLIENT_SECRET],
                user_input[CONF_ACCESS_TOKEN],
            )

            if not errors:
                name = construct_mastodon_username(instance, account)
                await self.async_set_unique_id(user_input[CONF_CLIENT_ID])
                return self.async_create_entry(
                    title=name,
                    data=user_input,
                )

        return self.show_user_form(user_input, errors)

   async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input:
            errors, user_id = await self.check_connection(
                user_input[CONF_API_KEY],
            )
            if not errors:
                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data=user_input,
                )
        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
            description_placeholders={"api_key_url": API_KEY_URL},
        )

    async def async_step_import(self, import_config: ConfigType) -> ConfigFlowResult:
        """Import a config entry from configuration.yaml."""
        errors: dict[str, str] | None = None

        LOGGER.debug("Importing Have I Been Pwned from configuration.yaml")

        base_url = str(import_config.get(CONF_BASE_URL, DEFAULT_URL))
        client_id = str(import_config.get(CONF_CLIENT_ID))
        client_secret = str(import_config.get(CONF_CLIENT_SECRET))
        access_token = str(import_config.get(CONF_ACCESS_TOKEN))
        name = import_config.get(CONF_NAME, None)

        instance, account, errors = await self.hass.async_add_executor_job(
            self.check_connection,
            base_url,
            client_id,
            client_secret,
            access_token,
        )

        if not errors:
            await self.async_set_unique_id(client_id)
            self._abort_if_unique_id_configured()

            if not name:
                name = construct_mastodon_username(instance, account)

            return self.async_create_entry(
                title=name,
                data={
                    CONF_BASE_URL: base_url,
                    CONF_CLIENT_ID: client_id,
                    CONF_CLIENT_SECRET: client_secret,
                    CONF_ACCESS_TOKEN: access_token,
                },
            )

        reason = next(iter(errors.items()))[1]
        return self.async_abort(reason=reason)
