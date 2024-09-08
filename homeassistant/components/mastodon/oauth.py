"""Provide oauth implementations for Mastodon integration."""

from typing import Final

from mastodon.Mastodon import Mastodon

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

SCOPES: Final = ["read", "write:statuses"]
REDIRECT_URIS: Final = "https://my.home-assistant.io/redirect/oauth"


class MastodonImplementation(config_entry_oauth2_flow.LocalOAuth2Implementation):
    """Mastodon Oauth2 implementation."""

    def __init__(self, hass: HomeAssistant, base_url, client_id, client_secret) -> None:
        """Initialize Oauth2 implementation."""

        super().__init__(
            hass,
            DOMAIN,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=base_url,
            token_url="",
        )

    @property
    def name(self) -> str:
        """Name of the implementation."""
        return self.authorize_url

    async def async_generate_authorize_url(self, flow_id: str) -> str:
        """Generate a url for the user to authorize based on app registration."""
        query = await super().async_generate_authorize_url()

        authorize_url = await self.hass.async_add_executor_job(
            Mastodon.auth_request_url(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uris=REDIRECT_URIS,
                scopes=SCOPES,
                force_login=True,
            )
        )
        return f"{authorize_url}{query}"
