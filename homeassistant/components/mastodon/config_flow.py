"""Config flow for Mastodon."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Final

from mastodon.Mastodon import Mastodon, MastodonNetworkError, MastodonUnauthorizedError
import voluptuous as vol

from homeassistant.config_entries import (
    SOURCE_REAUTH,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_NAME,
)
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import slugify

from .const import CONF_BASE_URL, DEFAULT_URL, DOMAIN, LOGGER
from .utils import (
    construct_mastodon_username,
    create_mastodon_client,
    create_mastodon_client_oauth,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_BASE_URL,
        ): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
        vol.Required(
            CONF_CLIENT_ID,
        ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        vol.Required(
            CONF_CLIENT_SECRET,
        ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        vol.Required(
            CONF_ACCESS_TOKEN,
        ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
    }
)

SCOPES: Final = ["read", "write:statuses"]
REDIRECT_URIS: Final = "https://my.home-assistant.io/redirect/oauth"


class MastodonConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    MINOR_VERSION = 2
    config_entry: ConfigEntry

    def __init__(self) -> None:
        """Initialize MastodonFlowHandler."""
        super().__init__()
        self._data: dict[str, Any] = {}

    def _async_reauth_entry(self) -> ConfigEntry | None:
        """Return existing entry for reauth."""
        if self.source != SOURCE_REAUTH or not (
            entry_id := self.context.get("entry_id")
        ):
            return None
        return next(
            (
                entry
                for entry in self._async_current_entries()
                if entry.entry_id == entry_id
            ),
            None,
        )

    def create_application(
        self,
        base_url,
    ) -> tuple[str, str, dict[str, str]]:
        """Create an application on the Mastodon instance."""
        try:
            client_id, client_secret = Mastodon.create_app(
                client_name="Home Assistant",
                scopes=SCOPES,
                redirect_uris=REDIRECT_URIS,
                website="https://www.home-assistant.io/integrations/mastodon/",
                api_base_url=base_url,
            )
        except MastodonNetworkError:
            return None, None, {"base": "network_error"}
        except MastodonUnauthorizedError:
            return None, None, {"base": "unauthorized_error"}
        except Exception:  # noqa: BLE001
            LOGGER.exception("Unexpected error")
            return None, None, {"base": "unknown"}
        return client_id, client_secret, {}

    def login(
        self,
        base_url,
        client_id,
        client_secret,
        oauth_code,
    ) -> tuple[str, dict[str, str]]:
        """Login using oauth code."""
        try:
            client = create_mastodon_client_oauth(base_url, client_id, client_secret)
            access_token = client.log_in(
                code=oauth_code,
            )
        except MastodonNetworkError:
            return None, {"base": "network_error"}
        except MastodonUnauthorizedError:
            return None, {"base": "unauthorized_error"}
        except Exception:  # noqa: BLE001
            LOGGER.exception("Unexpected error")
            return None, {"base": "unknown"}
        return access_token, {}

    def check_connection(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        access_token: str,
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

    def get_auth_request_url(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
    ) -> tuple[
        dict[str, str] | None,
        dict[str, str] | None,
        dict[str, str],
    ]:
        """Get the auth url for the Mastodon instance."""
        try:
            client = create_mastodon_client_oauth(
                base_url,
                client_id,
                client_secret,
            )
            auth_request_url = client.auth_request_url(
                redirect_uris=REDIRECT_URIS,
                scopes=SCOPES,
            )

        except MastodonNetworkError:
            return None, None, {"base": "network_error"}
        except MastodonUnauthorizedError:
            return None, None, {"base": "unauthorized_error"}
        except Exception:  # noqa: BLE001
            LOGGER.exception("Unexpected error")
            return None, None, {"base": "unknown"}
        return auth_request_url, {}

    async def async_generate_authorize_url(self) -> str:
        """Generate a url for the user to authorize based on user input."""

        auto_request_url, errors = await self.hass.async_add_executor_job(
            self.get_auth_request_url,
            self._data[CONF_BASE_URL],
            self._data[CONF_CLIENT_ID],
            self._data[CONF_CLIENT_SECRET],
        )

        if not errors:
            return auto_request_url
        reason = next(iter(errors.items()))[1]
        return self.async_abort(reason=reason)

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Complete OAuth setup and finish instance or finish."""
        LOGGER.debug("Finishing post-oauth configuration")
        self._data.update(data)
        if self.source == SOURCE_REAUTH:
            LOGGER.debug("Skipping Instance configuration")
            return await self.async_step_finish()
        return await self.async_step_instance()

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

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        self._data.update(entry_data)

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauth dialog."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""

        self._data = {}
        if self.source == SOURCE_REAUTH:
            return await super().async_step_user(user_input)
        # Application Credentials setup needs information from the user
        # before creating the OAuth URL
        return await self.async_step_instance()

    async def async_step_instance(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Handle instance in user input."""
        errors = {}
        if user_input is not None:
            self._data.update(user_input)

            if (
                self._data[CONF_CLIENT_ID]
                and self._data[CONF_CLIENT_ID] != ""
                and self._data[CONF_CLIENT_SECRET]
                and self._data[CONF_CLIENT_SECRET] != ""
            ):
                (
                    client_id,
                    client_secret,
                    errors,
                ) = await self.hass.async_add_executor_job(
                    self.create_application,
                    self._data[CONF_BASE_URL],
                )

                self._data[CONF_CLIENT_ID] = client_id
                self._data[CONF_CLIENT_SECRET] = client_secret

            if not errors:
                return await self.async_step_finish()
        return self.async_show_form(
            step_id="instance",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_BASE_URL,
                    ): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
                }
            ),
            errors=errors,
        )

    async def async_step_finish(
        self, data: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create an entry for the Mastodon account."""
        LOGGER.debug("Creating/updating configuration entry")
        # Update existing config entry when in the reauth flow.
        if entry := self._async_reauth_entry():
            self.hass.config_entries.async_update_entry(
                entry,
                data=self._data,
            )
            await self.hass.config_entries.async_reload(entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        instance, account, errors = await self.hass.async_add_executor_job(
            self.check_connection,
            self._data[CONF_BASE_URL],
            self._data[CONF_CLIENT_ID],
            self._data[CONF_CLIENT_SECRET],
            self._data[CONF_ACCESS_TOKEN],
        )

        if not errors:
            name = construct_mastodon_username(instance, account)
            await self.async_set_unique_id(slugify(name))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data=self._data,
            )
        reason = next(iter(errors.items()))[1]
        return self.async_abort(reason=reason)

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Import a config entry from configuration.yaml."""
        errors: dict[str, str] | None = None

        LOGGER.debug("Importing Mastodon from configuration.yaml")

        base_url = str(import_data.get(CONF_BASE_URL, DEFAULT_URL))
        client_id = str(import_data.get(CONF_CLIENT_ID))
        client_secret = str(import_data.get(CONF_CLIENT_SECRET))
        access_token = str(import_data.get(CONF_ACCESS_TOKEN))
        name = import_data.get(CONF_NAME)

        instance, account, errors = await self.hass.async_add_executor_job(
            self.check_connection,
            base_url,
            client_id,
            client_secret,
            access_token,
        )

        if not errors:
            name = construct_mastodon_username(instance, account)
            await self.async_set_unique_id(slugify(name))
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
