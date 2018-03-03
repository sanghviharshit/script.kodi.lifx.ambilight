import xbmc
import socket
import json
from time import sleep
import logging

from tools import *
from lifxlan import *

lifx = None

class Hue:
  params = None
  connected = None
  last_state = None
  light = None
  ambilight_dim_light = None

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

    if self.params == {}:
      self.test_connection()
    elif self.params['action'] == "discover":
      self.logger.debuglog("Starting discovery")
      notify("Lifx Bulbs Discovery", "Starting")
      self.test_connection()
      notify("Lifx Bulbs Discovery", "Finished")
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

    if self.connected:
      self.update_settings()
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
    self.logger.debuglog("Testing Connection")
    #self.logger.debuglog("Discovering lights...")
    bulbs = lifx.get_lights()
    if len(bulbs) > 0:
      self.logger.debuglog("Found {0} Lifx Bulbs".format(str(len(bulbs))))
      notify("Kodi Lifx", "Found {0} Lifx Bulbs".format(str(len(bulbs))))
      self.connected = True
    else:
      self.logger.debuglog("No Lifx bulbs found")
      notify("Kodi Lifx", "No Lifx bulbs found")
      self.connected = False
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
          #l.dim_light()  #why?
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
    self.logger.debuglog("Class Hue: update settings")
    self.logger.debuglog(self.settings)
    if self.settings.light == 0:
      self.logger.debuglog("creating Group instance")
      self.light = Group(self.settings, self.settings.group_id)
      self.logger.debuglog("Added %s bulbs to the Group %s" %(str(len(self.light.lights)), self.settings.group_id))
    elif self.settings.light > 0:
      self.logger.debuglog("creating Light instances")
      bulbs = lifx.get_lights()
      self.light = [None] * len(bulbs)
      self.logger.debuglog("Number of bulbs " + str(len(self.light)))
      index = 0
      for bulb in bulbs:
        #print(bulb.get_label())
        self.logger.debuglog("Discovered " + str(bulb.get_label()))
        self.light[index] = Light(bulb, self.settings)
        index = index + 1
        #xbmc.sleep(1)

    #ambilight dim
    if self.settings.ambilight_dim:
      if self.settings.ambilight_dim_light == 0:
        self.logger.debuglog("creating Group instance for ambilight dim")
        self.ambilight_dim_light = Group(self.settings, self.settings.ambilight_dim_group_id)
        self.logger.debuglog("Added %s bulbs to the Group %s" % (str(len(self.ambilight_dim_light.lights)), self.settings.ambilight_dim_group_id))
      elif self.settings.ambilight_dim_light > 0:
        self.logger.debuglog("creating Light instances for ambilight dim")
        bulbs = lifx.get_lights()
        self.ambilight_dim_light = [None] * len(bulbs)
        self.logger.debuglog("Number of bulbs " + str(len(self.light)))
        index = 0
        for bulb in bulbs:
          # Todo - check the light id from settings
          self.ambilight_dim_light[index] = Light(bulb, self.settings)
          index = index + 1
          #xbmc.sleep(1)


