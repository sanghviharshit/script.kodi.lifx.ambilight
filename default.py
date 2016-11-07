import xbmc
import xbmcgui
import xbmcaddon
from time import time, sleep
import sys
import colorsys
import os
from datetime import datetime
import math
from threading import Timer

__addon__      = xbmcaddon.Addon()
__addondir__   = xbmc.translatePath( __addon__.getAddonInfo('profile') ) 
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__        = __addon__.getAddonInfo('path')
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )

sys.path.append (__resource__)

from settings import *
from tools import *
from hue import *

useLegacyApi = True

xbmc.log("Kodi Lifx service started, version: %s" % __addonversion__)

capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# BGRA or RGBA
# xbmc.log("Hue Capture Image format: %s" % fmt)
fmtRGBA = fmt == 'RGBA'

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer     = None
    self.interval   = interval
    self.function   = function
    self.args       = args
    self.kwargs     = kwargs
    self.is_running = False
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self._timer = Timer(self.interval, self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False

class MyMonitor( xbmc.Monitor ):
  def __init__( self, *args, **kwargs ):
    xbmc.Monitor.__init__( self )

  def onSettingsChanged( self ):
    logger.debuglog("running in mode %s" % str(hue.settings.mode))
    #last = datetime.now()
    hue.settings.readxml()
    hue.update_settings()

class MyPlayer(xbmc.Player):
  duration = 0
  playingvideo = False
  playlistlen = 0
  timer = None
  movie = False
  framerate = 25

  def __init__(self):
    xbmc.Player.__init__(self)
  
  def checkTime(self):
    if self.isPlayingVideo():
      check_time(int(self.getTime())) #call back out to plugin function.

  def onPlayBackStarted(self):
    xbmc.log("Kodi Lifx: DEBUG playback started called on player")
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    self.playlistlen = playlist.size()
    self.playlistpos = playlist.getposition()

    if self.isPlayingVideo() and not self.playingvideo:
      self.playingvideo = True
      self.duration = self.getTotalTime()
      self.movie = xbmc.getCondVisibility('VideoPlayer.Content(movies)')

      global credits_triggered
      credits_triggered = False
      if self.movie and self.duration != 0: #only try if its a movie and has a duration
        get_credits_info(self.getVideoInfoTag().getTitle(), self.duration) # TODO: start it on a timer to not block the beginning of the media
        logger.debuglog("credits_time: %r" % credits_time)
        self.timer = RepeatedTimer(1, self.checkTime)
      state_changed("started", self.duration)

  def onPlayBackPaused(self):
    xbmc.log("Kodi Lifx: DEBUG playback paused called on player")
    if self.isPlayingVideo():
      self.playingvideo = False
      if self.movie and not self.timer is None:
        self.timer.stop()
      state_changed("paused", self.duration)

  def onPlayBackResumed(self):
    logger.debuglog("playback resumed called on player")
    if self.isPlayingVideo():
      self.playingvideo = True
      if self.duration == 0:
        self.duration = self.getTotalTime()
        if self.movie and self.duration != 0: #only try if its a movie and has a duration
          get_credits_info(self.getVideoInfoTag().getTitle(), self.duration) # TODO: start it on a timer to not block the beginning of the media
          logger.debuglog("credits_time: %r" % credits_time)
      if self.movie and self.duration != 0:    
        self.timer = RepeatedTimer(1, self.checkTime)
      state_changed("resumed", self.duration)

  def onPlayBackStopped(self):
    xbmc.log("Kodi Lifx: DEBUG playback stopped called on player")
    self.playingvideo = False
    self.playlistlen = 0
    if self.movie and not self.timer is None:
      self.timer.stop()
    state_changed("stopped", self.duration)

  def onPlayBackEnded(self):
    xbmc.log("Kodi Lifx: DEBUG playback ended called on player")
    # If there are upcoming plays, ignore 
    if self.playlistpos < self.playlistlen-1:
      return
      
    self.playingvideo = False
    if self.movie and not self.timer is None:
      self.timer.stop()
    state_changed("stopped", self.duration)

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
      if self.h > 0.065 and self.h < 0.19:
          self.h = self.h * 2.32
      elif self.s > 0.01:
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

    h = int(self.h*65535) # on a scale from 0 <-> 65534
    s = int(self.s*255)
    v = int(self.v*255)

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
    colorGroups = settings.color_bias #6 = more variety of colors, 36 = similar colors
    colorHueRatio = 360 / colorGroups #colorHueRatio will be between 60 and 10. 60=close to primary colors, 10 = more to original colors

    hsvRatios = []
    hsvRatiosDict = {}

    for i in spectrum:
      #shift index to the right so that groups are centered on primary and secondary colors
      colorIndex = int(((i+colorHueRatio/2) % 360)/colorHueRatio)
      #some info? - https://docs.gimp.org/en/gimp-tool-hue-saturation.html
      #i=0, ratio=60 => colorIndex = 0            
      #i=60, ratio=60 => colorIndex = int(1.5)
      #i=90, ratio=60 => colorIndex = int(2)
      #i=120, ratio=60 => colorIndex = int(2.5)
      #i=180, ratio=60 => colorIndex = int(3.5)
      #i=270, ratio=60 => colorIndex = int(4.5)
      #i=330, ratio=60 => colorIndex = int(5.5)
      #i=360, ratio=60 => colorIndex = int(0.5)

      pixelCount = spectrum[i]

      try:
        hsvr = hsvRatiosDict[colorIndex]
        hsvr.average(i/360.0, saturation[i], value[i])
        hsvr.ratio = hsvr.ratio + pixelCount / float(size)
      except KeyError:
        hsvr = HSVRatio(i/360.0, saturation[i], value[i], pixelCount / float(size))
        hsvRatiosDict[colorIndex] = hsvr
        hsvRatios.append(hsvr)

    colorCount = len(hsvRatios)
    logger.debuglog("Count of colors - %s" % colorCount)

    if colorCount > 1:
      # sort colors by popularity
      hsvRatios = sorted(hsvRatios, key=lambda hsvratio: hsvratio.ratio, reverse=True)
      
      for hsvRatio in hsvRatios:
        hsvRatio.averageValue(overall_value)

      '''  
      #return at least 3
      if colorCount == 2:
        hsvRatios.insert(0, hsvRatios[0])

      hsvRatios[0].averageValue(overall_value)
      hsvRatios[1].averageValue(overall_value)
      hsvRatios[2].averageValue(overall_value)
      '''
      return hsvRatios

    elif colorCount == 1:
      hsvRatios[0].averageValue(overall_value)
      return [hsvRatios[0]]

    else:
      return [HSVRatio()]

  def spectrum_hsv(self, pixels, width, height):
    spectrum = {}
    saturation = {}
    value = {}

    size = int(len(pixels)/4)

    v = 0
    r, g, b = 0, 0, 0
    tmph, tmps, tmpv = 0, 0, 0

    for i in range(0, size, 4):
      r, g, b = _rgb_from_pixels(pixels, i)
      tmph, tmps, tmpv = colorsys.rgb_to_hsv(float(r/255.0), float(g/255.0), float(b/255.0))
      v += tmpv

      # skip low value and saturation
      if tmpv > hue.settings.ambilight_threshold_value:
        if tmps > hue.settings.ambilight_threshold_saturation:
          h = int(tmph * 360)
          try:
              spectrum[h] += 1
              saturation[h] = saturation[h] + tmps
              value[h] = value[h] + tmpv
          except KeyError:
              spectrum[h] = 1
              saturation[h] = tmps
              value[h] = tmpv

      # Averaging saturation and value for each hue key in spectrum
      for i in spectrum:
        saturation[i] = saturation[i]/spectrum[i]
        value[h] = value[h]/spectrum[i]

    overall_value = 1
    if int(i) != 0:
      overall_value = v / float(len(pixels))
    return self.most_used_spectrum(spectrum, saturation, value, size, overall_value)


def _rgb_from_pixels(pixels, index):
  if fmtRGBA:
    return _rgb_from_pixels_rgba(pixels, index)
  else:  # probably BGRA
    return _rgb_from_pixels_rgba(pixels, index)[::-1]


def _rgb_from_pixels_rgba(pixels, index):
  return [pixels[index + i] for i in range(3)]

def run():
  player = MyPlayer()
  if player == None:
    logger.log("Cannot instantiate player. Bailing out")
    return
  last = time()

  #logger.debuglog("starting run loop!")
  while not monitor.abortRequested() and not xbmc.abortRequested:

    #sleep(100)
    waitTimeout = 1; #seconds

    if hue.settings.mode == 0: # ambilight mode
      waitTimeout = 0.01; #seconds
      
      startReadOut = False
      vals = {}

      #commenting the following lines because it breaks pause detection
      ## live tv does not trigger playbackstart
      #if player.isPlayingVideo() and not player.playingvideo:
      #  player.playingvideo = True
      #  state_changed("started", player.getTotalTime())
      #  continue
      if player.playingvideo: # only if there's actually video
        now = time()
        #logger.debuglog("run loop delta: %f (%f/sec)" % ((now-last), 1/(now-last)))
        #logger.debuglog("player.playingvideo: %s %s, useLegacyApi: %s" % (player.playingvideo, player.isPlayingVideo(), useLegacyApi))
        last = now
        try:
          if useLegacyApi:
            #logger.debuglog("Waiting for capture state changed")
            capture.waitForCaptureStateChangeEvent(1000)
            #we've got a capture event
            #logger.debuglog("Capture State = %s" % (capture.getCaptureState()))
            if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
              startReadOut = True
          else:
            pixels = capture.getImage(1000)
            if len(pixels) > 0:
              startReadOut = True

          if startReadOut:
            if useLegacyApi:
              pixels = capture.getImage(1000)

            width = capture.getWidth();
            height = capture.getHeight();

            screen = Screenshot(pixels, width, height)
            hsvRatios = screen.spectrum_hsv(screen.pixels, screen.capture_width, screen.capture_height)
            logger.debuglog("hsvRatios: %s" %(hsvRatios))

            if hue.settings.light == 0:
              if settings.color_variation == 0:
                fade_light_hsv(hue.light, hsvRatios[0])
              else:
                loop_index = 0
                for l in hue.light.lights:
                  fade_light_hsv(hue.light.lights[l], hsvRatios[loop_index % len(hsvRatios)])
                  loop_index = loop_index + 1
            else:
              if settings.color_variation == 0:
                for l in hue.light:
                  fade_light_hsv(l, hsvRatios[0])
              else:
                loop_index = 0
                for l in hue.light:
                  fade_light_hsv(l, hsvRatios[loop_index % len(hsvRatios)])
                  loop_index = loop_index + 1
        except ZeroDivisionError:
          logger.debuglog("no frame. looping.")

    if monitor.waitForAbort(waitTimeout):
      #kodi requested an abort, lets get out of here.
      break
  del player #might help with slow exit.
  #del monitor

def fade_light_hsv(light, hsvRatio):
  fullSpectrum = light.fullSpectrum
  h, s, v = hsvRatio.hue(fullSpectrum)
  hvec = abs(h - light.hueLast) % int(65535/2)
  hvec = float(hvec/128.0)
  svec = s - light.satLast
  vvec = v - light.briLast
  distance = math.sqrt(hvec**2 + svec**2 + vvec**2) #changed to squares for performance
  if distance > 0:
    if hue.settings.ambilight_old_algorithm:
      duration = int(3 + 27 * distance/255)
    else:
      duration = int(10 - 2.5 * distance/255)
    #logger.debuglog("distance %s duration %s" % (distance, duration))
    light.set_light2(h, s, v, kel=None, power=None, duration=duration)

credits_time = None #test = 10
credits_triggered = False

def get_credits_info(title, duration):
  logger.debuglog("get_credits_info")
  if hue.settings.undim_during_credits:
    #get credits time here
    logger.debuglog("title: %r, duration: %r" % (title, duration))
    global credits_time
    credits_time = ChapterManager.CreditsStartTimeForMovie(title, duration)
    logger.debuglog("set credits time to: %r" % credits_time)

def check_time(cur_time):
  global credits_triggered
  #logger.debuglog("check_time: %r, undim: %r, credits_time: %r" % (cur_time, hue.settings.undim_during_credits, credits_time))
  if hue.settings.undim_during_credits and credits_time != None:
    if (cur_time >= credits_time + hue.settings.credits_delay_time) and not credits_triggered:
      logger.debuglog("hit credits, turn on lights")
      # do partial undim (if enabled, otherwise full undim)
      if hue.settings.mode == 0:
        if hue.settings.ambilight_dim:
          if hue.settings.ambilight_dim_light == 0:
            hue.ambilight_dim_light.brighter_light()
          elif hue.settings.ambilight_dim_light > 0:
            for l in hue.ambilight_dim_light:
              l.brighter_light()
      else:
        hue.brighter_lights()
      credits_triggered = True
    elif (cur_time < credits_time + hue.settings.credits_delay_time) and credits_triggered:
      #still before credits, if this has happened, we've rewound
      credits_triggered = False

def state_changed(state, duration):
  logger.debuglog("state changed to: %s" % state)

  if duration < hue.settings.misc_disableshort_threshold and hue.settings.misc_disableshort:
    logger.debuglog("add-on disabled for short movies")
    return

  if state == "started":
    logger.debuglog("retrieving current setting before starting")
    
    if hue.settings.light == 0: # group mode
      hue.light.get_current_setting()
    else:
      for l in hue.light:
        l.get_current_setting()

    if hue.settings.mode == 0: # ambilight mode
      if hue.settings.ambilight_dim:
        if hue.settings.ambilight_dim_light == 0:
          hue.ambilight_dim_light.get_current_setting()
        elif hue.settings.ambilight_dim_light > 0:
          for l in hue.ambilight_dim_light:
            l.get_current_setting()
      #start capture when playback starts
      capture_width = 32 #100
      capture_height = capture_width / capture.getAspectRatio()
      if capture_height == 0:
        capture_height = capture_width #fix for divide by zero.
      logger.debuglog("capture %s x %s" % (capture_width, capture_height))
      if useLegacyApi:
        capture.capture(int(capture_width), int(capture_height), xbmc.CAPTURE_FLAG_CONTINUOUS)
      else:
        capture.capture(int(capture_width), int(capture_height))

  if state == "started" or state == "resumed":
    if hue.settings.mode == 0: #if in ambilight mode
      if hue.settings.ambilight_dim: #if dimming is enabled
        logger.debuglog("dimming for ambilight")
        if hue.settings.ambilight_dim_light == 0:
          hue.ambilight_dim_light.dim_light()
        elif hue.settings.ambilight_dim_light > 0:
          for l in hue.ambilight_dim_light:
            l.dim_light()
    else:
      logger.debuglog("dimming lights")
      hue.dim_lights()
    hue.last_state = "dimmed"
  elif state == "paused" and hue.last_state == "dimmed":
    #only if its coming from being off
    if hue.settings.mode == 0:  # if in ambilight mode
      if hue.settings.ambilight_dim:  # if dimming is enabled
        logger.debuglog("setting partial lights")
        if hue.settings.ambilight_dim_light == 0:
          hue.ambilight_dim_light.partial_light()
        elif hue.settings.ambilight_dim_light > 0:
          for l in hue.ambilight_dim_light:
            l.partial_light()
    else:
      logger.debuglog("setting partial lights")
      hue.partial_lights()
    hue.last_state = "partial"
  elif state == "stopped":
    if hue.settings.mode == 0:  # if in ambilight mode
      if hue.settings.ambilight_dim:  # if dimming is enabled
        logger.debuglog("restoring lights for ambilight")
        if hue.settings.ambilight_dim_light == 0:
          hue.ambilight_dim_light.brighter_light()
        elif hue.settings.ambilight_dim_light > 0:
          for l in hue.ambilight_dim_light:
            l.brighter_light()
    else:
      logger.debuglog("restoring lights for theater")
      hue.brighter_lights()
    hue.last_state = "brighter"

if ( __name__ == "__main__" ):
  try:
    capture.getCaptureState()
  except AttributeError:
    useLegacyApi = False

  settings = MySettings()
  logger = Logger()
  monitor = MyMonitor()

  if settings.debug == True:
    logger.debug()

  logger.debuglog("useLegacyApi - %s" % str(useLegacyApi))
  logger.debuglog("Settings - %s" % str(settings))

  args = None
  if len(sys.argv) == 2:
    args = sys.argv[1]
  hue = Hue(settings, args)
  while not hue.connected and not monitor.abortRequested():
    sleep(1)

  logger.debuglog("Connected")
    
  run()

