import xbmc

import ui
from tools import xbmclog


class KodiMonitor(xbmc.Monitor):
    hue_service = None
    def __init__(self):
        xbmclog('In KodiMonitor.__init__()')
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        self.hue_service.settings.readxml()
        xbmclog('In onSettingsChanged() {}'.format(self.hue_service.settings))
        self.hue_service.update_controllers()

    def onNotification(self, sender, method, data):
        xbmclog('In onNotification(sender={}, method={}, data={})'
                .format(sender, method, data))
        if sender == __addon__.getAddonInfo('id'):
            if method == 'Other.start_setup_theater_lights':
                ret = ui.multiselect_lights(
                    self.hue_service.settings.bridge_ip,
                    self.hue_service.settings.bridge_user,
                    'Select Theater Lights',
                    ','.join([self.hue_service.settings.ambilight_group,
                              self.hue_service.settings.static_group]),
                    self.hue_service.settings.theater_group
                )
                self.hue_service.settings.update(theater_group=ret)
                self.hue_service.update_controllers()
            if method == 'Other.start_setup_theater_subgroup':
                ret = ui.multiselect_lights(
                    self.hue_service.settings.bridge_ip,
                    self.hue_service.settings.bridge_user,
                    'Select Theater Subgroup',
                    ','.join([self.hue_service.settings.ambilight_group,
                              self.hue_service.settings.static_group]),
                    self.hue_service.settings.theater_subgroup
                )
                self.hue_service.settings.update(theater_subgroup=ret)
                self.hue_service.update_controllers()
            if method == 'Other.start_setup_ambilight_lights':
                ret = ui.multiselect_lights(
                    self.hue_service.settings.bridge_ip,
                    self.hue_service.settings.bridge_user,
                    'Select Ambilight Lights',
                    ','.join([self.hue_service.settings.theater_group,
                              self.hue_service.settings.static_group]),
                    self.hue_service.settings.ambilight_group
                )
                self.hue_service.settings.update(ambilight_group=ret)
                self.hue_service.update_controllers()
            if method == 'Other.start_setup_static_lights':
                ret = ui.multiselect_lights(
                    self.hue_service.settings.bridge_ip,
                    self.hue_service.settings.bridge_user,
                    'Select Static Lights',
                    ','.join([self.hue_service.settings.theater_group,
                              self.hue_service.settings.ambilight_group]),
                    self.hue_service.settings.static_group
                )
                self.hue_service.settings.update(static_group=ret)
                self.hue_service.update_controllers()
