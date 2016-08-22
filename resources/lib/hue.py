import xbmc
import socket
import json
from time import sleep
import logging

from tools import *
from lifxlan import *
try:
  import requests
except ImportError:
  notify("Kodi Lifx", "ERROR: Could not import Python requests")

lifx = None

class Hue:
  params = None
  connected = None
  last_state = None
  light = None
  ambilight_dim_light = None
  pauseafterrefreshchange = 0
  original_powers = None
  original_colors = None

  def __init__(self, settings, args):
    #Logs are good, mkay.
    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    global lifx
    lifx = LifxLAN()

    #get settings
    self.settings = settings
    self._parse_argv(args)

    if self.connected:
      self.update_settings()

    if self.params == {}:
      self.logger.debuglog("params: %s" % self.params)
      #if there's a bridge IP, try to talk to it.
      result = self.test_connection()
      if result:
        self.update_settings()
    elif self.params['action'] == "discover":
      self.logger.debuglog("Starting discovery")
      notify("Lifx Bulbs Discovery", "starting")
      self.test_connection()
      notify("Lifx Bulbs Discovery", "Finished")
      self.update_settings()
    elif self.params['action'] == "reset_settings":
      self.logger.debuglog("Reset Settings to default.")
      self.logger.debuglog(__addondir__)
      os.unlink(os.path.join(__addondir__,"settings.xml"))
      #self.settings.readxml()
      #xbmcgui.Window(10000).clearProperty("script.kodi.hue.ambilight" + '_running')
      #__addon__.openSettings()
    else:
      # not yet implemented
      self.logger.debuglog("unimplemented action call: %s" % self.params['action'])

    #detect pause for refresh change (must reboot for this to take effect.)
    #response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue", "params":{"setting":"videoplayer.pauseafterrefreshchange"},"id":1}'))
    #logger.debuglog(isinstance(response, dict))
    #if "result" in response and "value" in response["result"]:
      #pauseafterrefreshchange = int(response["result"]["value"])

    if self.connected:
      if self.settings.misc_initialflash:
        self.flash_lights()

  def flash_lights(self):
    self.logger.debuglog("class Lifx: flashing lights")
    if self.settings.light == 0:
      self.light.flash_light()
    else:
      for l in self.light:
        l.flash_light()
        #xbmc.sleep(1)

  def _parse_argv(self, args):
    try:
        self.params = dict(arg.split("=") for arg in args.split("&"))
    except:
        self.params = {}

  def test_connection(self):
    self.logger.debuglog("testing connection")
    print("Discovering lights...")
    self.original_powers = lifx.get_power_all_lights()
    self.original_colors = lifx.get_color_all_lights()
    notify("Kodi Lifx", "Connected")
    self.connected = True
    return self.connected

  # #unifed light action method. will replace dim_lights, brighter_lights, partial_lights
  # def light_actions(self, action, lights=None):
  #   if lights == None:
  #     #default for method
  #     lights = self.light

  #   self.last_state = action

  #   if isinstance(lights, list):
  #     #array of lights
  #     for l in lights:
  #       if action == "dim":
  #         l.dim_light()
  #       elif action == "undim":
  #         l.brighter_light()
  #       elif action == "partial":
  #         l.partial_light()
  #   else:
  #     #group
  #     if action == "dim":
  #       lights.dim_light()
  #     elif action == "undim":
  #       lights.brighter_light()
  #     elif action == "partial":
  #       lights.partial_light()

  def dim_lights(self):
    self.logger.debuglog("class Hue: dim lights")
    self.last_state = "dimmed"
    if self.settings.light == 0:
      self.light.dim_light()
    elif self.settings.light > 0:
        for l in self.light:
          #xbmc.sleep(1)
          l.dim_light()
    
  def brighter_lights(self):
    self.logger.debuglog("class Hue: brighter lights")
    self.last_state = "brighter"
    if self.settings.light == 0:
      self.light.brighter_light()
    elif self.settings.light > 0:
        for l in self.light:
          l.dim_light()
          #xbmc.sleep(1)
          l.brighter_light()
      
  def partial_lights(self):
    self.logger.debuglog("class Hue: partial lights")
    self.last_state = "partial"
    if self.settings.light == 0:
      self.light.partial_light()
    elif self.settings.light > 0:
        for l in self.light:
          #xbmc.sleep(1)
          l.partial_light()
      
  def update_settings(self):
    self.logger.debuglog("class Hue: update settings")
    self.logger.debuglog(self.settings)
    if self.settings.light == 0:
      self.logger.debuglog("creating Group instance")
      self.light = Group(self.settings)
    elif self.settings.light > 0:
      self.logger.debuglog("creating Light instances")      
      #hps
      #
      bulbs = lifx.get_lights()
      #print(bulbs)
      self.light = [None] * len(bulbs)
      self.logger.debuglog("Number of bulbs " + str(len(self.light)))

      index = 0
      for bulb in bulbs:
        #print(bulb.get_label())
        # Todo - check the light id from settings
        self.logger.debuglog("Discovered " + str(bulb.get_label()))
        self.light[index] = Light(bulb, self.settings)
        index = index + 1
        #xbmc.sleep(1)
        

      '''
      self.light = [None] * self.settings.light
      self.light[0] = Light(self.settings.light1_id, self.settings)
      if self.settings.light > 1:
        xbmc.sleep(1)
        self.light[1] = Light(self.settings.light2_id, self.settings)
      if self.settings.light > 2:
        xbmc.sleep(1)
        self.light[2] = Light(self.settings.light3_id, self.settings)
      '''

    #ambilight dim
    if self.settings.ambilight_dim:
      if self.settings.ambilight_dim_light == 0:
        self.logger.debuglog("creating Group instance for ambilight dim")
        self.ambilight_dim_light = Group(self.settings, self.settings.ambilight_dim_group_id)
      elif self.settings.ambilight_dim_light > 0:
        self.logger.debuglog("creating Light instances for ambilight dim")

        bulbs = lifx.get_lights()
        self.logger.debuglog("Number of bulbs " + str(lifx.num_lights))

        self.ambilight_dim_light = [None] * len(bulbs)
        index = 0
        for bulb in bulbs:
          # Todo - check the light id from settings
          self.ambilight_dim_light[index] = Light(bulb, self.settings)
          index = index + 1
          #xbmc.sleep(1)
        
        '''
        self.ambilight_dim_light = [None] * self.settings.ambilight_dim_light
        self.ambilight_dim_light[0] = Light(self.settings.ambilight_dim_light1_id, self.settings)
        if self.settings.ambilight_dim_light > 1:
          xbmc.sleep(1)
          self.ambilight_dim_light[1] = Light(self.settings.ambilight_dim_light2_id, self.settings)
        if self.settings.ambilight_dim_light > 2:
          xbmc.sleep(1)
          self.ambilight_dim_light[2] = Light(self.settings.ambilight_dim_light3_id, self.settings)
        '''

