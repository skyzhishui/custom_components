"""lifesmart switch @skyzhishui"""
import subprocess
import urllib.request
import json
import time
import hashlib

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import (
    SwitchDevice,
    PLATFORM_SCHEMA,
    ENTITY_ID_FORMAT,
)
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_SWITCHES,
)
CONF_LIFESMART_APPKEY = "appkey"
CONF_LIFESMART_APPTOKEN = "apptoken"
CONF_LIFESMART_USERTOKEN = "usertoken"
CONF_LIFESMART_USERID = "userid"
CONF_LIFESMART_AGT = "agt"
CONF_LIFESMART_DEV_ME = "me"
CONF_LIFESMART_DEV_IDX = "idx"


SWITCH_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_LIFESMART_AGT, default="true"): cv.string,
        vol.Optional(CONF_LIFESMART_DEV_ME, default="true"): cv.string,
        vol.Optional(CONF_LIFESMART_DEV_IDX, default="true"): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_LIFESMART_APPKEY, default="true"): cv.string,
        vol.Optional(CONF_LIFESMART_APPTOKEN, default="true"): cv.string,
        vol.Optional(CONF_LIFESMART_USERTOKEN, default="true"): cv.string,
        vol.Optional(CONF_LIFESMART_USERID, default="true"): cv.string,
        vol.Required(CONF_SWITCHES): cv.schema_with_slug_keys(SWITCH_SCHEMA)
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Find and return lifesmart switches."""
    appkey = config.get(CONF_LIFESMART_APPKEY)
    apptoken = config.get(CONF_LIFESMART_APPTOKEN)
    usertoken = config.get(CONF_LIFESMART_USERTOKEN)
    userid = config.get(CONF_LIFESMART_USERID)
    devices = config.get(CONF_SWITCHES, {})
    switches = []
    for object_id, device_config in devices.items():
        switches.append(
            LifeSmartSwitch(
                hass,
                object_id,
                device_config.get(CONF_FRIENDLY_NAME, object_id),
                appkey,
                apptoken,
                usertoken,
                userid,
                device_config.get(CONF_LIFESMART_AGT),
                device_config.get(CONF_LIFESMART_DEV_ME),
                device_config.get(CONF_LIFESMART_DEV_IDX),
            )
        )

    if not switches:
        return False

    add_entities(switches)


class LifeSmartSwitch(SwitchDevice):

    def __init__(
        self,
        hass,
        object_id,
        friendly_name,
        appkey,
        apptoken,
        usertoken,
        userid,
        agt,
        me,
        idx,
    ):
        """Initialize the switch."""
        self._hass = hass
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)
        self._name = friendly_name
        self._state = False
        self._appkey = appkey
        self._apptoken = apptoken
        self._usertoken = usertoken
        self._userid = userid
        self._agt = agt
        self._me = me
        self._idx = idx

    @staticmethod
    def _post_switch(self, cmd):
        url = "https://api.ilifesmart.com/app/api.EpSet"
        tick = int(time.time())
        appkey = self._appkey
        apptoken = self._apptoken
        userid = self._userid
        usertoken = self._usertoken
        agt = self._agt
        me = self._me
        idx = self._idx
        scmd = str(cmd)
        sdata = "method:EpSet,agt:"+ agt +",idx:"+idx+",me:"+me+",type:0x8"+scmd+",val:"+scmd+",time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
        sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
        send_values = {
          "id": 1,
          "method": "EpSet",
          "system": {
          "ver": "1.0",
          "lang": "en",
          "userid": userid,
          "appkey": appkey,
          "time": tick,
          "sign": sign
          },
          "params": {
          "agt": agt,
          "me": me,
          "idx": idx,
          "type": "0x8"+scmd,
          "val": cmd
          }
        }
        header = {'Content-Type': 'application/json'}
        send_data = json.dumps(send_values)
        req = urllib.request.Request(url=url, data=send_data.encode('utf-8'), headers=header, method='POST')
        response = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        return response['code']
	
    @staticmethod
    def _get_state_value(self):
        url = "https://api.ilifesmart.com/app/api.EpGet"
        tick = int(time.time())
        appkey = self._appkey
        apptoken = self._apptoken
        userid = self._userid
        usertoken = self._usertoken
        agt = self._agt
        me = self._me
        idx = self._idx
        sdata = "method:EpGet,agt:"+ agt +",me:"+ me +",time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
        sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
        send_values = {
          "id": 1,
          "method": "EpGet",
          "system": {
          "ver": "1.0",
          "lang": "en",
          "userid": userid,
          "appkey": appkey,
          "time": tick,
          "sign": sign
          },
          "params": {
          "agt": agt,
          "me": me
          }
        }
        header = {'Content-Type': 'application/json'}
        send_data = json.dumps(send_values)
        req = urllib.request.Request(url=url, data=send_data.encode('utf-8'), headers=header, method='POST')
        response = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        return response['message']['data'][idx]['val'] == 1

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def assumed_state(self):
        """Return true if we do optimistic updates."""
        return False

    def _get_state(self):
        """get lifesmart switch state."""
        return LifeSmartSwitch._get_state_value(self)

    def update(self):
        """Update device state."""
        payload = str(self._get_state())
        self._state = payload.lower() == "true"

    def turn_on(self, **kwargs):
        """Turn the device on."""
        if LifeSmartSwitch._post_switch(self, 1) == 0:
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if LifeSmartSwitch._post_switch(self, 0) == 0:
            self._state = False
            self.schedule_update_ha_state()
