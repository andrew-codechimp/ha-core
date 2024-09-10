"""Constants for the T-Smart integration."""

import logging
from typing import Final

LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "tsmart"

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"

PRESET_MANUAL = "Manual"
PRESET_SMART = "Smart"
PRESET_TIMER = "Timer"
