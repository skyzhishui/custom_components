"""Support for the LifeSmart climate devices."""
import logging
import time
from homeassistant.components.climate import ENTITY_ID_FORMAT, ClimateDevice
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_DRY,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    HVAC_MODE_OFF,
)
from homeassistant.components.fan import SPEED_HIGH, SPEED_LOW, SPEED_MEDIUM
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

from . import LifeSmartDevice
_LOGGER = logging.getLogger(__name__)
DEVICE_TYPE = "climate"

LIFESMART_STATE_LIST = [HVAC_MODE_OFF,
HVAC_MODE_AUTO,
HVAC_MODE_FAN_ONLY,
HVAC_MODE_COOL,
HVAC_MODE_HEAT,
HVAC_MODE_DRY]

FAN_MODES = [SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]
GET_FAN_SPEED = { SPEED_LOW:15, SPEED_MEDIUM:45, SPEED_HIGH:76 }

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up LifeSmart Climate devices."""
    if discovery_info is None:
        return
    devices = []
    dev = discovery_info.get("dev")
    param = discovery_info.get("param")
    devices = []
    idx = "T"
    if idx not in dev['data']:
        return
    devices.append(LifeSmartClimateDevice(dev,idx,dev['data'][idx],param))
    add_entities(devices)

class LifeSmartClimateDevice(LifeSmartDevice, ClimateDevice):
    """LifeSmart climate devices,include air conditioner,heater."""

    def __init__(self, dev, idx, val, param):
        """Init LifeSmart cover device."""
        super().__init__(dev, idx, val, param)
        dev['agt'] = dev['agt'].replace("_","")
        self._name = dev['name']
        cdata = dev['data']
        self.entity_id = ENTITY_ID_FORMAT.format(( dev['devtype'] + "_" + dev['agt'] + "_" + dev['me']).lower().replace(":","_").replace("@","_"))
        self._modes = LIFESMART_STATE_LIST
        if cdata['O']['type'] % 2 == 0:
            self._mode = LIFESMART_STATE_LIST[0]
        else:
            self._mode = LIFESMART_STATE_LIST[cdata['MODE']['val']]
        self._attributes.update({"last_mode": LIFESMART_STATE_LIST[cdata['MODE']['val']]})
        self._current_temperature = cdata['T']['v']
        self._target_temperature = cdata['tT']['v']
        self._min_temp = 10
        self._max_temp = 35
        self._fanspeed = cdata['F']['val']

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        return self._mode

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._modes

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def fan_mode(self):
        """Return the fan setting."""
        fanmode = None
        if self._fanspeed < 30:
            fanmode = SPEED_LOW
        elif self._fanspeed < 65 and self._fanspeed >= 30:
            fanmode = SPEED_MEDIUM
        elif self._fanspeed >=65:
            fanmode = SPEED_HIGH
        return fanmode

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return FAN_MODES

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        new_temp = int(kwargs['temperature']*10)
        _LOGGER.info("set_temperature: %s",str(new_temp))
        super()._lifesmart_epset(self, "0x88", new_temp, "tT")

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        super()._lifesmart_epset(self, "0xCE", GET_FAN_SPEED[fan_mode], "F")

    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        if hvac_mode == HVAC_MODE_OFF:
            super()._lifesmart_epset(self, "0x80", 0, "O")
            return
        if self._mode == HVAC_MODE_OFF:
            if super()._lifesmart_epset(self, "0x81", 1, "O") == 0:
                time.sleep(2)
            else:
                return
        super()._lifesmart_epset(self, "0xCE", LIFESMART_STATE_LIST.index(hvac_mode), "MODE")


    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._max_temp
