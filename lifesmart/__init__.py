"""lifesmart by @skyzhishui"""
import subprocess
import urllib.request
import json
import time
import hashlib
import logging
import threading
import websocket
from datetime import timedelta

import voluptuous as vol

from homeassistant.const import (
    CONF_FRIENDLY_NAME,
)
from homeassistant.core import callback
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util.dt import utcnow

_LOGGER = logging.getLogger(__name__)

CONF_LIFESMART_APPKEY = "appkey"
CONF_LIFESMART_APPTOKEN = "apptoken"
CONF_LIFESMART_USERTOKEN = "usertoken"
CONF_LIFESMART_USERID = "userid"
CONF_EXCLUDE_ITEMS = "exclude"
SWTICH_TYPES = ["SL_OL_W",
"SL_SW_IF1",
"SL_SW_IF2",
"SL_SW_IF3",
"OD_WE_OT1"
]
SPOT_TYPES = ["MSL_IRCTL",
"OD_WE_IRCTL",
"SL_SPOT"]
BINARY_SENSOR_TYPES = ["SL_SC_G",
"SL_SC_BG",
"SL_SC_MHW ",
"SL_SC_BM",
"SL_SC_CM",
"SL_P_A"]
COVER_TYPES = ["SL_DOOYA"]
GAS_SENSOR_TYPES = ["SL_SC_WA ",
"SL_SC_CH",
"SL_SC_CP",
"ELIQ_EM"]
EV_SENSOR_TYPES = ["SL_SC_THL",
"SL_SC_BE",
"SL_SC_CQ"]

ENTITYID = 'entity_id'
DOMAIN = 'lifesmart'

LifeSmart_STATE_MANAGER = 'lifesmart_wss'


