"""Support for LifeSmart Light."""
import binascii
import logging
import struct
import urllib.request
import json
import time
import hashlib
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    Light,
	ENTITY_ID_FORMAT,
)
import homeassistant.util.color as color_util

from . import  LifeSmartDevice

_LOGGER = logging.getLogger(__name__)



def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for LifeSmart devices."""
    if discovery_info is None:
        return
    dev = discovery_info.get("dev")
    param = discovery_info.get("param")
    devices = []
    for idx in dev['data']:
        if idx in ["RGB","RGBW"]:
            devices.append(LifeSmartLight(dev,idx,dev['data'][idx],param))
    add_entities(devices)

class LifeSmartLight(LifeSmartDevice, Light):
    """Representation of a LifeSmartLight."""

    def __init__(self, dev, idx, val, param):
        """Initialize the LifeSmartLight."""
        super().__init__(dev, idx, val, param)
        self.entity_id = ENTITY_ID_FORMAT.format(( dev['devtype'] + "_" + dev['agt'] + "_" + dev['me'] + "_" + idx).lower())
        if val['type'] % 2 == 1:
            self._state = True
        else:
            self._state = False
        value = val['val']
        if value == 0:
            self._hs = None
        else:
            rgbhexstr = "%x" % value
            rgbhexstr = rgbhexstr.zfill(8)
            rgbhex = bytes.fromhex(rgbhexstr)
            rgba = struct.unpack("BBBB", rgbhex)
            rgb = rgba[1:]
            self._hs = color_util.color_RGB_to_hs(*rgb)
            _LOGGER.info("hs_rgb: %s",str(self._hs))


    async def async_added_to_hass(self):
        rmdata = {}
        rmlist = LifeSmartLight._lifesmart_GetRemoteList(self)
        for ai in rmlist:
            rms = LifeSmartLight._lifesmart_GetRemotes(self,ai)
            rms['category'] = rmlist[ai]['category']
            rms['brand'] = rmlist[ai]['brand']
            rmdata[ai] = rms
        self._attributes.setdefault('remotelist',rmdata)
    @property
    def is_on(self):
        """Return true if it is on."""
        return self._state

    @property
    def hs_color(self):
        """Return the hs color value."""
        return self._hs

    @property
    def supported_features(self):
        """Return the supported features."""
        return SUPPORT_COLOR

    def turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_HS_COLOR in kwargs:
            self._hs = kwargs[ATTR_HS_COLOR]

        rgb = color_util.color_hs_to_RGB(*self._hs)
        rgba = (0,) + rgb
        rgbhex = binascii.hexlify(struct.pack("BBBB", *rgba)).decode("ASCII")
        rgbhex = int(rgbhex, 16)

        if super()._lifesmart_epset(self, "0xff", rgbhex, self._idx) == 0:
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the light off."""
        if super()._lifesmart_epset(self, "0x80", 0, self._idx) == 0:
            self._state = False
            self.schedule_update_ha_state()
    @staticmethod
    def _lifesmart_GetRemoteList(self):
        appkey = self._appkey
        apptoken = self._apptoken
        usertoken = self._usertoken
        userid = self._userid
        agt = self._agt
        url = "https://api.ilifesmart.com/app/irapi.GetRemoteList"
        tick = int(time.time())
        sdata = "method:GetRemoteList,agt:"+agt+",time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
        sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
        send_values ={
          "id": 1,
          "method": "GetRemoteList",
          "params": {
              "agt": agt
          }, 
          "system": {
          "ver": "1.0",
          "lang": "en",
          "userid": userid,
          "appkey": appkey,
          "time": tick,
          "sign": sign
          }
        }
        header = {'Content-Type': 'application/json'}
        send_data = json.dumps(send_values)
        req = urllib.request.Request(url=url, data=send_data.encode('utf-8'), headers=header, method='POST')
        response = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        return response['message']

    @staticmethod
    def _lifesmart_GetRemotes(self,ai):
        appkey = self._appkey
        apptoken = self._apptoken
        usertoken = self._usertoken
        userid = self._userid
        agt = self._agt
        url = "https://api.ilifesmart.com/app/irapi.GetRemote"
        tick = int(time.time())
        sdata = "method:GetRemote,agt:"+agt+",ai:"+ai+",needKeys:2,time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
        sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
        send_values ={
          "id": 1,
          "method": "GetRemote",
          "params": {
              "agt": agt,
              "ai": ai,
              "needKeys": 2
          },
          "system": {
          "ver": "1.0",
          "lang": "en",
          "userid": userid,
          "appkey": appkey,
          "time": tick,
          "sign": sign
          }
        }
        header = {'Content-Type': 'application/json'}
        send_data = json.dumps(send_values)
        req = urllib.request.Request(url=url, data=send_data.encode('utf-8'), headers=header, method='POST')
        response = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        return response['message']['codes']
