"""Constants for the HaveIBeenPwned integration."""

import logging
from typing import Final

LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "haveibeenpwned"

CONF_BASE_URL: Final = "base_url"
DATA_HASS_CONFIG = "haveibeenpwned_hass_config"
DEFAULT_NAME: Final = "HaveIBeenPwned"
