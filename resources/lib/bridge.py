import time

import lights

from lifxlan import *
from tools import *
from ga_client import GoogleAnalytics

# TODO - clean up, remove bridge ip, user references

lan = LifxLAN()
ga = GoogleAnalytics()

lights_cache = None

def discover():
    show_busy_dialog()
    lifx_lights = get_lights(refresh=True)
    if lifx_lights and len(lifx_lights) > 0:
      xbmclog("discover() - Found {0} Lifx lights".format(str(len(lifx_lights))))
      notify("Kodi Lifx", "Found {0} Lifx lights".format(str(len(lifx_lights))))
    else:
      xbmclog("discover() - No Lifx lights found")
      notify("Kodi Lifx", "No Lifx lights found")
    hide_busy_dialog()
    return len(lifx_lights)

def get_lights(refresh=False):
    global lights_cache
    if lights_cache == None or len(lights_cache) == 0 or refresh == True:
        try:
            lights_cache = lan.get_lights()
            xbmclog("get_lights(refresh={}) - Found {} Lifx lights".format(refresh, str(len(lights_cache))))
        except WorkflowException as error:
            errStrings = ga.formatException()
            ga.sendEventData("Exception", errStrings[0], errStrings[1])
            xbmclog("get_lights(refresh={}) - Exception - {}".format(refresh,str(error)))
    else:
        xbmclog("get_lights(refresh={}) - Returning {} cached Lifx lights".format(refresh, str(len(lights_cache))))
    return lights_cache

def get_lights_by_ids(light_ids=None):
    show_busy_dialog()
    found = {}
    xbmclog("get_lights_by_ids(light_ids={})".format(light_ids))
    if light_ids == None:
        lifx_lights = get_lights()
        if lifx_lights and len(lifx_lights) > 0:
            lifx_lights_ids = [lifx_light.get_label() for lifx_light in lifx_lights]
            # xbmclog("get_lights_by_ids(light_ids={}) - lifx_lights - {}".format(light_ids, lifx_lights_ids))
            for lifx_light in lifx_lights:
                try:
                    light_id = lifx_light.get_label()
                    xbmclog("get_lights_by_ids(light_ids={}) - Adding {}".format(light_ids, light_id))
                    found[light_id] = lifx_light
                    # found[light_id] = lights.Light(light_id, lifx_light)
                except WorkflowException as error:
                    errStrings = ga.formatException()
                    ga.sendEventData("Exception", errStrings[0], errStrings[1])
                    xbmclog("get_lights_by_ids(light_ids={}) - get_label() for {} - Exception - {}".format(light_ids, lifx_light, str(error)))
    elif light_ids == ['']:
        found = {}
    else:
        lifx_lights = get_lights()
        if lifx_lights and len(lifx_lights) > 0:
            lifx_dic = {}
            for lifx_light in lifx_lights:
                # TODO - Remove duplicate code
                lifx_light_label = lifx_light.mac_addr
                try:
                    # label is not set when initialized
                    lifx_light_label = lifx_light.get_label()
                except WorkflowException as error:
                    errStrings = ga.formatException()
                    ga.sendEventData("Exception", errStrings[0], errStrings[1])
                    xbmclog("get_label({}) - Exception - {}".format(lifx_light_label,str(error)))

                lifx_dic[lifx_light_label] = lifx_light

            for light_id in light_ids:
                if light_id in lifx_dic:
                    xbmclog("get_lights_by_ids(light_ids={}) - Found {}".format(light_ids, light_id))
                    found[light_id] = lifx_dic[light_id]
                    # found[light_id] = lights.Light(light_id, lifx_light)
                else:
                    # Try to discover the light_id if not found in the cache
                    lifx_light = get_light_by_id()
                    if lifx_light:
                        # TODO - remove duplicate code
                        lifx_light_label = lifx_light.mac_addr
                        try:
                            # label is not set when initialized
                            lifx_light_label = lifx_light.get_label()
                        except WorkflowException as error:
                            errStrings = ga.formatException()
                            ga.sendEventData("Exception", errStrings[0], errStrings[1])
                            xbmclog("get_label({}) - Exception - {}".format(lifx_light_label,str(error)))

                        found[light_id] = lifx_light

    xbmclog("get_lights_by_ids(light_ids={}) - Returning {} Lifx lights".format(light_ids, str(len(found))))
    hide_busy_dialog()
    return found

def get_lights_by_group():
    try:
        devices_by_group = lan.get_devices_by_group(group_id)
    except WorkflowException as error:
        errStrings = ga.formatException()
        ga.sendEventData("Exception", errStrings[0], errStrings[1])
        xbmclog("get_lights_by_group(group_id={}) - Exception - {}".format(group_id, str(error)))
    # device_ids = [device.get_label() for device in devices_by_group.get_device_list()]

    found = {}
    for device in devices_by_group.get_device_list():
        light_id = device.get_label()
        found[light_id] = lights.Light(light_id, device)

    return get_lights_by_ids(device_ids)

def get_light_by_id(light_id=''):
    global lights_cache
    device = None
    try:
        device = lan.get_device_by_name(light_id)
    except WorkflowException as error:
        errStrings = ga.formatException()
        ga.sendEventData("Exception", errStrings[0], errStrings[1])
        xbmclog("get_lights(refresh={}) - Exception - {}".format(refresh,str(error)))

    if device != None and device not in lights_cache:
        lights_cache.append(device)
        xbmclog("get_light_by_id(light_id={}) - Found new device".format(light_id))

    return device
