"""Support for the TSmart water heater."""

from __future__ import annotations

from typing import Any, Final

from aiotsmart import Mode

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import TSmartConfigEntry, TSmartCoordinator
from .entity import TSmartEntity

TSMART_MIN_TEMP: Final = 10.0
TSMART_MAX_TEMP: Final = 75.0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TSmartConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add TSmart Water Heater from a config_entry."""
    coordinator = entry.runtime_data.control_coordinator
    async_add_entities([TSmartWaterHeater(coordinator, entry)])


class TSmartWaterHeater(TSmartEntity, WaterHeaterEntity):
    """Define a TSmart Water Heater."""

    _attr_name = None
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.ON_OFF
        # | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = TSMART_MIN_TEMP
    _attr_max_temp = TSMART_MAX_TEMP
    _attr_target_temperature_step = 1.0

    coordinator: TSmartCoordinator

    def __init__(
        self,
        coordinator: TSmartCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize TSmart water heater entity."""
        super().__init__(coordinator, entry, "water_heater")

        # self._attr_operation_list = [
        #     OPERATION_LIB_TO_HASS[operation]
        #     for operation in self.get_airzone_value(AZD_OPERATIONS)
        # ]
        # self._attr_temperature_unit = TEMP_UNIT_LIB_TO_HASS[
        #     self.get_airzone_value(AZD_TEMP_UNIT)
        # ]

        self._async_update_attrs()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update attributes when the coordinator updates."""
        self._async_update_attrs()
        super()._handle_coordinator_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update water heater attributes."""
        self._attr_current_temperature = float(self.coordinator.data.temperature_high)
        self._attr_target_temperature = float(self.coordinator.data.setpoint)

        # self._attr_current_operation = OPERATION_LIB_TO_HASS[
        #     self.get_airzone_value(AZD_OPERATION)
        # ]

    async def turn_on(self, **kwargs: Any) -> None:
        """Turn on water heater."""
        await self.coordinator.client.control_write(
            power=True, mode=Mode.MANUAL, setpoint=self.coordinator.data.setpoint
        )

    async def turn_off(self, **kwargs: Any) -> None:
        """Turn off water heater."""
        await self.coordinator.client.control_write(
            power=False, mode=Mode.MANUAL, setpoint=self.coordinator.data.setpoint
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        if not self.coordinator.data.power:
            return

        await self.coordinator.client.control_write(
            power=True, mode=Mode.MANUAL, setpoint=int(temperature)
        )
        await self.coordinator.async_request_refresh()
