import json
# import requests

import xbmc

from lifxlan import *

from tools import xbmclog
from ga_client import GoogleAnalytics

ga = GoogleAnalytics()

class Light(object):

    def __init__(self, light):
        global ga
        xbmclog("Adding Light <{}>".format(light.mac_addr))

        self.light = light

        self.name = self.light.mac_addr
        self.product_name = ''
        self.product_features = None
        self.supports_color = True
        self.supports_temperature = True
        self.supports_multizone = False
        self.color = [0,0,0,3500]

        try:
            # Label is not set on initialization because refresh() was never called after initializing `light`
            if self.light.label == None:
                self.light.refresh()

            # Use cached responses after refresh() called once
            self.name = self.light.label
            self.product_name = self.light.get_product_name()
            self.product_features = self.light.get_product_features()
            self.supports_temperature = self.light.supports_temperature()
            self.supports_color = self.light.supports_color()
            self.supports_multizone = self.light.supports_multizone()

            # color is not cached
            self.color = self.light.get_color()

        except WorkflowException as error:
            errStrings = ga.formatException()
            ga.sendExceptionData(errStrings[0])
            ga.sendEventData("Exception", errStrings[0], errStrings[1])
            xbmclog("{}.__init__({}) - Exception - {}".format(self.__class__.__name__, self.name, str(error)))

        self.init_hue = self.color[0]
        self.hue = self.init_hue
        self.init_sat = int(self.color[1]*255/65535)
        self.sat = self.init_sat

        self.init_bri = int(self.color[2]*255/65535)
        self.bri = self.init_bri

        self.init_kel = self.color[3]
        self.kel = self.init_kel

        self.init_on = (self.light.power_level > 0)
        self.on = self.init_on

        xbmclog("Added light={}".format(self))

    def set_state(self, hue=0, sat=0, bri=0, kel=3500, on=None,
                  transition_time=None):
        # NOTE: From https://github.com/mclarkk/lifxlan -
        #   rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
        #   rapid is meant for super-fast light shows with lots of changes.
        state = {
            'hue' : self.hue,
            'sat' : self.sat,
            'bri' : self.bri,
            'kel' : self.kel,
            'on' : None,
            'transitiontime' : 0,
            'rapid' : False
        }


        xbmclog('set_state() - light={} - requested_state: HSBK=[{}, {}, {}, {}] on={} transition_time={})'.format(self.name, hue, sat, bri, kel, on, transition_time))
        xbmclog("set_state() - light={} - current_state: HSBK=[{}, {}, {}, {}] on={}".format(self.name, self.hue, self.sat, self.bri, self.kel, self.on))

        # reset `hue` and `sat` if light doesn't support color
        if not self.supports_color:
            hue = self.init_hue
            sat = self.init_sat

        # reset `kel` if light doesn't support temperature
        if not self.supports_temperature:
            kel = self.init_kel

        if transition_time is not None:
            state['transitiontime'] = transition_time
            # transition_time less than 1 second => set rapid = True
            state['rapid'] = True if transition_time < 1/100 else False
        if hue is not None and hue != self.hue:
            self.hue = hue
            state['hue'] = hue
        if sat is not None and sat != self.sat:
            self.sat = sat
            state['sat'] = sat

            # Use initial Kel values if `sat` == 0 and `kel` == None
            if sat == 0 and kel is None:
                kel = self.init_kel

            # Override `kel` to neutral if `sat` > 0
            if sat > 0:
                kel = 3500

        if bri is not None and bri != self.bri:
            self.bri = bri
            state['bri'] = bri

            # Turn the light on or off based on `bri` value
            # No need to turn the power off, just setting the bri=0 should turn the light "off", but keep the power=on
            # if bri <= 0 and self.on and on is None:
            #     on = False
            if bri >= 1 and not self.on and on is None:
                on = True

        if kel is not None and self.supports_temperature and kel != self.kel:
            self.kel = kel
            state['kel'] = kel

            # if `kel` is not neutral, reset `hue`, `sat` to initial values
            if kel != 3500:
                self.hue = self.init_hue
                self.sat = self.init_sat
                state['hue'] = self.init_hue
                state['sat'] = self.init_sat

        if on is not None and on != self.on:
            self.on = on
            state['on'] = on

        xbmclog('set_state() - light={} - final_state={})'.format(self.name, state))

        # Set power state
        if state['on'] != None:
            try:
                self.light.set_power(state['on'], rapid=False)
            except WorkflowException as error:
                errStrings = ga.formatException()
                ga.sendExceptionData(errStrings[0])
                ga.sendEventData("Exception", errStrings[0], errStrings[1])
                xbmclog("set_state() - set_power({}) - Exception - {}".format(state['on'], str(error)))

        # Set color state
        try:
            # NOTE:
            #   Lifx color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
            #   65535/255 = 257
            color = [int(state['hue']),int(state['sat']*257),int(state['bri']*257),int(state['kel'])]
            # xbmclog('set_state() - light={} - color={})'.format(self.name, color))
            # color_log = [int(data["hue"]*360/65535),int(data["sat"]*100/255),int(data["bri"]*100/255),int(data["kel"])]
            # self.logger.debuglog("set_light2: %s: %s  (%s ms)" % (self.light.get_label(), color_log, data["transitiontime"]*self.multiplier))

            # NOTE:
            #   Lifxlan duration is in miliseconds, for hue it's multiple of 100ms - https://developers.meethue.com/documentation/lights-api#16_set_light_state
            self.light.set_color(color, state['transitiontime']*100, rapid=state['rapid'])
        except WorkflowException as error:
            errStrings = ga.formatException()
            ga.sendExceptionData(errStrings[0])
            ga.sendEventData("Exception", errStrings[0], errStrings[1])
            xbmclog("set_color() - light={} - failed to set_color({}) - Exception - {}".format(self.name, color, str(error)))

    def restore_initial_state(self, transition_time=0):
        self.set_state(
            self.init_hue,
            self.init_sat,
            self.init_bri,
            self.init_kel,
            self.init_on,
            transition_time
        )

    def save_state_as_initial(self):
        self.init_hue = self.hue
        self.init_sat = self.sat
        self.init_bri = self.bri
        self.init_kel = self.kel
        self.init_on = self.on

    def __repr__(self):
        s = self.name
        try:
            indent = "  "
            s = self.light.device_characteristics_str(indent)
            s += indent + "Color (HSBK): {}\n".format(self.color)
            s += indent + self.light.device_firmware_str(indent)
            s += indent + self.light.device_product_str(indent)
        except (KeyError, WorkflowException) as err:
            errStrings = ga.formatException()
            ga.sendExceptionData(errStrings[0])
            ga.sendEventData("Exception", errStrings[0], errStrings[1])
            xbmclog("{}.__repr__() - light={} - Exception - {}".format(self.__class__.__name__, self.name, str(err)))
        return s

