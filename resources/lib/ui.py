import xbmcgui

import bridge
from tools import notify, xbmclog


def multiselect_lights(label, exclude, preselect):

    xbmclog('In multiselect_lights(label={}, exclude={}, preselect={})'.format(
                label, exclude, preselect)
            )

    lifx_lights = bridge.get_lights_by_ids()

    actual_lights = []
    items = []
    preselect_items = []
    index = 0

    if lifx_lights:
        for light_id, light in lifx_lights.items():
            if str(light_id) not in exclude.split(','):
                items.append(xbmcgui.ListItem(label=light_id))
                actual_lights.append(light_id)  # store the light's label instead of the light object
                if str(light_id) in preselect.split(','):
                    preselect_items.append(index)
                index += 1

        selected = xbmcgui.Dialog().multiselect(label, items,
                                                preselect=preselect_items)

        if selected:
            light_ids = [str(actual_lights[idx]) for idx in selected]
            return ','.join(light_ids)
        return ''


def discover_lights(hue):
    notify("Lifx Device Discovery", "Starting")
    num_lights = bridge.discover()
    if num_lights > 0:
        hue.connected = True
        # notify("Hue Bridge Discovery", "Finished")
    else:
        # notify("Hue Bridge Discovery", "Failed. Could not find bridge.")
        pass
