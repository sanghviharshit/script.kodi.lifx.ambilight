import xbmc
import xbmcgui
import xbmcaddon
import json
import time
import sys
import colorsys
import os
import datetime
import math

from lifxlan import *
from copy import copy
from time import sleep, time

lifx = LifxLAN()
bulbs = lifx.get_lights()

def notify(title, msg=""):
  #global __icon__
  xbmc.executebuiltin("XBMC.Notification(%s, %s, 2)" % (title, msg))

try:
  import requests
except ImportError:
  notify("Kodi Hue", "ERROR: Could not import Python requests")

def get_version():
  # prob not the best way...
  global __xml__
  try:
    for line in open(__xml__):
      if line.find("ambilight") != -1 and line.find("version") != -1:
        return line[line.find("version=")+9:line.find(" provider")-1]
  except:
    return "unknown"

class Logger:
  scriptname = "Kodi Lifx Ambilight"
  enabled = True
  debug_enabled = False

  def log(self, msg):
    if self.enabled:
      xbmc.log("%s: %s" % (self.scriptname, msg))

  def debuglog(self, msg):
    if self.debug_enabled:
      self.log("DEBUG %s" % msg)

  def debug(self):
    self.debug_enabled = True

  def disable(self):
    self.enabled = False

try:
  import requests
except ImportError:
  xbmc.log("ERROR: Could not locate required library requests")
  notify("Kodi Hue", "ERROR: Could not import Python requests")

xbmc.log("Kodi Hue service started, version: %s" % get_version())

class settings():
  def __init__( self, *args, **kwargs ):
    self.debug = True
    self.mode = 0
    self.ambilight_min = 10000
    self.ambilight_max = 30000
    self.misc_disableshort = False

###################################
'''
useLegacyApi   = True

refreshRate = 300;
min_brightness = int(10)*655;
max_brightness = int(20)*655;

if useLegacyApi:
	capture.capture(32, 32, xbmc.CAPTURE_FLAG_CONTINUOUS)


class PlayerMonitor( xbmc.Player ):
	def __init__( self, *args, **kwargs ):
		xbmc.Player.__init__( self )

	def onPlayBackStarted( self ):
		if not useLegacyApi:
			capture.capture(32, 32)

original_powers = lifxlan.get_power_all_lights()


while not xbmc.abortRequested:
	xbmc.sleep(refreshRate)
	if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
		width = capture.getWidth();
		height = capture.getHeight();
		pixels = capture.getImage(1000);

		if useLegacyApi:
			capture.waitForCaptureStateChangeEvent(1000)
			
		pixels = capture.getImage(1000)

		red = [];
		green = [];
		blue = [];

                color = []

		for y in range(height):
			row = width * y * 4
			for x in range(width):
				red.append(pixels[row + x * 4 + 2]);
				green.append(pixels[row + x * 4 + 1]);
				blue.append(pixels[row + x * 4]);


		red = (sum(red)/len(red))/255.00;
		green = (sum(green)/len(green))/255.00;
		blue = (sum(blue)/len(blue))/255.00;

		hsb = colorsys.rgb_to_hsv(red, green, blue);

		huevalue = int(hsb[0]*65535);
		satvalue = int(hsb[1]*65535);
		brightnessvalue = int(hsb[2]*65535);

		if brightnessvalue < min_brightness:
			brightnessvalue = min_brightness;
		elif brightnessvalue > max_brightness:
			brightnessvalue = max_brightness;
		else:
			brightnessvalue = brightnessvalue;

                color.append(huevalue)
                color.append(satvalue)
                color.append(brightnessvalue)
                color.append(4000)
                print color;
		try:
			lifxlan.set_color_all_lights(color, rapid=False)
		except:
			print "Caught exception socket.error"

print("Restoring original power to all lights...")
for light, power in original_powers:
    light.set_power(power)

##################################
'''

capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# BGRA or RGBA
# xbmc.log("Hue Capture Image format: %s" % fmt)
fmtRGBA = fmt == 'RGBA'