def lifesmart_EpGetAll(appkey,apptoken,usertoken,userid):
    url = "https://api.ilifesmart.com/app/api.EpGetAll"
    tick = int(time.time())
    sdata = "method:EpGetAll,time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
    sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
    send_values ={
      "id": 1,
      "method": "EpGetAll",
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
    if response['code'] == 0:
        return response['message']
    return False


def lifesmart_Sendkeys(appkey,apptoken,usertoken,userid,agt,ai,me,category,brand,keys):
    url = "https://api.ilifesmart.com/app/irapi.SendKeys"
    tick = int(time.time())
    #keys = str(keys)
    sdata = "method:SendKeys,agt:"+agt+",ai:"+ai+",brand:"+brand+",category:"+category+",keys:"+keys+",me:"+me+",time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
    sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
    _LOGGER.debug("sendkey: %s",str(sdata))
    send_values ={
      "id": 1,
      "method": "SendKeys",
      "params": {
          "agt": agt,
          "me": me,
          "category": category,
          "brand": brand,
          "ai": ai,
          "keys": keys
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
    _LOGGER.debug("sendkey_res: %s",str(response))
    return response
def lifesmart_Sendackeys(appkey,apptoken,usertoken,userid,agt,ai,me,category,brand,keys,power,mode,temp,wind,swing):                                                                             
    url = "https://api.ilifesmart.com/app/irapi.SendACKeys"                                                                                                        
    tick = int(time.time()) 
    sdata = "method:SendACKeys,agt:"+agt+",ai:"+ai+",brand:"+brand+",category:"+category+",keys:"+keys+",me:"+me+",mode:"+str(mode)+",power:"+str(power)+",swing:"+str(swing)+",temp:"+str(temp)+",wind:"+str(wind)+",time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
    sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()     
    _LOGGER.debug("sendackey: %s",str(sdata))
    send_values ={                                                                                                                                                                                                 
      "id": 1,                                                                                                                                                                                                     
      "method": "SendACKeys",                                                                                                                                                                                        
      "params": {                                                                                                                                                                                                  
          "agt": agt,                                                                                                                                                                                              
          "me": me,                                                                                                                                                                                                
          "category": category,                                                                                                                                                                                    
          "brand": brand,                                                                                                                                                                                          
          "ai": ai,                                                                                                                                                                                                
          "keys": keys,
          "power": power,
          "mode": mode,
          "temp": temp,
          "wind": wind,
          "swing": swing                                                                                                                                                                                            
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
    _LOGGER.debug("sendackey_res: %s",str(response))
    return response 

def setup(hass, config):
    """Set up the LifeSmart component."""
    param = {}
    param['appkey'] = config[DOMAIN][CONF_LIFESMART_APPKEY]
    param['apptoken'] = config[DOMAIN][CONF_LIFESMART_APPTOKEN]
    param['usertoken'] = config[DOMAIN][CONF_LIFESMART_USERTOKEN]
    param['userid'] = config[DOMAIN][CONF_LIFESMART_USERID]
    exclude_items = config[DOMAIN][CONF_EXCLUDE_ITEMS]
    devices = lifesmart_EpGetAll(param['appkey'],param['apptoken'],param['usertoken'],param['userid'])
    for dev in devices:
        if dev['me'] in exclude_items:
            continue
        devtype = dev['devtype']
        if devtype in SWTICH_TYPES:
            discovery.load_platform(hass,"switch", DOMAIN, {"dev": dev,"param": param}, config)
        elif devtype in BINARY_SENSOR_TYPES:
            discovery.load_platform(hass,"binary_sensor", DOMAIN, {"dev": dev,"param": param}, config)
        elif devtype in COVER_TYPES:
            discovery.load_platform(hass,"cover", DOMAIN, {"dev": dev,"param": param}, config)
        elif devtype in EV_SENSOR_TYPES or devtype in GAS_SENSOR_TYPES:
            discovery.load_platform(hass,"sensor", DOMAIN, {"dev": dev,"param": param}, config)
        elif devtype in SPOT_TYPES:
            discovery.load_platform(hass,"light", DOMAIN, {"dev": dev,"param": param}, config)

    def send_keys(call):
        """Handle the service call."""
        agt = call.data['agt']
        me = call.data['me']
        ai = call.data['ai']
        category = call.data['category']
        brand = call.data['brand']
        keys = call.data['keys']
        restkey = lifesmart_Sendkeys(param['appkey'],param['apptoken'],param['usertoken'],param['userid'],agt,ai,me,category,brand,keys)
        _LOGGER.debug("sendkey: %s",str(restkey))
    def send_ackeys(call):
        """Handle the service call."""
        agt = call.data['agt']
        me = call.data['me']
        ai = call.data['ai']
        category = call.data['category']
        brand = call.data['brand']
        keys = call.data['keys']
        power = call.data['power']
        mode = call.data['mode']
        temp = call.data['temp']
        wind = call.data['wind']
        swing = call.data['swing']
        restackey = lifesmart_Sendackeys(param['appkey'],param['apptoken'],param['usertoken'],param['userid'],agt,ai,me,category,brand,keys,power,mode,temp,wind,swing)
        _LOGGER.debug("sendkey: %s",str(restackey))
    def on_message(ws, message):
        _LOGGER.info("websocket_msg: %s",str(message))
        msg = json.loads(message)
        if msg['type'] != "io":
            return
        if msg['msg']['idx'] != "s" and msg['msg']['me'] not in exclude_items:
            devtype = msg['msg']['devtype']
            if devtype in SWTICH_TYPES:
                enid = "switch."+(devtype + "_" + msg['msg']['me'] + "_" + msg['msg']['idx']).lower()
                #_LOGGER.debug("websocket_msg_nid: %s",enid)
                attrs = hass.states.get(enid).attributes
                if msg['msg']['val'] == 1:
                    hass.states.set(enid, 'on',attrs)
                else:
                    hass.states.set(enid, 'off',attrs)
            elif devtype in BINARY_SENSOR_TYPES and msg['msg']['idx'] in ["M","G","B","AXS","P1"]:
                enid = "binary_sensor."+(devtype + "_" + msg['msg']['me'] + "_" + msg['msg']['idx']).lower()
                #_LOGGER.debug("websocket_msg_nid: %s",enid)
                attrs = hass.states.get(enid).attributes
                #_LOGGER.debug("websocket_states: %s",str(attrs))
                #sdata = { "entity_id":enid }
                if msg['msg']['val'] == 1:
                    hass.states.set(enid, 'on',attrs)
                else:
                    hass.states.set(enid, 'off',attrs)
            elif devtype in COVER_TYPES and msg['msg']['idx'] == "P1":
                enid = "cover."+(devtype + "_" + msg['msg']['me']).lower()
                #_LOGGER.debug("websocket_msg_nid: %s",enid)
                #attrs = hass.states.get(enid).attributes
                #stat = hass.states.get(enid).state
                attrs = dict(hass.states.get(enid).attributes)
                nval = msg['msg']['val']
                ntype = msg['msg']['type']
                attrs['current_position'] = nval & 0x7F
                _LOGGER.debug("websocket_cover_attrs: %s",str(attrs))
                nstat = None
                if ntype % 2 == 0:
                    if nval > 0:
                        nstat = "open"
                    else:
                        nstat = "closed"
                else:
                    if nval & 0x80 == 0x80:
                        nstat = "opening"
                    else:
                        nstat = "closing"
                hass.states.set(enid, nstat, attrs)
            elif devtype in EV_SENSOR_TYPES:
                enid = "sensor."+(devtype + "_" + msg['msg']['me'] + "_" + msg['msg']['idx']).lower()
                #_LOGGER.debug("websocket_msg_nid: %s",enid)
                attrs = hass.states.get(enid).attributes
                hass.states.set(enid, msg['msg']['v'], attrs)
            elif devtype in GAS_SENSOR_TYPES:
                enid = "sensor."+(devtype + "_" + msg['msg']['me'] + "_" + msg['msg']['idx']).lower()
                #_LOGGER.debug("websocket_msg_nid: %s",enid)
                attrs = hass.states.get(enid).attributes
                hass.states.set(enid, msg['msg']['val'], attrs)
            elif devtype in SPOT_TYPES:
                enid = "light."+(devtype + "_" + msg['msg']['me'] + "_" + msg['msg']['idx']).lower()
                #_LOGGER.debug("websocket_msg_nid: %s",enid)
                attrs = hass.states.get(enid).attributes
                if msg['msg']['type'] % 2 == 1:
                    hass.states.set(enid, 'on',attrs)
                else:
                    hass.states.set(enid, 'off',attrs)
                
    def on_error(ws, error):
        _LOGGER.debug(error)

    def on_close(ws):
        _LOGGER.debug("lifesmart websocket closed...")
        
    def on_open(ws):
        tick = int(time.time())
        sdata = "method:WbAuth,time:"+str(tick)+",userid:"+param['userid']+",usertoken:"+param['usertoken']+",appkey:"+param['appkey']+",apptoken:"+param['apptoken']
        sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
        send_values ={
        "id": 1,
        "method": "WbAuth",
        "system": {
        "ver": "1.0",
        "lang": "en",
        "userid": param['userid'],
        "appkey": param['appkey'],
        "time": tick,
        "sign": sign
        }
        }
        header = {'Content-Type': 'application/json'}
        send_data = json.dumps(send_values)
        ws.send(send_data)
        _LOGGER.debug("lifesmart websocket sending_data...")

    hass.services.register(DOMAIN, 'send_keys', send_keys)
    hass.services.register(DOMAIN, 'send_ackeys', send_ackeys)
    ws = websocket.WebSocketApp("wss://api.ilifesmart.com:8443/wsapp/",
                          on_message = on_message,
                          on_error = on_error,
                          on_close = on_close)
    ws.on_open = on_open
    hass.data[LifeSmart_STATE_MANAGER] = LifeSmartStatesManager(ws = ws)
    hass.data[LifeSmart_STATE_MANAGER].start_keep_alive()
    return True

class LifeSmartDevice(Entity):
    """LifeSmart base device."""

    def __init__(self, dev, idx, val, param):
        """Initialize the switch."""
        self._name = dev['name'] + "_" + idx
        self._appkey = param['appkey']
        self._apptoken = param['apptoken']
        self._usertoken = param['usertoken']
        self._userid = param['userid']
        self._agt = dev['agt']
        self._me = dev['me']
        self._idx = idx
        self._devtype = dev['devtype']
        attrs = {"agt": self._agt,"me": self._me,"idx": self._idx,"devtype": self._devtype }
        self._attributes = attrs
        

    @property
    def object_id(self):
        """Return LifeSmart device id."""
        return self.entity_id

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def name(self):
        """Return LifeSmart device name."""
        return self._name

    @property
    def assumed_state(self):
        """Return true if we do optimistic updates."""
        return False

    @property
    def should_poll(self):
        """check with the entity for an updated state."""
        return False


    @staticmethod
    def _lifesmart_epset(self, type, val, idx):
        url = "https://api.ilifesmart.com/app/api.EpSet"
        tick = int(time.time())
        appkey = self._appkey
        apptoken = self._apptoken
        userid = self._userid
        usertoken = self._usertoken
        agt = self._agt
        me = self._me
        sdata = "method:EpSet,agt:"+ agt +",idx:"+idx+",me:"+me+",type:"+type+",val:"+str(val)+",time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
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
          "type": type,
          "val": val
          }
        }
        header = {'Content-Type': 'application/json'}
        send_data = json.dumps(send_values)
        req = urllib.request.Request(url=url, data=send_data.encode('utf-8'), headers=header, method='POST')
        response = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        #_LOGGER.info("epset_send: %s",str(send_data))
        #_LOGGER.info("epset_res: %s",str(response))
        return response['code']

    @staticmethod
    def _lifesmart_epget(self):
        url = "https://api.ilifesmart.com/app/api.EpGet"
        tick = int(time.time())
        appkey = self._appkey
        apptoken = self._apptoken
        userid = self._userid
        usertoken = self._usertoken
        agt = self._agt
        me = self._me
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
        return response['message']['data']

class LifeSmartStatesManager(threading.Thread):


    def __init__(self, ws):
        """Init LifeSmart websocket Manager."""
        threading.Thread.__init__(self)
        self._run = False
        self._lock = threading.Lock()
        self._ws = ws

    def run(self):
        while self._run:
            _LOGGER.debug('lifesmart: starting wss...')
            self._ws.run_forever()
            _LOGGER.debug('lifesmart: restart wss...')
            time.sleep(10)

    def start_keep_alive(self):
        """Start keep alive."""
        with self._lock:
            self._run = True
            threading.Thread.start(self)

    def stop_keep_alive(self):
        """Stop keep alive."""
        with self._lock:
            self._run = False
            self.join()