class Light:
  start_setting = None
  group = False
  livingwhite = False
  fullSpectrum = False

  # light_id is now bulb from get_lights()
  def __init__(self, light_id, settings):
    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    self.bridge_ip    = settings.bridge_ip
    self.bridge_user  = settings.bridge_user
    self.mode         = settings.mode
    self.light        = light_id
    self.dim_time     = settings.dim_time
    self.proportional_dim_time = settings.proportional_dim_time
    self.override_hue = settings.override_hue
    self.dimmed_bri   = settings.dimmed_bri
    self.dimmed_hue   = settings.dimmed_hue
    self.override_sat = settings.override_sat
    self.dimmed_sat   = settings.dimmed_sat
    self.undim_sat   = settings.undim_sat
    self.override_paused = settings.override_paused
    self.paused_bri   = settings.paused_bri
    self.undim_bri    = settings.undim_bri
    self.undim_hue    = settings.undim_hue
    self.override_undim_bri = settings.override_undim_bri
    self.force_light_on = settings.force_light_on
    self.force_light_group_start_override = settings.force_light_group_start_override

    self.onLast = True
    self.hueLast = 0
    self.satLast = 0
    self.briLast = 0

    self.get_current_setting()
    self.s = requests.Session()

  def get_current_setting(self):
    self.start_setting = {}

    #HPS
    #self.logger.debuglog("current_setting: %r" % self.light)
    power_on = True if self.light.get_power() > 0 else False
    self.start_setting['on'] = power_on
    #HSBK
    color = self.light.get_color()
    self.start_setting['bri'] = int(color[2]*255/65535)
    
    self.onLast = self.start_setting['on']
    self.briLast = self.start_setting['bri']
    
    #modelid = j['modelid']
    self.fullSpectrum = True
    self.livingwhite = False

    self.start_setting['hue'] = int(color[0])
    self.start_setting['sat'] = int(color[1]*255/65535)
    self.hueLast = self.start_setting['hue']
    self.satLast = self.start_setting['sat']

    self.logger.debuglog("light %s start settings: %s" % (self.light.get_label(), self.start_setting))

  # def set_light(self, data):
  #   self.logger.debuglog("set_light: %s: %s" % (self.light, data))
  #   self.request_url_put("http://%s/api/%s/lights/%s/state" % \
  #     (self.bridge_ip, self.bridge_user, self.light), data=data)

  def set_light2(self, hue, sat, bri, duration=None):

    if self.start_setting["on"] == False and self.force_light_on == False:
      # light was not on, and settings say we should not turn it on
      # self.logger.debuglog("light %s was off, settings say we should not turn it on" % self.light.get_label())
      return

    data = {}

    if not self.livingwhite:
      if not hue is None:
        data["hue"] = hue
        self.hueLast = hue
      elif not self.hueLast is None:
        data["hue"] = self.hueLast
      else:
        data["hue"] = self.start_setting["hue"]
        self.hueLast = self.start_setting["hue"]

      if not sat is None:
        data["sat"] = sat
        self.satLast = sat
      elif not self.satLast is None:
        data["sat"] = self.satLast
      else:
        data["sat"] = self.start_setting["sat"]
        self.satLast = self.start_setting["sat"]

    #self.logger.debuglog("light %s: onLast: %s, briLast: %s" % (self.light.get_label(), self.onLast, self.briLast))

    '''
    if bri > 0:
      if self.onLast == False: #don't send on unless we have to (performance)
        data["on"] = True
        self.onLast = True
      data["bri"] = bri
    else:
      data["on"] = False
      self.onLast = False
    '''
    if not bri is None:
      data["bri"] = bri
    elif not self.briLast is None:
      data["bri"] = self.briLast
    else:
      data["bri"] = self.start_setting["bri"]

    time = 0
    if duration is None:
      if self.proportional_dim_time and self.mode != 0: #only if its not ambilight mode too
        #self.logger.debuglog("last %r, next %r, start %r, finish %r" % (self.briLast, bri, self.start_setting['bri'], self.dimmed_bri))
        difference = abs(float(bri) - self.briLast)
        total = float(self.start_setting['bri']) - self.dimmed_bri
        if total != 0:
          proportion = difference / total
          time = int(round(proportion * self.dim_time))
      else:
        time = self.dim_time
    else:
      time = duration

    self.briLast = data["bri"] # moved after time calclation to know the previous value (important)

    data["transitiontime"] = time
    
    dataString = json.dumps(data)

    self.logger.debuglog("set_light2: %s: %s" % (self.light.get_label(), dataString))
    

    #if data["on"]:
    #  self.light.set_power("on", time*100, rapid=True)

    # color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
    k = 5500
    color = [int(data["hue"]),int(data["sat"]*65535/255),int(data["bri"]*65535/255),k]
    self.logger.debuglog("set_light2: %s: %s" % (self.light.get_label(), color))

    # Lifxlan duration is in miliseconds
    self.light.set_color(color, data["transitiontime"]*100, rapid=False)
    #self.request_url_put("http://%s/api/%s/lights/%s/state" % \
    #  (self.bridge_ip, self.bridge_user, self.light), data=dataString)

  def flash_light(self):
    self.dim_light()
    sleep(self.dim_time/10)
    self.brighter_light()

  def dim_light(self):
    if self.override_hue:
      hue = self.dimmed_hue
    else:
      hue = None

    if self.override_sat:
      sat = self.dimmed_sat
    else:
      sat = None

    self.set_light2(hue, sat, self.dimmed_bri)

  def brighter_light(self):
    if self.override_undim_bri:
      bri = self.undim_bri
    else:
      bri = self.start_setting['bri']

    if not self.livingwhite:
      if self.override_sat:
        sat = self.undim_sat
      else:
        sat = self.start_setting['sat']
      if self.override_hue:
        hue = self.undim_hue
      else:
        hue = self.start_setting['hue']
    else:
      sat = None
      hue = None

    self.set_light2(hue, sat, bri)

  def partial_light(self):
    if self.override_paused:
      bri = self.paused_bri

      if not self.livingwhite:
        if self.override_sat:
          sat = self.undim_sat
        else:
          sat = self.start_setting['sat']

        if self.override_hue:
          hue = self.undim_hue
        else:
          hue = self.start_setting['hue']
      else:
        sat = None
        hue = None

      self.set_light2(hue, sat, bri)
    else:
      #not enabled for dimming on pause
      self.brighter_light()

