"""lifesmart switch @skyzhishui"""
import subprocess
import urllib.request
import json
import time
import hashlib
import logging
from . import LifeSmartDevice


from homeassistant.components.switch import (
    SwitchDevice,
    ENTITY_ID_FORMAT,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Find and return lifesmart switches."""
    if discovery_info is None:
        return
    dev = discovery_info.get("dev")
    param = discovery_info.get("param")
    devices = []
    for idx in dev['data']:
        devices.append(LifeSmartSwitch(dev,idx,dev['data'][idx],param))
    add_entities(devices)
    return True

class LifeSmartSwitch(LifeSmartDevice, SwitchDevice):
    

    def __init__(self, dev, idx, val, param):
        """Initialize the switch."""
        super().__init__(dev, idx, val, param)
        self.entity_id = ENTITY_ID_FORMAT.format(( dev['devtype'] + "_" + dev['agt'] + "_" + dev['me'] + "_" + idx).lower())
        if val['val'] == 1:
            self._state = True
        else:
            self._state = False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""

    def _get_state(self):
        """get lifesmart switch state."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the device on."""
        if super()._lifesmart_epset(self, "0x81", 1, self._idx) == 0:
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if super()._lifesmart_epset(self, "0x80", 0, self._idx) == 0:
            self._state = False
            self.schedule_update_ha_state()

