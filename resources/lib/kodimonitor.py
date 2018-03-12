import xbmc

import ui
import clientinfo

from tools import xbmclog


class KodiMonitor(xbmc.Monitor):
    hue_service = None
    def __init__(self):
        xbmclog('In KodiMonitor.__init__()')
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        xbmclog('In onSettingsChanged() {}'.format(self.hue_service.settings))
        self.hue_service.settings.readxml()
        self.hue_service.update_controllers()

    def onNotification(self, sender, method, data):
        xbmclog('In onNotification(sender={}, method={}, data={})'
                .format(sender, method, data))
        if sender == clientinfo.ClientInfo().get_addon_id():
            if 'discover' in method:
                self.hue_service.ga.sendEventData("Configurations", "Discover")
                ui.discover_hue_bridge(self.hue_service)
                self.hue_service.update_controllers()
            if 'start_setup_theater_lights' in method:
                self.hue_service.ga.sendEventData("Configurations", "Setup Group", "Theater")
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
            if 'start_setup_theater_subgroup' in method:
                self.hue_service.ga.sendEventData("Configurations", "Setup Group", "Theater Subgroup")
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
            if 'start_setup_ambilight_lights' in method:
                self.hue_service.ga.sendEventData("Configurations", "Setup Group", "Ambilight")
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
            if 'start_setup_static_lights' in method:
                self.hue_service.ga.sendEventData("Configurations", "Setup Group", "Static")
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
            if 'reset_settings' in method:
                self.hue_service.ga.sendEventData("Configurations", "Reset")
                os.unlink(os.path.join(__addondir__, "settings.xml"))
