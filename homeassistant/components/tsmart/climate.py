"""Tsmart platform for climate components."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from aiotsmart import Mode

from homeassistant.components.climate import (
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_ECO,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TsmartConfigEntry
from .const import PRESET_MANUAL, PRESET_SMART, PRESET_TIMER
from .entity import TsmartEntity

SCAN_INTERVAL = timedelta(seconds=5)

PRESET_MAP = {
    PRESET_MANUAL: Mode.MANUAL,
    PRESET_ECO: Mode.ECO,
    PRESET_SMART: Mode.SMART,
    PRESET_TIMER: Mode.TIMER,
    PRESET_AWAY: Mode.TRAVEL,
    PRESET_BOOST: Mode.BOOST,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TsmartConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform for entity."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([TsmartClimateEntity(coordinator)])


class TsmartClimateEntity(TsmartEntity, ClimateEntity):
    """A Tsmart climate entity."""

    _attr_translation_key = "thermostat"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]

    _enable_turn_on_off_backwards_compatibility = False

    _attr_preset_modes = list(PRESET_MAP.keys())
    _attr_max_temp = 70
    _attr_min_temp = 15
    _attr_target_temperature_step = 5

    _attr_has_entity_name = True
    _attr_name = None

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Get supported features."""
        return (
            ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
        )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Get HVAC mode."""
        return HVACMode.HEAT if self.coordinator.data.mode else HVACMode.OFF

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.temperature_high

    @property
    def target_temperature(self) -> float | None:
        """Get the target temperature."""
        return self.coordinator.data.setpoint

    def _climate_preset(self, tsmart_mode: Mode) -> str | None:
        return next((k for k, v in PRESET_MAP.items() if v == tsmart_mode), None)

    @property
    def preset_mode(self) -> str | None:
        """Get the current preset mode."""
        return self._climate_preset(self.coordinator.data.mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        await self._tsmart.async_control_set(
            hvac_mode == HVACMode.HEAT,
            PRESET_MAP[self.preset_mode],
            self.target_temperature,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        await self.coordinator.client.control_write(
            self.hvac_mode == HVACMode.HEAT,
            PRESET_MAP[preset_mode],
            self.target_temperature,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, temperature, **kwargs: Any) -> None:
        """Set the target temperature."""
        await self.coordinator.client.control_write(
            self.hvac_mode == HVACMode.HEAT, PRESET_MAP[self.preset_mode], temperature
        )
        await self.coordinator.async_request_refresh()
