import os
import xbmcgui

TESTING_ENV = False

try:
    import xbmc
    import xbmcaddon

    __addon__ = xbmcaddon.Addon()
    __cwd__ = __addon__.getAddonInfo('path')
    __icon__ = os.path.join(__cwd__, "resources/icon.png")
    __settings__ = os.path.join(__cwd__, "resources", "settings.xml")
    __xml__ = os.path.join(__cwd__, 'addon.xml')
except ImportError:
    TESTING_ENV = True


def xbmclog(message):
    if TESTING_ENV:
        pass
    else:
        xbmc.log("Kodi Lifx: %s" % message)


def notify(title, msg=''):
    if TESTING_ENV:
        pass
    else:
        xbmc.executebuiltin('XBMC.Notification({}, {}, 3, {})'.format(
            title, msg, __icon__))

# TODO: see if this can be moved to Settings class
def configs(config, value=None):
    # Get or add addon setting
    global __addon__
    if value is not None:
        __addon__.setSetting(config, value)
        xbmclog("Setting {}={}".format(config, value))
    else: # returns unicode object
        value = __addon__.getSetting(config)
        xbmclog("getSetting({})={}".format(config, value))
        return value

pDialog = None

def show_busy_dialog():
    # pass
    # TODO - add timeout thread to close the dialog
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    # pDialog = xbmcgui.DialogProgressBG()
    # pDialog.create('Kodi Lifx', 'Processing your request...')

def hide_busy_dialog():
    # pass
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
        xbmc.sleep(100)
    # if pDialog:
    #     pDialog.update(100, message='Done')
    #     pDialog.close()
