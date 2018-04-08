import sys

import xbmcaddon

from tools import xbmclog

__addon__ = sys.modules["__main__"].__addon__


class Settings():
    def __init__(self, hue):

        xbmclog('In Settings.__init__()')

        self.readonce = False
        self.readxml()

        self.hue = hue

        # Report initial settings to GA
        for k, v in self.__dict__.items():
            if k == "ambilight_group" or k == "theater_group" or k == "theater_subgroup" or k == "static_group":
                v = len(str(v).split(','))
            if k == "hue" or k == "readonce":
                continue
            try:
                self.hue.ga.sendEventData("Settings", k, str(v), ni=1)
            except Exception:
                pass
        self.readonce = True


    @staticmethod
    def getSetting(key):
        # Get or add addon setting
        global __addon__
        # returns unicode object
        value = __addon__.getSetting(key)
        xbmclog("getSetting({})={}".format(key, value))
        return value

    @staticmethod
    def setSetting(key, value):
        # Get or add addon setting
        global __addon__
        if value is not None:
            __addon__.setSetting(key, value)
            xbmclog("Setting {}={}".format(key, value))

    # TODO: Remove duplicate - setSetting()
    def update(self, **kwargs):
        self.__dict__.update(**kwargs)
        for k, v in kwargs.iteritems():
            __addon__.setSetting(k, str(v))
            if k == "ambilight_group" or k == "theater_group" or k == "theater_subgroup" or k == "static_group":
                v = len(str(v).split(','))
            try:
                self.hue.ga.sendEventData("Update", k, str(v))
            except Exception:
                pass

    def readxml(self):
        global __addon__
        __addon__ = xbmcaddon.Addon()

        # TODO: Add GA update event here
        self.connected = __addon__.getSetting("connected") == "true"

        # TODO - Remove duplicate code
        # self.update_setting("Setting name", self.ambilight_group, __addon__.getSetting("setting_id"))

        # Settings were read once already, so this is a manual update
        if self.readonce == True:
            pass
            # self.ambilight_group is changed before settings are saved
            # if set(self.ambilight_group.split(',')) != set(__addon__.getSetting("ambilight_group").split(',')):
            #     self.hue.ga.sendEventData("Settings", "Update", "ambilight_group", len(__addon__.getSetting("ambilight_group").split(',')), 1)
            # if set(self.theater_group.split(',')) != set(__addon__.getSetting("theater_group").split(',')):
            #     self.hue.ga.sendEventData("Settings", "Update", "theater_group", len(__addon__.getSetting("theater_group").split(',')), 1)
            # if set(self.theater_subgroup.split(',')) != set(__addon__.getSetting("theater_subgroup").split(',')):
            #     self.hue.ga.sendEventData("Settings", "Update", "theater_subgroup", len(__addon__.getSetting("theater_subgroup").split(',')), 1)
            # if set(self.static_group.split(',')) != set(__addon__.getSetting("static_group").split(',')):
            #     self.hue.ga.sendEventData("Settings", "Update", "static_group", len(__addon__.getSetting("static_group").split(',')), 1)

        self.ambilight_group = __addon__.getSetting("ambilight_group")
        self.theater_group = __addon__.getSetting("theater_group")
        self.theater_subgroup = __addon__.getSetting("theater_subgroup")
        self.static_group = __addon__.getSetting("static_group")

        self.dim_time = int(float(__addon__.getSetting("dim_time"))*10)
        self.proportional_dim_time = __addon__.getSetting("proportional_dim_time") == "true"

        self.theater_start_hue_override = __addon__.getSetting("theater_start_hue_override") == "true"
        self.theater_start_hue = int(__addon__.getSetting("theater_start_hue").split(".")[0])
        self.theater_start_sat_override = __addon__.getSetting("theater_start_sat_override") == "true"
        self.theater_start_sat = int(__addon__.getSetting("theater_start_sat").split(".")[0])
        self.theater_start_bri_override = __addon__.getSetting("theater_start_bri_override") == "true"
        self.theater_start_bri = int(__addon__.getSetting("theater_start_bri").split(".")[0])
        self.theater_start_kel_override = __addon__.getSetting("theater_start_kel_override") == "true"
        self.theater_start_kel = int(__addon__.getSetting("theater_start_kel").split(".")[0])

        self.theater_pause_dim_subgroup = __addon__.getSetting("theater_pause_dim_subgroup") == "true"
        self.theater_pause_hue_override = __addon__.getSetting("theater_pause_hue_override") == "true"
        self.theater_pause_hue = int(__addon__.getSetting("theater_pause_hue").split(".")[0])
        self.theater_pause_sat_override = __addon__.getSetting("theater_pause_sat_override") == "true"
        self.theater_pause_sat = int(__addon__.getSetting("theater_pause_sat").split(".")[0])
        self.theater_pause_bri_override = __addon__.getSetting("theater_pause_bri_override") == "true"
        self.theater_pause_bri = int(__addon__.getSetting("theater_pause_bri").split(".")[0])
        self.theater_pause_kel_override = __addon__.getSetting("theater_pause_kel_override") == "true"
        self.theater_pause_kel = int(__addon__.getSetting("theater_pause_kel").split(".")[0])

        self.theater_stop_hue_override = __addon__.getSetting("theater_stop_hue_override") == "true"
        self.theater_stop_hue = int(__addon__.getSetting("theater_stop_hue").split(".")[0])
        self.theater_stop_sat_override = __addon__.getSetting("theater_stop_sat_override") == "true"
        self.theater_stop_sat = int(__addon__.getSetting("theater_stop_sat").split(".")[0])
        self.theater_stop_bri_override = __addon__.getSetting("theater_stop_bri_override") == "true"
        self.theater_stop_bri = int(__addon__.getSetting("theater_stop_bri").split(".")[0])
        self.theater_stop_kel_override = __addon__.getSetting("theater_stop_kel_override") == "true"
        self.theater_stop_kel = int(__addon__.getSetting("theater_stop_kel").split(".")[0])

        self.ambilight_min = int(__addon__.getSetting("ambilight_min").split(".")[0])
        self.ambilight_max = int(__addon__.getSetting("ambilight_max").split(".")[0])

        self.ambilight_threshold_value = int(__addon__.getSetting("ambilight_threshold_value").split(".")[0])
        self.ambilight_threshold_saturation = int(__addon__.getSetting("ambilight_threshold_saturation").split(".")[0])

        self.color_variation = __addon__.getSetting("color_variation") == "true"
        self.color_bias = int(__addon__.getSetting("color_bias").split(".")[0])

        self.ambilight_start_dim_enable = __addon__.getSetting("ambilight_start_dim_enable") == "true"
        self.ambilight_start_dim_override = __addon__.getSetting("ambilight_start_dim_override") == "true"
        self.ambilight_start_dim = int(__addon__.getSetting("ambilight_start_dim").split(".")[0])

        self.ambilight_pause_bri_override = __addon__.getSetting("ambilight_pause_bri_override") == "true"
        self.ambilight_pause_bri = int(__addon__.getSetting("ambilight_pause_bri").split(".")[0])

        self.ambilight_stop_bri_override = __addon__.getSetting("ambilight_stop_bri_override") == "true"
        self.ambilight_stop_bri = int(__addon__.getSetting("ambilight_stop_bri").split(".")[0])

        self.static_start_random = __addon__.getSetting("static_start_random") == "true"
        self.static_start_hue_override = __addon__.getSetting("static_start_hue_override") == "true"
        self.static_start_hue = int(__addon__.getSetting("static_start_hue").split(".")[0])
        self.static_start_sat_override = __addon__.getSetting("static_start_sat_override") == "true"
        self.static_start_sat = int(__addon__.getSetting("static_start_sat").split(".")[0])
        self.static_start_bri_override = __addon__.getSetting("static_start_bri_override") == "true"
        self.static_start_bri = int(__addon__.getSetting("static_start_bri").split(".")[0])
        self.static_start_kel_override = __addon__.getSetting("static_start_kel_override") == "true"
        self.static_start_kel = int(__addon__.getSetting("static_start_kel").split(".")[0])

        self.misc_initialflash = __addon__.getSetting("misc_initialflash") == "true"
        self.misc_disableshort = __addon__.getSetting("misc_disableshort") == "true"
        self.misc_disableshort_threshold = int(__addon__.getSetting("misc_disableshort_threshold"))
        self.force_light_on = __addon__.getSetting("force_light_on") == "true"
        self.startup_delay = int(__addon__.getSetting("startup_delay").split(".")[0])
        self.metric_logging = __addon__.getSetting("metric_logging") == "true"

        if self.ambilight_min > self.ambilight_max:
            self.update(ambilight_min=self.ambilight_max)

    def __repr__(self):
        return '<Settings\n{}\n>'.format('\n'.join(['{}={}'.format(key, value) for key, value in sorted(self.__dict__.items())]))