class MyMonitor( xbmc.Monitor ):
  def __init__( self, *args, **kwargs ):
    xbmc.Monitor.__init__( self )

  def onSettingsChanged( self ):
    hue.settings.mode = 0
    logger.debuglog("running in mode %s" % str(hue.settings.mode))
    last = datetime.datetime.now()
#    hue.settings.readxml()
#    hue.update_settings()

monitor = MyMonitor()

class MyPlayer(xbmc.Player):
  duration = 0
  playingvideo = None

  def __init__(self):
    xbmc.Player.__init__(self)
  
  def onPlayBackStarted(self):
    if self.isPlayingVideo():
      self.playingvideo = True
      self.duration = self.getTotalTime()
      state_changed("started", self.duration)

  def onPlayBackPaused(self):
    if self.isPlayingVideo():
      self.playingvideo = False
      state_changed("paused", self.duration)

  def onPlayBackResumed(self):
    if self.isPlayingVideo():
      self.playingvideo = True
      state_changed("resumed", self.duration)

  def onPlayBackStopped(self):
    if self.playingvideo:
      self.playingvideo = False
      state_changed("stopped", self.duration)

  def onPlayBackEnded(self):
    if self.playingvideo:
      self.playingvideo = False
      state_changed("stopped", self.duration)

class Hue:
  params = None
  connected = None
  last_state = None
  light = None
  dim_group = None
  original_powers = None
  original_colors = None

  def __init__(self, settings, args):
    self.logger = Logger()
    settings.debug = True
    if settings.debug:
      self.logger.debug()
    self.settings = settings

    self.logger.debuglog("Starting discover")
    self.test_connection()

  def test_connection(self):
    # test power control
    print("Discovering lights...")
    self.original_powers = lifx.get_power_all_lights()
    self.original_colors = lifx.get_color_all_lights()
    notify("Kodi Hue", "Connected")
    self.connected = True

  def dim_lights(self):
    self.logger.debuglog("class Hue: dim lights")
    self.last_state = "dimmed"
    for bulb, color in self.original_colors:
                dim = list(copy(color))
                half_bright = int(dim[2]/3)
                dim[2] = half_bright if half_bright >= 10000 else 10000
                bulb.set_color(dim, 300, rapid=True)

  def brighter_lights(self):
    self.logger.debuglog("class Hue: brighter lights")
    self.last_state = "brighter"
    for bulb, color in self.original_colors:
                dim = list(copy(color))
                full_bright = 65000
                dim[2] = full_bright
                bulb.set_color(dim, 300, rapid=True)

  def partial_lights(self):
    self.logger.debuglog("class Hue: partial lights")
    self.last_state = "partial"
    for bulb, color in self.original_colors:
                dim = list(copy(color))
                half_bright = int(dim[2]/2)
                dim[2] = half_bright if half_bright >= 10000 else 10000
                bulb.set_color(dim, 300, rapid=True)

  def update_settings(self):
    self.logger.debuglog("class Hue: update settings")
  
  def restore_bulbs(self):
    self.logger.debuglog("class Hue: restore bulbs")
    print("Restoring original color to all lights...")
    for light, color in self.original_colors:
        light.set_color(color)

    print("Restoring original power to all lights...")
    for light, power in self.original_powers:
        light.set_power(power)

class HSVRatio:
  cyan_min = float(4.5/12.0)
  cyan_max = float(7.75/12.0)

  def __init__(self, hue=0.0, saturation=0.0, value=0.0, ratio=0.0):
    self.h = hue
    self.s = saturation
    self.v = value
    self.ratio = ratio

  def average(self, h, s, v):
    self.h = (self.h + h)/2
    self.s = (self.s + s)/2
    self.v = (self.v + v)/2

  def averageValue(self, overall_value):
    if self.ratio > 0.5:
      self.v = self.v * self.ratio + overall_value * (1-self.ratio)
    else:
      self.v = (self.v + overall_value)/2
    

  def hue(self, fullSpectrum):
    if fullSpectrum != True:
      if self.s > 0.01:
        if self.h < 0.5:
          #yellow-green correction
          self.h = self.h * 1.17
          #cyan-green correction
          if self.h > self.cyan_min:
            self.h = self.cyan_min
        else:
          #cyan-blue correction
          if self.h < self.cyan_max:
            self.h = self.cyan_max

    h = int(self.h*65535) # on a scale from 0 <-> 65535
    s = int(self.s*65535)
    v = int(self.v*65535)

    if v < hue.settings.ambilight_min:
      v = hue.settings.ambilight_min
    if v > hue.settings.ambilight_max:
      v = hue.settings.ambilight_max
    return h, s, v

  def __repr__(self):
    return 'h: %s s: %s v: %s ratio: %s' % (self.h, self.s, self.v, self.ratio)