class Controller(object):

    def __init__(self, lights, settings):
        global ga
        self.lights = {}

        for light_id, lifx_light in lights.items():
            try:
                new_light = Light(lifx_light)
                self.lights[light_id] = new_light
            except WorkflowException as error:
                errStrings = ga.formatException()
                ga.sendExceptionData(errStrings[0])
                ga.sendEventData("Exception", errStrings[0], errStrings[1])
                xbmclog("{}.__init__(lights={}) - Exception ({}) - {}".format(self.__class__.__name__, lights.keys(), light_id, str(error)))

        self.settings = settings

    def on_playback_start(self, resume=False):
        raise NotImplementedError(
            'on_playback_start must be implemented in the controller'
        )

    def on_playback_pause(self):
        raise NotImplementedError(
            'on_playback_pause must be implemented in the controller'
        )

    def on_playback_stop(self):
        raise NotImplementedError(
            'on_playback_stop must be implemented in the controller'
        )

    def set_state(self, hue=None, sat=None, bri=None, kel=None, on=None,
                  transition_time=None, lights=None, force_on=None):
        xbmclog(
            'In {}.set_state(hue={}, sat={}, bri={}, kel={}, '
            'on={}, transition_time={}, lights={})'.format(
                self.__class__.__name__, hue, sat, bri, kel, on, transition_time,
                self.lights.keys()
            )
        )

        if force_on is None:
            # NOTE: We need the force_on parameter in this function because
            #   Static light group has to ignore the "force light on" settings,
            #   as it should always turn the lights on when playback starts and off when stops
            #   Only static light geoup will pass force_on=True, rest should use the value from settings
            force_on = self.settings.force_light_on

        for light in self._calculate_subgroup(lights):
            if not force_on and not light.init_on:
                continue

            if bri:
                if self.settings.proportional_dim_time:
                    transition_time = self._transition_time(light, bri)
                else:
                    transition_time = self.settings.dim_time

            light.set_state(
                hue=hue, sat=sat, bri=bri, kel=kel, on=on,
                transition_time=transition_time
            )

    def restore_initial_state(self, lights=None, force_on=None):
        xbmclog(
            'In {}.restore_initial_state(lights={})'
            .format(self.__class__.__name__, lights)
        )
        if force_on is None:
            force_on = self.settings.force_light_on

        for light in self._calculate_subgroup(lights):
            if not force_on and not light.init_on:
                continue
            transition_time = self.settings.dim_time
            if self.settings.proportional_dim_time:
                transition_time = self._transition_time(light, light.init_bri)

            light.restore_initial_state(
                transition_time
            )

    def save_state_as_initial(self, lights=None):
        xbmclog(
            'In {}.save_state_as_initial(lights={})'
            .format(self.__class__.__name__, lights)
        )

        for light in self._calculate_subgroup(lights):
            light.save_state_as_initial()

    def flash_lights(self):
        xbmclog(
            'In {} flash_lights())'
            .format(self.__class__.__name__)
        )

        # Turn the lights off first
        self.set_state(
            on = False
        )

        xbmc.sleep(1000)
        # Turn the lights on
        self.set_state(
            bri = 255,   # It is possible the current bri is 0, so turning the light on may not be enough
            on = True
        )
        xbmc.sleep(1000)
        self.restore_initial_state()

    def _calculate_subgroup(self, lights=None):
        if lights is None:
            ret = self.lights.values()
        else:
            xbmclog(
                'In {}._calculate_subgroup(lights={}) returning {} lights'.format(
                    self.__class__.__name__, lights, len(ret))
            )
            ret = [light for light in
                   self.lights.values() if light.name in lights]

        return ret

    def _transition_time(self, light, bri):
        time = 0

        difference = abs(float(bri) - light.bri)
        total = abs(float(light.init_bri) - self.settings.theater_start_bri)
        if total <= 0:
            return self.settings.dim_time
        proportion = difference / total
        time = int(round(proportion * self.settings.dim_time))

        return time

    def __repr__(self):
        return ('<{} ({})>'.format(self.__class__.__name__, self.lights.keys()))
