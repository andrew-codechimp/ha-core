"""Constants for SFR Box tests."""
from homeassistant.components.select.const import ATTR_OPTIONS
from homeassistant.components.sensor import (
    ATTR_STATE_CLASS,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.sfr_box.const import DOMAIN
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ENTITY_ID,
    ATTR_IDENTIFIERS,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_STATE,
    ATTR_SW_VERSION,
    ATTR_UNIT_OF_MEASUREMENT,
    SIGNAL_STRENGTH_DECIBELS,
    Platform,
    UnitOfDataRate,
)

ATTR_DEFAULT_DISABLED = "default_disabled"
ATTR_UNIQUE_ID = "unique_id"
FIXED_ATTRIBUTES = (
    ATTR_DEVICE_CLASS,
    ATTR_OPTIONS,
    ATTR_STATE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
)

EXPECTED_ENTITIES = {
    "expected_device": {
        ATTR_IDENTIFIERS: {(DOMAIN, "e4:5d:51:00:11:22")},
        ATTR_MODEL: "NB6VAC-FXC-r0",
        ATTR_NAME: "SFR Box",
        ATTR_SW_VERSION: "NB6VAC-MAIN-R4.0.44k",
    },
    Platform.SENSOR: [
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_ENTITY_ID: "sensor.sfr_box_line_mode",
            ATTR_STATE: "ADSL2+",
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_linemode",
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_ENTITY_ID: "sensor.sfr_box_counter",
            ATTR_STATE: "16",
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_counter",
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_ENTITY_ID: "sensor.sfr_box_crc",
            ATTR_STATE: "0",
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_crc",
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_DEVICE_CLASS: SensorDeviceClass.SIGNAL_STRENGTH,
            ATTR_ENTITY_ID: "sensor.sfr_box_noise_down",
            ATTR_STATE: "5.8",
            ATTR_STATE_CLASS: SensorStateClass.MEASUREMENT,
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_noise_down",
            ATTR_UNIT_OF_MEASUREMENT: SIGNAL_STRENGTH_DECIBELS,
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_DEVICE_CLASS: SensorDeviceClass.SIGNAL_STRENGTH,
            ATTR_ENTITY_ID: "sensor.sfr_box_noise_up",
            ATTR_STATE: "6.0",
            ATTR_STATE_CLASS: SensorStateClass.MEASUREMENT,
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_noise_up",
            ATTR_UNIT_OF_MEASUREMENT: SIGNAL_STRENGTH_DECIBELS,
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_DEVICE_CLASS: SensorDeviceClass.SIGNAL_STRENGTH,
            ATTR_ENTITY_ID: "sensor.sfr_box_attenuation_down",
            ATTR_STATE: "28.5",
            ATTR_STATE_CLASS: SensorStateClass.MEASUREMENT,
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_attenuation_down",
            ATTR_UNIT_OF_MEASUREMENT: SIGNAL_STRENGTH_DECIBELS,
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_DEVICE_CLASS: SensorDeviceClass.SIGNAL_STRENGTH,
            ATTR_ENTITY_ID: "sensor.sfr_box_attenuation_up",
            ATTR_STATE: "20.8",
            ATTR_STATE_CLASS: SensorStateClass.MEASUREMENT,
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_attenuation_up",
            ATTR_UNIT_OF_MEASUREMENT: SIGNAL_STRENGTH_DECIBELS,
        },
        {
            ATTR_DEVICE_CLASS: SensorDeviceClass.DATA_RATE,
            ATTR_ENTITY_ID: "sensor.sfr_box_rate_down",
            ATTR_STATE: "5549",
            ATTR_STATE_CLASS: SensorStateClass.MEASUREMENT,
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_rate_down",
            ATTR_UNIT_OF_MEASUREMENT: UnitOfDataRate.KILOBITS_PER_SECOND,
        },
        {
            ATTR_DEVICE_CLASS: SensorDeviceClass.DATA_RATE,
            ATTR_ENTITY_ID: "sensor.sfr_box_rate_up",
            ATTR_STATE: "187",
            ATTR_STATE_CLASS: SensorStateClass.MEASUREMENT,
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_rate_up",
            ATTR_UNIT_OF_MEASUREMENT: UnitOfDataRate.KILOBITS_PER_SECOND,
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_DEVICE_CLASS: SensorDeviceClass.ENUM,
            ATTR_ENTITY_ID: "sensor.sfr_box_line_status",
            ATTR_OPTIONS: [
                "no_defect",
                "of_frame",
                "loss_of_signal",
                "loss_of_power",
                "loss_of_signal_quality",
                "unknown",
            ],
            ATTR_STATE: "no_defect",
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_line_status",
        },
        {
            ATTR_DEFAULT_DISABLED: True,
            ATTR_DEVICE_CLASS: SensorDeviceClass.ENUM,
            ATTR_ENTITY_ID: "sensor.sfr_box_training",
            ATTR_OPTIONS: [
                "idle",
                "g_994_training",
                "g_992_started",
                "g_922_channel_analysis",
                "g_992_message_exchange",
                "g_993_started",
                "g_993_channel_analysis",
                "g_993_message_exchange",
                "showtime",
                "unknown",
            ],
            ATTR_STATE: "showtime",
            ATTR_UNIQUE_ID: "e4:5d:51:00:11:22_dsl_training",
        },
    ],
}