class Screenshot:
  def __init__(self, pixels, capture_width, capture_height):
    self.pixels = pixels
    self.capture_width = capture_width
    self.capture_height = capture_height

  def most_used_spectrum(self, spectrum, saturation, value, size, overall_value):
    # color bias/groups 6 - 36 in steps of 3
    settings.color_bias = 0
    colorGroups = settings.color_bias
    if colorGroups == 0:
      colorGroups = 1
    colorHueRatio = 360 / colorGroups

    hsvRatios = []
    hsvRatiosDict = {}

    for i in range(360):
      if spectrum.has_key(i):
        #shift index to the right so that groups are centered on primary and secondary colors
        colorIndex = int(((i+colorHueRatio/2) % 360)/colorHueRatio)
        pixelCount = spectrum[i]

        if hsvRatiosDict.has_key(colorIndex):
          hsvr = hsvRatiosDict[colorIndex]
          hsvr.average(i/360.0, saturation[i], value[i])
          hsvr.ratio = hsvr.ratio + pixelCount / float(size)

        else:
          hsvr = HSVRatio(i/360.0, saturation[i], value[i], pixelCount / float(size))
          hsvRatiosDict[colorIndex] = hsvr
          hsvRatios.append(hsvr)

    colorCount = len(hsvRatios)
    if colorCount > 1:
      # sort colors by popularity
      hsvRatios = sorted(hsvRatios, key=lambda hsvratio: hsvratio.ratio, reverse=True)
      # logger.debuglog("hsvRatios %s" % hsvRatios)
      
      #return at least 3
      if colorCount == 2:
        hsvRatios.insert(0, hsvRatios[0])
      
      hsvRatios[0].averageValue(overall_value)
      hsvRatios[1].averageValue(overall_value)
      hsvRatios[2].averageValue(overall_value)
      return hsvRatios

    elif colorCount == 1:
      hsvRatios[0].averageValue(overall_value)
      return [hsvRatios[0]] * 3

    else:
      return [HSVRatio()] * 3

  def spectrum_hsv(self, pixels, width, height):
    spectrum = {}
    saturation = {}
    value = {}

    size = int(len(pixels)/4)
    pixel = 0

    i = 0
    s, v = 0, 0
    r, g, b = 0, 0, 0
    tmph, tmps, tmpv = 0, 0, 0
    
    for i in range(size):
      if fmtRGBA:
        r = pixels[pixel]
        g = pixels[pixel + 1]
        b = pixels[pixel + 2]
      else: #probably BGRA
        b = pixels[pixel]
        g = pixels[pixel + 1]
        r = pixels[pixel + 2]
      pixel += 4

      tmph, tmps, tmpv = colorsys.rgb_to_hsv(float(r/255.0), float(g/255.0), float(b/255.0))
      s += tmps
      v += tmpv

      # skip low value and saturation
      if tmpv > 0.25:
        if tmps > 0.33:
          h = int(tmph * 360)

          # logger.debuglog("%s \t set pixel r %s \tg %s \tb %s" % (i, r, g, b))
          # logger.debuglog("%s \t set pixel h %s \ts %s \tv %s" % (i, tmph*100, tmps*100, tmpv*100))

          if spectrum.has_key(h):
            spectrum[h] += 1 # tmps * 2 * tmpv
            saturation[h] = (saturation[h] + tmps)/2
            value[h] = (value[h] + tmpv)/2
          else:
            spectrum[h] = 1 # tmps * 2 * tmpv
            saturation[h] = tmps
            value[h] = tmpv

    overall_value = v / float(i)
    # s_overall = int(s * 100 / i)
    return self.most_used_spectrum(spectrum, saturation, value, size, overall_value)

