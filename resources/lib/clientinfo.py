# -*- coding: utf-8 -*-

#################################################################################################

import os
from uuid import uuid4

import xbmc
import xbmcaddon
import xbmcvfs

from tools import xbmclog

class ClientInfo(object):

    def __init__(self):

        self.addon = xbmcaddon.Addon(self.get_addon_id())

    @staticmethod
    def get_addon_id():
        return xbmcaddon.Addon().getAddonInfo('id')

    def get_addon_name(self):
        # Used for logging
        return self.addon.getAddonInfo('name').upper()

    def get_version(self):
        return self.addon.getAddonInfo('version')

    @classmethod
    def get_device_name(cls):

        device_name = xbmc.getInfoLabel('System.FriendlyName').decode('utf-8')
        return device_name

    @classmethod
    def get_platform(cls):

        if xbmc.getCondVisibility('system.platform.osx'):
            return "OSX"
        elif xbmc.getCondVisibility('system.platform.atv2'):
            return "ATV2"
        elif xbmc.getCondVisibility('system.platform.ios'):
            return "iOS"
        elif xbmc.getCondVisibility('system.platform.windows'):
            return "Windows"
        elif xbmc.getCondVisibility('system.platform.android'):
            return "Linux/Android"
        elif xbmc.getCondVisibility('system.platform.linux.raspberrypi'):
            return "Linux/RPi"
        elif xbmc.getCondVisibility('system.platform.linux'):
            return "Linux"
        else:
            return "Unknown"

    def get_device_id(self, reset=False):

        emby_guid = xbmc.translatePath("special://temp/emby_guid").decode('utf-8')

        if reset and xbmcvfs.exists(emby_guid):
            # Reset the file
            xbmcvfs.delete(emby_guid)

        guid = xbmcvfs.File(emby_guid)
        client_id = guid.read()
        if not client_id:
            xbmclog("Generating a new guid...")
            client_id = str("%012X" % uuid4())
            guid = xbmcvfs.File(emby_guid, 'w')
            guid.write(client_id)

        guid.close()

        xbmclog("DeviceId loaded: {}".format(client_id))

        return client_id
