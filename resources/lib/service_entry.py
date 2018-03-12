from threading import Event
import os
import sys
import platform

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

    def __init__(self):
        self.client_info = clientinfo.ClientInfo()
        self.addon_name = self.client_info.get_addon_name()

        # Initial logging
        xbmclog("======== START {} ========".format(self.addon_name))
        xbmclog("Python Version: {}".format(sys.version))
        xbmclog("Platform: {}".format(self.client_info.get_platform()))
        xbmclog("KODI Version: {}".format(xbmc.getInfoLabel('System.BuildVersion')))
        xbmclog("{} Version: {}".format(self.addon_name, self.client_info.get_version()))

        self.connected = False

    def service_entry_point(self, args):
        try:
            params = dict(arg.split("=") for arg in args.split("&"))
        except Exception:
            params = {}

        xbmclog(
            'In Service.service_entry_point() '
            'params={}'.format(
                params)
            )

        if params == {}:
            if not self.startup:
                self.startup = self._startup()

            if self.player is None:
                xbmclog('Could not instantiate player')
                return
            # run() until abortRequested to update ambilight lights
            self.run()
            # Kodi requested abort
            self.shutdown()
        else:
            # not yet implemented
            pass


    def _startup(self):
        self.settings = Settings()
        # Important: Threads depending on abortRequest will not trigger
        # if profile switch happens more than once.
        self.ga = GoogleAnalytics()

        self.monitor = kodimonitor.KodiMonitor()
        self.monitor.hue_service = self
        self.player = player.Player()
        self.player.hue_service = self

        self.ga.sendEventData("Application", "Startup")

        try:
            self.ga.sendEventData("Version", "OS", platform.platform())
            self.ga.sendEventData("Version", "Python", platform.python_version())
        except Exception:
            pass

        # if there's a bridge IP, try to talk to it.
        if self.settings.bridge_ip not in ["-", "", None]:
            result = bridge.user_exists(
                self.settings.bridge_ip,
                self.settings.bridge_user
            )
            if result:
                self.connected = True

        if self.connected:
            self.update_controllers()

            if self.settings.misc_initialflash:
                self.ambilight_controller.flash_lights()
                self.theater_controller.flash_lights()
                self.static_controller.flash_lights()
        xbmclog("======== SERVICE STARTUP ========")
        return True

    def shutdown(self):
        del self.settings
        del self.monitor
        del self.player

        xbmclog("======== SERVICE SHUTDOWN ========")

        if self.ga == None:
            self.ga = GoogleAnalytics()

        self.ga.sendEventData("Application", "Shutdown")

    def update_controllers(self):
        self.ambilight_controller = AmbilightController(
            bridge.get_lights_by_ids(
                self.settings.bridge_ip,
                self.settings.bridge_user,
                self.settings.ambilight_group.split(',')),
            self.settings
        )

        self.theater_controller = TheaterController(
            bridge.get_lights_by_ids(
                self.settings.bridge_ip,
                self.settings.bridge_user,
                self.settings.theater_group.split(',')),
            self.settings
        )

        self.static_controller = StaticController(
            bridge.get_lights_by_ids(
                self.settings.bridge_ip,
                self.settings.bridge_user,
                self.settings.static_group.split(',')),
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
                    try:
                        pixels = capture.getImage(200)
                        if len(pixels) > 0 and self.player.playingvideo:
                            startReadOut = True
                        if startReadOut:
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
