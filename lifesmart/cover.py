"""Support for LifeSmart covers."""
from homeassistant.components.cover import (
    ENTITY_ID_FORMAT,
    ATTR_POSITION,
    CoverDevice,
)

from . import LifeSmartDevice


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up lifesmart dooya cover devices."""
    if discovery_info is None:
        return
    dev = discovery_info.get("dev")
    param = discovery_info.get("param")
    devices = []
    idx = "P1"
    devices.append(LifeSmartCover(dev,idx,dev['data'][idx],param))
    add_entities(devices)


class LifeSmartCover(LifeSmartDevice, CoverDevice):
    """LifeSmart cover devices."""

    def __init__(self, dev, idx, val, param):
        """Init LifeSmart cover device."""
        super().__init__(dev, idx, val, param)
        self._name = dev['name']
        self.entity_id = ENTITY_ID_FORMAT.format(( dev['devtype'] + "_" + dev['agt'] + "_" + dev['me']).lower())
        self._pos = val['val']
        self._device_class = "curtain"

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._pos

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.current_cover_position <= 0

    def close_cover(self, **kwargs):
        """Close the cover."""
        super()._lifesmart_epset(self, "0xCF", 0, "P2")

    def open_cover(self, **kwargs):
        """Open the cover."""
        super()._lifesmart_epset(self, "0xCF", 100, "P2")

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        super()._lifesmart_epset(self, "0xCE", 0x80, "P2")

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        super()._lifesmart_epset(self, "0xCE", position, "P2")

    @property
    def device_class(self):
        """Return the class of binary sensor."""
        return self._device_class
