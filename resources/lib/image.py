import colorsys
from tools import xbmclog

class HSVRatio:

    cyan_min = float(4.5 / 12.0)
    cyan_max = float(7.75 / 12.0)

    def __init__(self, hue=0.0, saturation=0.0, value=0.0, ratio=0.0, hue_count=0):
        self.h = hue
        self.s = saturation
        self.v = value
        self.ratio = ratio
        self.hue_count = hue_count

    def average(self, h, s, v):
        self.h = (self.h + h) / 2
        self.s = (self.s + s) / 2
        self.v = (self.v + v) / 2

    def average_value(self, overall_value):
        if self.ratio > 0.5:
            self.v = self.v * self.ratio + overall_value * (1 - self.ratio)
        else:
            self.v = (self.v + overall_value) / 2

    def hue(self, fullspectrum, bri_min, bri_max):
        """
        if not fullspectrum:
            if self.h > 0.065 and self.h < 0.19:
                self.h = self.h * 2.32
            elif self.s > 0.01:
                if self.h < 0.5:
                    # yellow-green correction
                    self.h = self.h * 1.17
                    # cyan-green correction
                    if self.h > self.cyan_min:
                        self.h = self.cyan_min
                else:
                    # cyan-blue correction
                    if self.h < self.cyan_max:
                        self.h = self.cyan_max
        """

        h = int(self.h * 65535)  # on a scale from 0 <-> 65535
        s = int(self.s * 255)
        v = int(self.v * 255)
        if v < bri_min:
            v = bri_min
        if v > bri_max:
            v = bri_max
        return h, s, v

    def __repr__(self):
        return 'h: %s s: %s v: %s ratio: %s hue_count: %s' % (
            self.h, self.s, self.v, self.ratio, self.hue_count)


class Screenshot:

    def __init__(self, pixels):
        self.pixels = pixels

    def most_used_spectrum(self, spectrum, saturation, value, size,
                           overall_value, color_variation, color_bias, num_hsv):
        # color bias/groups 6 - 36 in steps of 3
        # 6 = more variety of colors, 36 = similar colors
        # colorHueRatio will be between 60 and 10. 60=close to primary colors, 10 = more to original colors
        color_hue_ratio = 360 / color_bias

        hsv_ratios = []
        hsv_ratios_dict = {}

        for i in spectrum:
            # shift index to the right so that groups are centered on primary
            # and secondary colors
            color_index = int(
                ((i + color_hue_ratio / 2) % 360) / color_hue_ratio
            )
            # some info? - https://docs.gimp.org/en/gimp-tool-hue-saturation.html
            # i=0, ratio=60 => colorIndex = 0
            # i=60, ratio=60 => colorIndex = int(1.5)
            # i=90, ratio=60 => colorIndex = int(2)
            # i=120, ratio=60 => colorIndex = int(2.5)
            # i=180, ratio=60 => colorIndex = int(3.5)
            # i=270, ratio=60 => colorIndex = int(4.5)
            # i=330, ratio=60 => colorIndex = int(5.5)
            # i=360, ratio=60 => colorIndex = int(0.5)
            pixel_count = spectrum[i]

            try:
                hsvr = hsv_ratios_dict[color_index]
                # hsvr.average(i / 360.0, saturation[i], value[i])
                hsvr.h = hsvr.h + i / 360.0
                hsvr.s = hsvr.s + saturation[i]
                hsvr.v = hsvr.v + value[i]
                hsvr.hue_count = hsvr.hue_count + 1
                hsvr.ratio = hsvr.ratio + pixel_count / float(size)
            except KeyError:
                hsvr = HSVRatio(
                    i / 360.0, saturation[i],
                    value[i],
                    pixel_count / float(size),
                    1)

                hsv_ratios_dict[color_index] = hsvr
                hsv_ratios.append(hsvr)

        # Averaging hsvr by dividing the total of hsv by number pixel_count for each hue key
        for hsvr in hsv_ratios:
            hsvr.h = (float) (hsvr.h / hsvr.hue_count)
            hsvr.s = (float) (hsvr.s / hsvr.hue_count)
            hsvr.v = (float) (hsvr.v / hsvr.hue_count)

        color_count = len(hsv_ratios)

        if color_count > 1:
            # sort colors by popularity
            hsv_ratios = sorted(
                hsv_ratios,
                key=lambda hsvratio: hsvratio.ratio,
                reverse=True)

            for ratio in hsv_ratios:
                ratio.average_value(overall_value)

            if len(hsv_ratios) < num_hsv:
                hsv_ratios += [hsv_ratios[--1]] * (num_hsv - len(hsv_ratios))

            if not color_variation:
                # All ambilight lights will have one color
                # Return list of just the first hsv_ratio
                return [hsv_ratios[0]] * num_hsv

            return hsv_ratios

        return [HSVRatio()] * num_hsv

    def spectrum_hsv(self, pixels, threshold_bri, threshold_sat, color_variation, color_bias,
                     num_hsv):
        spectrum = {}
        saturation = {}
        value = {}

        size = int(len(pixels))

        v = 0
        r, g, b = 0, 0, 0
        tmph, tmps, tmpv = 0, 0, 0
        overall_value = 1

        for i in range(0, size, 4):
            r, g, b = _rgb_from_pixels(pixels, i)
            # https://docs.python.org/2/library/colorsys.html#colorsys.rgb_to_hsv
            tmph, tmps, tmpv = colorsys.rgb_to_hsv(
                float(r / 255.0), float(g / 255.0), float(b / 255.0))
            v += tmpv

            # skip low value and saturation
            if tmpv > threshold_bri:
                if tmps > threshold_sat:
                    h = int(tmph * 360) # Hue in 0-360
                    try:
                        spectrum[h] += 1
                        saturation[h] = saturation[h] + tmps
                        value[h] = value[h] + tmpv
                    except KeyError:
                        spectrum[h] = 1
                        saturation[h] = tmps
                        value[h] = tmpv

        # Averaging saturation and value for each hue key in spectrum
        # xbmclog("spectrum: {}, sat: {}, value: {}".format(spectrum, saturation, value))
        for i in spectrum:
            saturation[i] = saturation[i]/spectrum[i]
            value[i] = value[i]/spectrum[i]


        if size > 0:
            overall_value = v / float(len(pixels))

        return self.most_used_spectrum(
            spectrum, saturation, value, size, overall_value, color_variation, color_bias,
            num_hsv)


def _rgb_from_pixels(pixels, index, rgba=False):
    if rgba:
        return _rgb_from_pixels_rgba(pixels, index)
    else:  # probably BGRA
        return _rgb_from_pixels_rgba(pixels, index)[::-1]


def _rgb_from_pixels_rgba(pixels, index):
    return [pixels[index + i] for i in range(3)]
