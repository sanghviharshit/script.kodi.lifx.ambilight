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
    sendMetrics = False
    total_lights = 0

    if lights_cache is None or refresh == True:
        sendMetrics = True

    if lights_cache is None or len(lights_cache) == 0 or refresh == True:
        try:
            lan.discover_devices()
            lights_cache = lan.get_lights()
            xbmclog("get_lights(refresh={}) - Found {} Lifx lights".format(refresh, str(len(lights_cache))))
        except WorkflowException as error:
            errStrings = ga.formatException()
            ga.sendExceptionData(errStrings[0])
            ga.sendEventData("Exception", errStrings[0], errStrings[1])
            xbmclog("get_lights(refresh={}) - Exception - {}".format(refresh,str(error)))

        if lights_cache != None and len(lights_cache) > 0:
            sendMetrics = True
            products_list = {}
            for lifx_light in lights_cache:
                product = None
                product_name = None
                try:
                    lifx_light.refresh()
                    product = lifx_light.get_product()
                    product_name = lifx_light.get_product_name()
                except WorkflowException as error:
                    errStrings = ga.formatException()
                    ga.sendExceptionData(errStrings[0])
                    ga.sendEventData("Exception", errStrings[0], errStrings[1])
                    xbmclog("Exception - {}".format(str(error)))

                product_str = "{}".format(product)
                if product_name != None:
                    product_str += " ({})".format(product_name)
                try:
                    products_list[product_str] += 1
                except KeyError:
                    products_list[product_str] = 1

            xbmclog("Product list: {}".format(products_list))
            for product, count in products_list.items():
                # Collect metrics to help prioritize support for more device types
                ga.sendEventData("Metrics", "Devices", product, count, 1)   # Category, Action, Label, Value, Non-interactive

        if lights_cache is not None:
            total_lights = len(lights_cache)
        if sendMetrics:
            ga.sendEventData("Metrics", "Devices", "Total", total_lights, 1)
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
                except WorkflowException as error:
                    errStrings = ga.formatException()
                    ga.sendExceptionData(errStrings[0])
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
                    ga.sendExceptionData(errStrings[0])
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
                            ga.sendExceptionData(errStrings[0])
                            ga.sendEventData("Exception", errStrings[0], errStrings[1])
                            xbmclog("get_label({}) - Exception - {}".format(lifx_light_label,str(error)))

                        found[light_id] = lifx_light

    xbmclog("get_lights_by_ids(light_ids={}) - Returning {} Lifx lights".format(light_ids, str(len(found))))
    hide_busy_dialog()
    return found

# Unused Code for now
def get_lights_by_group():
    try:
        devices_by_group = lan.get_devices_by_group(group_id)
        found = {}
        device_ids = [device.get_label() for device in devices_by_group.get_device_list()]
        xbmclog("get_lights_by_group(group_id={}) - device_ids - {}".format(group_id, device_ids))
        for device in devices_by_group.get_device_list():
            if device.is_light():
                light_id = device.get_label()
                found[light_id] = device
    except WorkflowException as error:
        errStrings = ga.formatException()
        ga.sendExceptionData(errStrings[0])
        ga.sendEventData("Exception", errStrings[0], errStrings[1])
        xbmclog("get_lights_by_group(group_id={}) - Exception - {}".format(group_id, str(error)))

    return get_lights_by_ids(device_ids)

def get_light_by_id(light_id=''):
    global lights_cache
    light = None
    try:
        device = lan.get_device_by_name(light_id)
        if device != None and device not in lights_cache and device.is_light():
            light = device
            lights_cache.append(light)
            xbmclog("get_light_by_id(light_id={}) - Found new device".format(light_id))
    except WorkflowException as error:
        errStrings = ga.formatException()
        ga.sendExceptionData(errStrings[0])
        ga.sendEventData("Exception", errStrings[0], errStrings[1])
        xbmclog("get_light_by_id(light_id={}) - Exception - {}".format(light_id,str(error)))

    return light