class Group(Light):
  group = True
  lights = {}

  def __init__(self, settings, group_id=None):
    if group_id==None:
      self.group_id = settings.group_id
    else:
      self.group_id = group_id

    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    Light.__init__(self, settings.light1_id, settings)

    #hps
    bulbs = lifx.get_lights()
    for light in  bulbs:
      if self.group_id.lower() in light.get_group_label().lower():
        tmp = Light(light, settings)
        tmp.get_current_setting()
        self.logger.debuglog("Adding %s to the group" % light.get_label())
        #if tmp.start_setting['on']: #TODO: Why only add these if they're on?
        self.lights[light] = tmp

    '''
    for light in self.get_lights():
      tmp = Light(light, settings)
      tmp.get_current_setting()
      #if tmp.start_setting['on']: #TODO: Why only add these if they're on?
      self.lights[light] = tmp
    '''

  def __len__(self):
    return 0

  def set_light2(self, hue, sat, bri, duration=None):

    if self.start_setting["on"] == False and self.force_light_on == False:
      # light was not on, and settings say we should not turn it on
      self.logger.debuglog("group %s was off, settings say we should not turn it on" % self.group_id)
      return

    data = {}

    if not self.livingwhite:
      if not hue is None:
        data["hue"] = hue
        self.hueLast = hue
      elif not self.hueLast is None:
        data["hue"] = self.hueLast
      else:
        data["hue"] = self.start_setting["hue"]
        self.hueLast = self.start_setting["hue"]

      if not sat is None:
        data["sat"] = sat
        self.satLast = sat
      elif not self.satLast is None:
        data["sat"] = self.satLast
      else:
        data["sat"] = self.start_setting["sat"]
        self.satLast = self.start_setting["sat"]

    if not bri is None:
      data["bri"] = bri
    elif not self.briLast is None:
      data["bri"] = self.briLast
    else:
      data["bri"] = self.start_setting["bri"]

    time = 0
    if duration is None:
      if self.proportional_dim_time and self.mode != 0: #only if its not ambilight mode too
        #self.logger.debuglog("last %r, next %r, start %r, finish %r" % (self.briLast, bri, self.start_setting['bri'], self.dimmed_bri))
        difference = abs(float(bri) - self.briLast)
        total = float(self.start_setting['bri']) - self.dimmed_bri
        proportion = difference / total
        time = int(round(proportion * self.dim_time))
      else:
        time = self.dim_time
    else:
      time = duration

    self.briLast = bri # moved after time calculation
    data["transitiontime"] = time

    dataString = json.dumps(data)

    self.logger.debuglog("set_light2: group_id %s: %s" % (self.group_id, dataString))

    for group_light in self.lights:
      if not (self.lights[group_light].start_setting["on"] == False and self.force_light_on == False):
      # Lifxlan duration is in miliseconds
        #self.lights[group_light].set_power("on", data["transitiontime"]*100, rapid=False)

        # color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
        k = 5500
        color = [int(data["hue"]), int(data["sat"]*65535/255), int(data["bri"]*65535/255), k]
        # Lifxlan duration is in miliseconds
        #self.lights[group_light].set_color(color, data["transitiontime"]*100, rapid=False)
        group_light.set_color(color, data["transitiontime"] * 100, rapid=False)

  # def dim_light(self):
  #   for light in self.lights:
  #       self.lights[light].dim_light()

  # def brighter_light(self):
  #     for light in self.lights:
  #       self.lights[light].brighter_light()

  # def partial_light(self):
  #     for light in self.lights:
  #       self.lights[light].partial_light()

  def get_current_setting(self):
    
    self.start_setting = {}

    #HPS
    #self.logger.debuglog("current_setting: %r" % self.light)
    self.start_setting['on'] = False

    if self.force_light_group_start_override: #override default just in case there is one light on
      for l in self.lights:
        #self.logger.debuglog("light: %s" % self.lights[l])
        if self.lights[l].start_setting['on']:
          self.logger.debuglog("light %s was on, so the group will start as on" % l)
          self.start_setting['on'] = True
          break

    self.start_setting['bri'] = 0
    self.start_setting['hue'] = 0
    self.start_setting['sat'] = 0

    if self.force_light_group_start_override:
      for l in self.lights:
        if self.start_setting['bri'] < self.lights[l].start_setting['bri']:
          self.start_setting['bri'] = self.lights[l].start_setting['bri'] #take the brightest of the group.
          self.start_setting['hue'] = self.lights[l].start_setting['hue']
          self.start_setting['sat'] = self.lights[l].start_setting['sat']

    self.onLast = self.start_setting['on']
    self.briLast = self.start_setting['bri']
    self.hueLast = self.start_setting['hue']
    self.satLast = self.start_setting['sat']

    #modelid = j['modelid']
    self.fullSpectrum = True
    self.livingwhite = False

    self.logger.debuglog("light %s start settings: %s" % (self.group_id, self.start_setting))

#todo - remove this fn and requests import
  def request_url_put(self, url, data):
    try:
      response = self.s.put(url, data=data)
      self.logger.debuglog("response: %s" % response)
    except Exception as e:
      # probably a timeout
      self.logger.debuglog("WARNING: Request fo bridge failed")
      pass

