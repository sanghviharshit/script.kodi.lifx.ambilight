import lights
from tools import xbmclog


class TheaterController(lights.Controller):
    def __init__(self, *args, **kwargs):
        super(TheaterController, self).__init__(*args, **kwargs)

    def on_playback_start(self, resume=False):
        # Theater dimming
        xbmclog('In TheaterController.on_playback_start() '
                'dimming theater group')

        # Let's keep only the last user-set state
        # BUT! Avoid theater subgroup if enabled
        subgroup = None
        if self.settings.theater_pause_dim_subgroup:
            subgroup = self.settings.theater_subgroup.split(',')

        if resume == False:
            self.save_state_as_initial(subgroup)

        hue = None
        if self.settings.theater_start_hue_override:
            hue=self.settings.theater_start_hue
        sat = None
        if self.settings.theater_start_sat_override:
            sat=self.settings.theater_start_sat

        bri=self.settings.theater_start_bri

        kel = None
        if self.settings.theater_start_kel_override:
            kel=self.settings.theater_start_kel

        self.set_state(
            hue=hue,
            sat=sat,
            bri=bri,
            kel=kel,
            force_on=self.settings.force_light_on,
        )

    def on_playback_pause(self):

        hue = None
        if self.settings.theater_pause_hue_override:
            hue=self.settings.theater_pause_hue
        sat = None
        if self.settings.theater_pause_sat_override:
            sat=self.settings.theater_pause_sat

        bri=self.settings.theater_pause_bri

        kel = None
        if self.settings.theater_pause_kel_override:
            kel=self.settings.theater_pause_kel

        if self.settings.theater_pause_dim_subgroup:
            xbmclog('In TheaterController.on_playback_pause() '
                    'undimming theater subgroup')
            if self.settings.theater_pause_bri_override:
                self.set_state(
                    hue=hue,
                    sat=sat,
                    bri=bri,
                    kel=kel,
                    lights=self.settings.theater_subgroup.split(','),
                    force_on=self.settings.force_light_on,
                )
            else:
                self.restore_initial_state(
                    lights=self.settings.theater_subgroup.split(','),
                    force_on=self.settings.force_light_on,
                )
        else:
            xbmclog('In TheaterController.on_playback_pause() '
                    'undimming theater group')
            if self.settings.theater_pause_bri_override:
                self.set_state(
                    hue=hue,
                    sat=sat,
                    bri=bri,
                    kel=kel,
                    force_on=self.settings.force_light_on,
                )
            else:
                self.restore_initial_state(
                    force_on=self.settings.force_light_on,
                )

    def on_playback_stop(self):
        xbmclog('In TheaterController.on_playback_stop() '
                'undimming theater group')

        hue = None
        if self.settings.theater_stop_hue_override:
            hue=self.settings.theater_stop_hue
        sat = None
        if self.settings.theater_stop_sat_override:
            sat=self.settings.theater_stop_sat

        bri=self.settings.theater_stop_bri

        kel = None
        if self.settings.theater_stop_kel_override:
            kel=self.settings.theater_stop_kel

        if self.settings.theater_stop_bri_override:
            self.set_state(
                hue=hue,
                sat=sat,
                bri=bri,
                kel=kel,
                force_on=self.settings.force_light_on,
            )
        else:
            self.restore_initial_state(
                force_on=self.settings.force_light_on,
            )
