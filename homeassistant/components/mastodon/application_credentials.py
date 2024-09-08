"""application_credentials platform for Mastodon."""

from homeassistant.components.application_credentials import AuthorizationServer
from homeassistant.core import HomeAssistant


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    return AuthorizationServer(
        authorize_url="",  # Overridden in config flow as needs Mastodon instance
        token_url="",  # Overridden in config flow as needs Mastodon instance
    )