class Light:

  def __init__(self, light_id, settings):
    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    self.start_setting = None
    self.group = False
    self.livingwhite = False
    self.fullSpectrum = False

    self.mode         = settings.mode
    self.light        = light_id  ## light_id is now bulb from get_lights()
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

    self.override_kel = settings.override_kel
    self.dimmed_kel = settings.dimmed_kel
    self.undim_kel = settings.undim_kel

    self.force_light_on = settings.force_light_on
    self.force_light_group_start_override = settings.force_light_group_start_override

    self.onLast = True
    self.hueLast = 0
    self.satLast = 0
    self.briLast = 0
    self.kelLast = 0

    self.get_current_setting()

  def get_current_setting(self):
    self.start_setting = {}

    #HPS
    #self.logger.debuglog("current_setting: %r" % self.light)
    power_on = True if self.light.get_power() > 0 else False
    self.start_setting['on'] = power_on
    #HSBK
    color = self.light.get_color()
    self.start_setting['hue'] = int(color[0])
    self.start_setting['sat'] = int(color[1]*255/65535)
    self.start_setting['bri'] = int(color[2]*255/65535)
    self.start_setting['kel'] = int(color[3])

    self.onLast = self.start_setting['on']
    self.hueLast = self.start_setting['hue']
    self.satLast = self.start_setting['sat']
    self.briLast = self.start_setting['bri']
    self.kelLast = self.start_setting['kel']

    self.fullSpectrum = True
    self.livingwhite = False

    self.multiplier = 100

    self.logger.debuglog("light %s start settings: %s" % (self.light.get_label(), self.start_setting))

  def set_light2(self, hue, sat, bri, kel, power=None, duration=None):

    if self.start_setting["on"] == False and self.force_light_on == False:
      # light was not on, and settings say we should not turn it on
      self.logger.debuglog("light %s was off, settings say we should not turn it on" % self.light.get_label())
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

    if self.onLast == False:  # don't send on unless we have to (performance)
      data["on"] = True
      self.onLast = True
    else:
      data["on"] = False

    if not bri is None:
      data["bri"] = bri
    elif not self.briLast is None:
      data["bri"] = self.briLast
    else:
      data["bri"] = self.start_setting["bri"]
      self.briLast = data["bri"]

    if not kel is None:
      data["kel"] = kel
    elif hue > 0 or sat > 0:
      data["kel"] = 3500  # Set kelvin to neutral
      # self.logger.debuglog("Light: %s: kel=neutral - 3500" % (self.light.get_label()))
    elif sat == 0:
      data["kel"] = 5500  # Set kelvin to White Daylight if saturation is 0
    elif not self.kelLast is None:
      data["kel"] = self.kelLast
    else:
      data["kel"] = self.start_setting["kel"]

    self.kelLast = data["kel"]

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

    self.briLast = data["bri"] # moved after time calculation to know the previous value (important)
    self.kelLast = data["kel"]

    data["transitiontime"] = time

    dataString = json.dumps(data)

    #self.logger.debuglog("set_light2: %s: %s" % (self.light.get_label(), dataString))


    if data["on"]:
      self.light.set_power(True, rapid=False)

    if power==False:
      self.light.set_power(False, rapid=False)

    # color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
    # 65535/255 = 257
    color = [int(data["hue"]),int(data["sat"]*257),int(data["bri"]*257),int(data["kel"])]
    #color_log = [int(data["hue"]*360/65535),int(data["sat"]*100/255),int(data["bri"]*100/255),int(data["kel"])]
    #self.logger.debuglog("set_light2: %s: %s  (%s ms)" % (self.light.get_label(), color_log, data["transitiontime"]*self.multiplier))

    # Lifxlan duration is in miliseconds
    try:
        self.light.set_color(color, data["transitiontime"]*self.multiplier, rapid=False)
    except WorkflowException:
        self.logger.debuglog("set_color: %s failed to respond to a request" % self.light.get_label())
    #self.request_url_put("http://%s/api/%s/lights/%s/state" % \
    #  (self.bridge_ip, self.bridge_user, self.light), data=dataString)

  def flash_light(self):
    self.dim_light()
    sleep(self.dim_time/10)
    self.brighter_light()

  def dim_light(self):
    if self.override_kel:
      kel = self.dimmed_kel
    else:
      kel = None

    if self.override_hue:
      hue = self.dimmed_hue
    else:
      hue = None

    if self.override_sat:
      sat = self.dimmed_sat
    else:
      sat = None

    self.set_light2(hue, sat, self.dimmed_bri, kel, power=None, duration=None)

  def brighter_light(self):

    if self.override_undim_bri:
      bri = self.undim_bri
    else:
      bri = self.start_setting['bri']

    power = None
    if self.force_light_on:
      self.logger.debuglog("%s was off, so will be powered off" %(self.light.get_label()))
      power = self.start_setting['on']

    if not self.livingwhite:
      if self.override_kel:
        kel = self.undim_kel
      else:
        kel = self.start_setting['kel']
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

    self.set_light2(hue, sat, bri, kel, power, duration=None)

  def partial_light(self):
    if self.override_paused:
      bri = self.paused_bri

      if not self.livingwhite:
        if self.override_kel:
          kel = self.undim_kel
        else:
          kel = self.start_setting['kel']

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

      self.set_light2(hue, sat, bri, kel, power=None, duration=None)
    else:
      #not enabled for dimming on pause
      self.brighter_light()

