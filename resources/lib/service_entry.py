from threading import Event
import os
import sys
import platform
import time

import xbmc

import bridge
import ui
import algorithm
import image

import clientinfo
import player
import kodimonitor

from settings import Settings
from tools import xbmclog
from ambilight_controller import AmbilightController
from theater_controller import TheaterController
from static_controller import StaticController

from ga_client import GoogleAnalytics

ev = Event()
capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# BGRA or RGBA
fmtRGBA = fmt == 'RGBA'


class Service(object):

    startup = False
    ga = None
    theater_controller = None
    ambilight_controller = None
    static_controller = None

    settings = None
    monitor = None
    player = None

    lastMetricPing = time.time()

    def __init__(self):
        self.client_info = clientinfo.ClientInfo()
        self.addon_name = self.client_info.get_addon_name()

        # Initial logging
        xbmclog("======== START {} ========".format(self.addon_name))
        xbmclog("Python Version: {}".format(sys.version))
        xbmclog("Platform: {}".format(self.client_info.get_platform()))
        xbmclog("KODI Version: {}".format(xbmc.getInfoLabel('System.BuildVersion')))
        xbmclog("{} Version: {}".format(self.addon_name, self.client_info.get_version()))

        self.ga = GoogleAnalytics()

        try:
            # self.ga.sendEventData("Startup", "OS", platform.platform())
            # self.ga.sendEventData("Startup", "Python", platform.python_version())
            # self.ga.sendEventData("Startup", "Kodi", xbmc.getInfoLabel('System.BuildVersion'))
            self.ga.sendEventData("Startup", "Version", self.client_info.get_version())
        except Exception:
            pass

        self.connected = False

    def service_entry_point(self):

        xbmclog('In Service.service_entry_point()')

        if not self.startup:
            self.startup = self._startup()

        if self.player == None:
            xbmclog('Could not instantiate player')
            return
        # run() until abortRequested to update ambilight lights
        self.run()
        # Kodi requested abort
        self.shutdown()


    def _startup(self):
        self.settings = Settings(self)
        xbmclog("Current settings: \n{}".format(self.settings))
        # Important: Threads depending on abortRequest will not trigger
        # if profile switch happens more than once.
        self.monitor = kodimonitor.KodiMonitor()
        self.monitor.hue_service = self
        self.player = player.Player()
        self.player.hue_service = self

        if self.settings.ambilight_group or self.settings.theater_group or self.settings.static_group:
            self.update_controllers()

            if self.settings.misc_initialflash:
                self.ambilight_controller.flash_lights()
                self.theater_controller.flash_lights()
                self.static_controller.flash_lights()
        xbmclog("======== SERVICE STARTUP ========")
        return time.time()

    def shutdown(self):
        if self.settings:
            del self.settings
        if self.monitor:
            del self.monitor
        if self.player:
            del self.player

        xbmclog("======== SERVICE SHUTDOWN ========")

        if not self.ga:
            self.ga = GoogleAnalytics()

        if self.startup:
            uptime = time.time() - self.startup
            uptime = int(uptime/60)
            xbmclog("Shutting down after {} minutes".format(uptime))
            self.ga.sendEventData("Application", "Shutdown", "Uptime", uptime)
        else:
            self.ga.sendEventData("Application", "Shutdown")

    def update_controllers(self):
        if (self.ambilight_controller == None
            or (    self.ambilight_controller != None
                and set(self.settings.ambilight_group.split(',')) != set(self.ambilight_controller.lights.keys())
                )
            ):
            self.ambilight_controller = AmbilightController(
                bridge.get_lights_by_ids(self.settings.ambilight_group.split(',')),
                self.settings
            )

        if (self.theater_controller == None
            or (    self.theater_controller != None
                and set(self.settings.theater_group.split(',')) != set(self.theater_controller.lights.keys())
                )
            ):
            self.theater_controller = TheaterController(
                bridge.get_lights_by_ids(self.settings.theater_group.split(',')),
                self.settings
            )

        if (self.static_controller == None
            or (    self.static_controller != None
                and set(self.settings.static_group.split(',')) != set(self.static_controller.lights.keys())
                )
            ):
            self.static_controller = StaticController(
                bridge.get_lights_by_ids(self.settings.static_group.split(',')),
                self.settings
            )

        xbmclog(
            'In Hue.update_controllers() instantiated following '
            'controllers {} {} {}'.format(
                self.theater_controller,
                self.ambilight_controller,
                self.static_controller,
            )
        )

    def state_changed(self, state, duration):
        xbmclog('In state_changed(state={}, duration={})'.format(
            state, duration))

        if (xbmc.getCondVisibility('Window.IsActive(screensaver-atv4.xml)') or
                xbmc.getCondVisibility('Window.IsActive(screensaver-video-main.xml)')):
            return

        if duration < self.settings.misc_disableshort_threshold and self.settings.misc_disableshort:
            return

        if state == "started":
            # start capture when playback starts
            capture_width = 32  # 100
            capture_height = capture_width / capture.getAspectRatio()
            if capture_height == 0:
                capture_height = capture_width  # fix for divide by zero.
            capture.capture(int(capture_width), int(capture_height))

        if state == "started" or state == "resumed":
            ev.set()
            resume = False
            if state == "resumed":
                resume = True
            self.theater_controller.on_playback_start(resume)
            self.ambilight_controller.on_playback_start(resume)
            self.static_controller.on_playback_start(resume)
            ev.clear()

        elif state == "paused":
            ev.set()
            self.theater_controller.on_playback_pause()
            self.ambilight_controller.on_playback_pause()
            self.static_controller.on_playback_pause()

        elif state == "stopped":
            ev.set()
            self.theater_controller.on_playback_stop()
            self.ambilight_controller.on_playback_stop()
            self.static_controller.on_playback_stop()

    def run(self):
        while not self.monitor.abortRequested():
            if len(self.ambilight_controller.lights) and not ev.is_set():
                startReadOut = False
                vals = {}
                if self.player.playingvideo:  # only if there's actually video
                    # ping metrics server to keep sessions alive while playing
                    # ping every 5 min
                    timeSinceLastPing = time.time() - self.lastMetricPing
                    if(timeSinceLastPing > 300):
                        self.lastMetricPing = time.time()
                        ga = GoogleAnalytics()
                        # Keep the session alive
                        ga.sendEventData("Playback", "Video", "Playing", None, 1)
                    try:
                        pixels = capture.getImage(200)
                        if len(pixels) > 0:
                            screen = image.Screenshot(
                                pixels)
                            hsv_ratios = screen.spectrum_hsv(
                                screen.pixels,
                                self.settings.ambilight_threshold_value,
                                self.settings.ambilight_threshold_saturation,
                                self.settings.color_variation,
                                self.settings.color_bias,
                                len(self.ambilight_controller.lights)
                            )
                            for i in range(len(self.ambilight_controller.lights)):
                                algorithm.transition_colorspace(
                                    self, self.ambilight_controller.lights.values()[i], hsv_ratios[i], )
                    except ZeroDivisionError:
                        pass
            # Sleep for 0.1s
            if self.monitor.waitForAbort(0.1 if self.player.playingvideo else 1):
                # Abort was requested while waiting. We should exit
                break