def run():
  player = None
  #last = datetime.datetime.now()

  while not xbmc.abortRequested:
    hue.settings.mode = 0
    if hue.settings.mode == 1: # theatre mode
      if player == None:
        logger.debuglog("creating instance of player")
        player = MyPlayer()
      xbmc.sleep(500)
    if hue.settings.mode == 0: # ambilight mode
      if player == None:
        player = MyPlayer()
      else:
        xbmc.sleep(100)

      capture.waitForCaptureStateChangeEvent(1000/60)
      if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
        if player.playingvideo:
          screen = Screenshot(capture.getImage(), capture.getWidth(), capture.getHeight())
          hsvRatios = screen.spectrum_hsv(screen.pixels, screen.capture_width, screen.capture_height)
          fade_light_hsv(hsvRatios[0])

class Light:
  def __init__(self):
    self.fullSpectrum = True
    self.hueLast = 0
    self.satLast = 0
    self.valLast = 65535

light = Light()

def fade_light_hsv(hsvRatio):
  fullSpectrum = True

  h, s, v = hsvRatio.hue(fullSpectrum)
  hvec = abs(h - light.hueLast) % int(65535/2)
  hvec = float(hvec/128.0)
  svec = s - light.satLast
  vvec = v - light.valLast
  distance = math.sqrt(hvec * hvec + svec * svec + vvec * vvec)
  if distance > 0:
    duration = int(3 + 27 * distance/255)
    # this dur is in multiples of 100 miliseconds.
    # http://www.developers.meethue.com/documentation/lights-api
    # logger.debuglog("distance %s duration %s" % (distance, duration))
    #light.set_light2(h, s, v, duration)

    # color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
    k = 3500
    color = [h,s,v,k]
    # Lifxlan duration is in miliseconds
    lifx.set_color_all_lights(color, duration*100, rapid=False)

  light.hueLast = h
  light.satLast = s
  light.valLast = v


def state_changed(state, duration):
  logger.debuglog("state changed to: %s" % state)

  #detect pause for refresh change
  pauseafterrefreshchange = 0
  response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue", "params":{"setting":"videoplayer.pauseafterrefreshchange"},"id":1}'))
  #logger.debuglog(isinstance(response, dict))
  if "result" in response and "value" in response["result"]:
    pauseafterrefreshchange = int(response["result"]["value"])

  if duration < 300 and hue.settings.misc_disableshort:
    logger.debuglog("add-on disabled for short movies")
    return

  if state == "started":
    logger.debuglog("retrieving current setting before starting")
    if hue.settings.mode == 0: # ambilight mode
      #start capture when playback starts
      capture_width = 32 #100
      capture_height = int(capture_width / capture.getAspectRatio())
      logger.debuglog("capture %s x %s" % (capture_width, capture_height))
      capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)

  if (state == "started" and pauseafterrefreshchange == 0) or state == "resumed":
    logger.debuglog("dimming lights")
    hue.dim_lights()
  elif state == "paused" and hue.last_state == "dimmed":
    # only if its coming from being off
    # if settings.mode == 0 and hue.settings.ambilight_dim:
      # Be persistent in restoring the lights 
      # (prevent from being overwritten by an ambilight update)
      #for i in range(0, 3):
      #  logger.debuglog("partial lights")
      #  hue.dim_group.partial_lights()
      #  time.sleep(1)
    #else:
    hue.partial_lights()
  elif state == "stopped":
    # if hue.settings.mode == 0 and hue.settings.ambilight_dim:
      # Be persistent in restoring the lights 
      # (prevent from being overwritten by an ambilight update)
      #for i in range(0, 3):
      #  logger.debuglog("brighter lights")
      #  hue.dim_group.brighter_light()
      #  time.sleep(1)
    #else:
    hue.restore_bulbs()

if ( __name__ == "__main__" ):
  settings = settings()
  logger = Logger()
  if settings.debug == True:
    logger.debug()

  args = None
  if len(sys.argv) == 2:
    args = sys.argv[1]
  hue = Hue(settings, args)
  while not hue.connected:
    logger.debuglog("not connected")
    time.sleep(1)
  run()