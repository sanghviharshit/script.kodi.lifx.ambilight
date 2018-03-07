import json
# import requests

from tools import xbmclog


class Light(object):

    def __init__(self, bridge_ip, username, light_id, light):
        self.bridge_ip = bridge_ip
        self.username = username

        # xbmclog("Adding Light object: {}".format(light))

        self.light_id = light_id
        self.light = light
        self.color = self.light.get_color()
        # self.features = light.get_product_features()
        self.fullspectrum = self.light.supports_color() # All Lifx Color bulbs are fullspectrum
        self.livingwhite = not self.light.supports_color()
        self.name = light_id

        self.init_hue = None
        self.hue = None

        self.init_sat = None
        self.sat = None

        if self.fullspectrum:
            self.init_hue = self.color[0]
            self.hue = self.init_hue
            self.init_sat = self.color[1]*255/65535
            self.sat = self.init_sat

        self.init_bri = self.color[2]*255/65535
        self.bri = self.init_bri

        self.init_kel = self.color[3]
        self.kel = self.init_kel

        self.init_on = (self.light.power_level > 0)
        self.on = self.init_on

        # xbmclog("Added light={} - current_state: hue-{}, sat-{}, bri-{},on-{}".format(self.name, self.hue, self.sat, self.bri, self.on))
        # self.session = requests.Session()

    def set_state(self, hue=None, sat=None, bri=None, kel=None, on=None,
                  transition_time=None):
        # NOTE: From https://github.com/mclarkk/lifxlan -
        #   rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
        #   rapid is meant for super-fast light shows with lots of changes.
        rapid = False
        state = {}

        # xbmclog('set_state() - light={} - new_state: hue={}, sat={}, bri={}, on={}, transition_time={})'.format(self.name, hue, sat, bri, on, transition_time))

        # xbmclog("set_state() - light={} - current_state: hue-{}, sat-{}, bri-{},on-{}".format(self.name, self.hue, self.sat, self.bri, self.on))

        if transition_time is not None:
            state['transitiontime'] = transition_time
            # rapid = False
        if on is not None and on != self.on:
            self.on = on
            state['on'] = on
        if hue is not None and not self.livingwhite and hue != self.hue:
            self.hue = hue
            state['hue'] = hue
        if sat is not None and not self.livingwhite and sat != self.sat:
            self.sat = sat
            state['sat'] = sat
        if bri is not None and bri != self.bri:
            self.bri = bri
            state['bri'] = bri
            # Hue specific
            if bri <= 0 and self.on and on is None:
                self.on = False
                state['on'] = False
            if bri >= 1 and not self.on and on is None:
                self.on = True
                state['on'] = True

        if kel is not None and kel != self.kel:
            self.kel = kel
            state['kel'] = kel
            if kel != 3500:
                state['hue'] = 0
                state['sat'] = 0
        elif sat == 0:
            state["kel"] = self.init_kel

        if 'hue' not in state:
            state['hue'] = self.hue
        if 'sat' not in state:
            state['sat'] = self.sat
        if 'bri' not in state:
            state['bri'] = self.bri
        if 'kel' not in state:
            state['kel'] = self.kel
        if 'transitiontime' not in state:
            state['transitiontime'] = 0
            rapid = True

        # override kel to neutral if hue or sat > 0
        if state['hue'] > 0 or state['hue'] > 0:
            self.kel = 3500
            state['kel']  = 3500  # Set kelvin to neutral

        if 'on' in state:
            try:
                self.light.set_power(state['on'], rapid=False)
            except:
                xbmclog('set_state() - failed to set_power()')

        # xbmclog('set_state() - light={} - final_state={})'.format(self.name, state))
        # NOTE:
        #   Lifx color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
        #   65535/255 = 257
        color = [int(state['hue']),int(state['sat']*257),int(state['bri']*257),int(state['kel'])]
        # xbmclog('set_state() - light={} - color={})'.format(self.name, color))
                #color_log = [int(data["hue"]*360/65535),int(data["sat"]*100/255),int(data["bri"]*100/255),int(data["kel"])]
        #self.logger.debuglog("set_light2: %s: %s  (%s ms)" % (self.light.get_label(), color_log, data["transitiontime"]*self.multiplier))

        # NOTE:
        #   Lifxlan duration is in miliseconds, for hue it's multiple of 100ms - https://developers.meethue.com/documentation/lights-api#16_set_light_state
        try:
            self.light.set_color(color, state['transitiontime']*100/2, rapid=rapid)
        except:
            xbmclog("set_color() - light={} - failed to set_color()".format(self.name))

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
        return ('<Light({}) {} hue: {}, sat: {}, bri: {}, kel: {}, on: {}>'.format(
            self.name, self.light_id, self.hue, self.sat, self.bri, self.kel, self.on))


class Controller(object):

    def __init__(self, lights, settings):
        self.lights = lights
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
                  transition_time=None, lights=None, force_on=True):
        xbmclog(
            'In {}.set_state(hue={}, sat={}, bri={}, kel={}, '
            'on={}, transition_time={}, lights={}, force_on={})'.format(
                self.__class__.__name__, hue, sat, bri, kel, on, transition_time,
                lights, force_on
            )
        )

        for light in self._calculate_subgroup(lights):
            if not force_on and not light.init_on:
                continue
            if bri:
                if self.settings.proportional_dim_time:
                    transition_time = self._transition_time(light, bri)
                else:
                    transition_time = self.settings.dim_time
            xbmclog(
                'In {}.set_state(hue={}, sat={}, bri={}, kel={}, '
                'on={}, transition_time={}, light={})'.format(
                    self.__class__.__name__, hue, sat, bri, kel, on, transition_time,
                    light.name
                )
            )

            light.set_state(
                hue=hue, sat=sat, bri=bri, kel=kel, on=on,
                transition_time=transition_time
            )

    def restore_initial_state(self, lights=None, force_on=True):
        xbmclog(
            'In {}.restore_initial_state(lights={})'
            .format(self.__class__.__name__, lights)
        )

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

        if self.settings.force_light_on:
            on = True

        self.set_state(
            on=False
        )

        self.set_state(
            on=on
        )

        self.restore_initial_state(
            force_on=self.settings.force_light_on,
        )

    def _calculate_subgroup(self, lights=None):
        if lights is None:
            ret = self.lights.values()
        else:
            ret = [light for light in
                   self.lights.values() if light.light_id in lights]

        xbmclog(
            'In {}._calculate_subgroup'
            '(lights={}) returning {}'.format(
                self.__class__.__name__, lights, ret)
        )
        return ret

    def _transition_time(self, light, bri):
        time = 0

        difference = abs(float(bri) - light.bri)
        total = float(light.init_bri) - self.settings.theater_start_bri
        if total == 0:
            return self.settings.dim_time
        proportion = difference / total
        time = int(round(proportion * self.settings.dim_time))

        return time

    def __repr__(self):
        return ('<{} {}>'.format(self.__class__.__name__, self.lights))
