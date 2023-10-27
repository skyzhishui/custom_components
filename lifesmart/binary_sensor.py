"""Support for LifeSmart binary sensors."""
import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    ENTITY_ID_FORMAT,
)

from . import LifeSmartEntity

_LOGGER = logging.getLogger(__name__)


GUARD_SENSOR = ["SL_SC_G",
"SL_SC_BG"]
MOTION_SENSOR = ["SL_SC_MHW",
"SL_SC_BM",
"SL_SC_CM"]
SMOKE_SENSOR = ["SL_P_A"]
def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for lifesmart devices."""
    if discovery_info is None:
        return
    dev = discovery_info.get("dev")
    param = discovery_info.get("param")
    devices = []
    for idx in dev['data']:
        if idx in ["M","G","B","AXS","P1"]:
            devices.append(LifeSmartBinarySensor(dev,idx,dev['data'][idx],param))
    add_entities(devices)

class LifeSmartBinarySensor(LifeSmartEntity, BinarySensorEntity):
    """Representation of LifeSmartBinarySensor."""

    def __init__(self, dev, idx, val, param):
        super().__init__(dev, idx, val, param)
        self.entity_id = ENTITY_ID_FORMAT.format(( dev['devtype'] + "_" + dev['agt'] + "_" + dev['me'] + "_" + idx).lower())
        devtype = dev['devtype']
        if devtype in GUARD_SENSOR:
            self._device_class = "door"
        elif devtype in MOTION_SENSOR:
            self._device_class = "motion"
        else:
            self._device_class = "smoke"
        if (val['val'] == 1 and self._device_class != "door") or (val['val'] == 0 and self._device_class == "door"):
            self._state = True
        else:
            self._state = False

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of binary sensor."""
        return self._device_class