class Group(Light):
  group = True

  def __init__(self, settings, group_id=None):
    self.lights = {}

    if group_id==None:
      self.group_id = settings.group_id
    else:
      self.group_id = group_id

    self.mode         = settings.mode
    self.dim_time = settings.dim_time
    self.proportional_dim_time = settings.proportional_dim_time
    self.override_hue = settings.override_hue
    self.dimmed_bri = settings.dimmed_bri
    self.dimmed_hue = settings.dimmed_hue
    self.override_sat = settings.override_sat
    self.dimmed_sat = settings.dimmed_sat
    self.undim_sat = settings.undim_sat
    self.override_paused = settings.override_paused
    self.paused_bri = settings.paused_bri
    self.undim_bri = settings.undim_bri
    self.undim_hue = settings.undim_hue
    self.override_undim_bri = settings.override_undim_bri
    self.force_light_on = settings.force_light_on
    self.force_light_group_start_override = settings.force_light_group_start_override

    self.override_kel = settings.override_kel
    self.dimmed_kel = settings.dimmed_kel
    self.undim_kel = settings.undim_kel

    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    #Light.__init__(self, settings.light1_id, settings)

    #hps
    bulbs = lifx.get_lights()
    for light in bulbs:
      if self.group_id.lower() in light.get_group_label().lower():
        tmp = Light(light, settings)
        tmp.get_current_setting()
        self.logger.debuglog("Adding %s to the group - %s" % (light.get_label(), self.group_id))
        #if tmp.start_setting['on']: #TODO: Why only add these if they're not on?
        self.lights[light] = tmp

    self.get_current_setting()

  def __len__(self):
    return 0

  def set_light2(self, hue, sat, bri, kel, power=None, duration=None):
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

    if self.onLast == False:  # don't send on unless we have to (performance)
      data["on"] = True
      self.onLast = True
    else:
      data["on"] = False

    if not bri is None:
      data["bri"] = bri
    elif not self.briLast is None:
      data["bri"] = self.briLast
    else:
      data["bri"] = self.start_setting["bri"]
      self.briLast = data["bri"]

    if not kel is None:
      data["kel"] = kel
      #self.logger.debuglog("Group: %s: kel - %s" % (self.group_id, data["kel"]))
    elif hue > 0 or sat > 0:
      data["kel"] = 3500  # Set kelvin to neutral
      # self.logger.debuglog("Group: %s: kel=neutral - 3500" % (self.group_id))
      self.kelLast = data["kel"]
    elif not self.kelLast is None:
      data["kel"] = self.kelLast
      #self.logger.debuglog("Group: %s: kel=kelLast - %s" % (self.group_id, data["kel"]))
    else:
      data["kel"] = self.start_setting["kel"]
      #self.logger.debuglog("Group: %s: kel=start_setting[kelLast] - %s" % (self.group_id, data["kel"]))
      self.kelLast = data["kel"]


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


    self.briLast = data["bri"]  # moved after time calclation to know the previous value (important)
    self.kelLast = data["kel"]  # moved after time calclation to know the previous value (important)

    data["transitiontime"] = time

    dataString = json.dumps(data)

    #self.logger.debuglog("Group: %s: number of bulbs - %s" % (self.group_id, len(self.lights)))

    # color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
    color = [int(data["hue"]), int(data["sat"]*257), int(data["bri"]*257), int(data["kel"])]
    #color_log = [int(data["hue"]*360/65535),int(data["sat"]*100/255),int(data["bri"]*100/255),int(data["kel"])]
    #self.logger.debuglog("set_light2: %s: %s  (%s ms)" % (self.group_id, color_log, data["transitiontime"]*self.multiplier))
    for group_light in self.lights:
      # Lifxlan duration is in miliseconds
      #self.lights[group_light].set_power("on", data["transitiontime"]*100, rapid=False)
      if data["on"]:
        group_light.set_power(True, rapid=False)

      # Lifxlan duration is in miliseconds
      try:
          group_light.set_color(color, data["transitiontime"]*self.multiplier, rapid=False)
      except WorkflowException:
        self.logger.debuglog("set_color: %s failed to respond to a request" % self.group_id)

  def dim_light(self):
    for light in self.lights:
      self.lights[light].dim_light()

  def brighter_light(self):
    for light in self.lights:
      self.lights[light].brighter_light()

  def partial_light(self):
    for light in self.lights:
      self.lights[light].partial_light()

  def get_current_setting(self):

    self.start_setting = {}

    #HPS
    #self.logger.debuglog("current_setting: %r" % self.light)
    self.start_setting['on'] = False

    if self.force_light_group_start_override: #override default just in case there is one light on
      for l in self.lights:
        #self.logger.debuglog("light: %s" % self.lights[l])
        if self.lights[l].start_setting['on']:
          self.logger.debuglog("light %s was on, so the group will start as on" % l.get_label())
          self.start_setting['on'] = True
          break

    self.start_setting['bri'] = 0
    self.start_setting['hue'] = 0
    self.start_setting['sat'] = 0
    self.start_setting['kel'] = 3500

    if self.force_light_group_start_override:
      for l in self.lights:
        if self.start_setting['bri'] < self.lights[l].start_setting['bri']:
          self.start_setting['bri'] = self.lights[l].start_setting['bri'] #take the brightest of the group.
          self.start_setting['hue'] = self.lights[l].start_setting['hue']
          self.start_setting['sat'] = self.lights[l].start_setting['sat']
          self.start_setting['kel'] = self.lights[l].start_setting['kel']

    self.onLast = self.start_setting['on']
    self.hueLast = self.start_setting['hue']
    self.satLast = self.start_setting['sat']
    self.briLast = self.start_setting['bri']
    self.kelLast = self.start_setting['kel']

    #modelid = j['modelid']
    self.fullSpectrum = True
    self.livingwhite = False

    # Used for transition duration
    self.multiplier = 100

    self.logger.debuglog("Group %s start settings: %s" % (self.group_id, self.start_setting))
