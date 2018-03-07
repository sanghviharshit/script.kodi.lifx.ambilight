import socket
import time

import lights
# import tools

from lifxlan import *
from tools import *

lan = LifxLAN()

"""
try:
    import requests
except ImportError:
    tools.notify("Kodi Hue", "ERROR: Could not import Python requests")
"""

lights_cache = None

def user_exists(bridge_ip, bridge_user, notify=True):
    return True
    """
    req = requests.get('http://{}/api/{}/config'.format(
        bridge_ip, bridge_user))
    res = req.json()

    success = False
    try:
        success = bridge_user in res['whitelist']
    except KeyError:
        success = False

    if notify:
        import tools
        if success:
            tools.notify("Kodi Hue", "Connected")
        else:
            tools.notify("Kodi Hue", "Could not connect to bridge")

    return success
    """

def discover():
    show_busy_dialog()
    lifx_lights = get_lights("127.0.0.1", "kodi", refresh=True)
    if lifx_lights and len(lifx_lights) > 0:
      xbmclog("discover() - Found {0} Lifx lights".format(str(len(lifx_lights))))
      notify("Kodi Lifx", "Found {0} Lifx lights".format(str(len(lifx_lights))))
    else:
      xbmclog("discover() - No Lifx lights found")
      notify("Kodi Lifx", "No Lifx lights found")

    """
    bridge_ip = _discover_upnp()
    if bridge_ip is None:
        bridge_ip = _discover_nupnp()

    return bridge_ip
    """
    hide_busy_dialog()
    return "127.0.0.1"

def create_user(bridge_ip, notify=True):
    """
    device = 'kodi#ambilight'
    data = '{{"devicetype": "{}"}}'.format(device)

    res = 'link button not pressed'
    while 'link button not pressed' in res:
        if notify:
            import tools
            tools.notify('Kodi Hue', 'Press link button on bridge')
        req = requests.post('http://{}/api'.format(bridge_ip), data=data)
        res = req.text
        time.sleep(3)

    res = req.json()
    username = res[0]['success']['username']

    return username
    """
    return "kodi"


def get_lights(bridge_ip, username, refresh=False):
    # return get_lights_by_ids(bridge_ip, username)
    global lights_cache
    if lights_cache == None or len(lights_cache) == 0 or refresh == True:
        try:
            lights_cache = lan.get_lights()
            xbmclog("get_lights() - Found {} Lifx lights".format(str(len(lights_cache))))
        except:
            pass
    else:
        xbmclog("get_lights() - Returning {} cached Lifx lights".format(str(len(lights_cache))))
    return lights_cache


def get_lights_by_ids(bridge_ip, username, light_ids=None):
    """
    req = requests.get('http://{}/api/{}/lights'.format(bridge_ip, username))
    res = req.json()

    if light_ids is None:
        light_ids = res.keys()

    if light_ids == ['']:
        return {}

    found = {}
    for light_id in light_ids:
        found[light_id] = lights.Light(bridge_ip, username, light_id,
                                       res[light_id])
   return found
   """
    show_busy_dialog()
    found = {}
    xbmclog("In get_lights_by_ids() - light_ids - {}".format(light_ids))
    if light_ids == None:
        lifx_lights = get_lights(bridge_ip, username)
        if lifx_lights and len(lifx_lights) > 0:
            lifx_lights_ids = [lifx_light.get_label() for lifx_light in lifx_lights]
            xbmclog("get_lights_by_ids() - lifx_lights - {}".format(lifx_lights_ids))
            for lifx_light in lifx_lights:
                try:
                    light_id = lifx_light.get_label()
                    xbmclog("get_lights_by_ids() - Adding {}".format(light_id))
                    found[light_id] = lights.Light(bridge_ip, username, light_id,
                                                lifx_light)
                except:
                    pass
    elif light_ids == ['']:
        found = {}
    else:
        lifx_lights = get_lights(bridge_ip, username)
        if lifx_lights and len(lifx_lights) > 0:
            for light_id in light_ids:
                for lifx_light in lifx_lights:
                    if lifx_light.get_label() == light_id:
                        xbmclog("get_lights_by_ids() - Found {}".format(light_id))
                        found[light_id] = lights.Light(bridge_ip, username, light_id,
                                                lifx_light)

    xbmclog("get_lights_by_ids() - Returning {} Lifx lights".format(str(len(found))))
    hide_busy_dialog()
    return found

def get_lights_by_group(bridge_ip, username, group_id):
    """
    req = requests.get('http://{}/api/{}/groups/{}'.format(
        bridge_ip, username, group_id))
    res = req.json()

    light_ids = res['lights']
    return get_lights_by_ids(bridge_ip, username, light_ids)
    """
    try:
        devices_by_group = lan.get_devices_by_group(group_id)
    except:
        pass
    # device_ids = [device.get_label() for device in devices_by_group.get_device_list()]

    found = {}
    for device in devices_by_group.get_device_list():
        light_id = device.get_label()
        found[light_id] = lights.Light(bridge_ip, username, light_id,
                                       device)

    return get_lights_by_ids(bridge_ip, username, device_ids)

def _discover_upnp():
    port = 1900
    ip = "239.255.255.250"
    bridge_ip = None
    address = (ip, port)
    data = '''M-SEARCH * HTTP/1.1
    HOST: {}:{}
    MAN: ssdp:discover
    MX: 3
    ST: upnp:rootdevice
    '''.format(ip, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    for _ in range(10):
        try:
            sock.sendto(data, address)
            recv, addr = sock.recvfrom(2048)
            if 'IpBridge' in recv and 'description.xml' in recv:
                bridge_ip = recv.split('LOCATION: http://')[1].split(':')[0]
                break
            time.sleep(3)
        except socket.timeout:
            # if the socket times out once, its probably not going to
            # complete at all. fallback to nupnp.
            break

    return bridge_ip

def _discover_nupnp():
    # verify false hack until meethue fixes their ssl cert.
    req = requests.get('https://www.meethue.com/api/nupnp', verify=False)
    res = req.json()
    bridge_ip = None
    if res:
        bridge_ip = res[0]["internalipaddress"]

    return bridge_ip
