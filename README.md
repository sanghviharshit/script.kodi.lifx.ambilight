# Lifx (Ambilight) Addon for Kodi

A [Kodi](https://kodi.tv/) add-on for your [Lifx](http://www.lifx.com/) lights.

[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/sanghviharshit)

## Compatibility
|Kodi v16|Kodi v17+|
|--------|---------|
|Release v0.1.3|Branch "develop"|
|[download](https://github.com/sanghviharshit/script.kodi.lifx.ambilight/archive/0.1.3.zip)|[download](https://github.com/sanghviharshit/script.kodi.lifx.ambilight/archive/develop.zip)|


## Description

This [Kodi](https://kodi.tv/) add-on controls [Lifx](http://www.lifx.com/) lights based on the following light groups, fully configurable using the setup wizard from addon settings.

### Theater Group
  Lights in the theater group act like wall lights in a typical theater. When playback starts the lights dim and they undim when playback is paused or ends. If you only want some of the lights to undim during pause, it is possible to configure "subgroup" in add-on settings -> Theater and only dim the subgroup.
### Ambilight Group
  **[Ambilight](https://en.wikipedia.org/wiki/Ambilight)** group tries to control the lights similarly to modern ambilight TVs. The add-on tries to figure out the most represented colors and brightness in each frame and change the lights to reflect that. They can also be configured to work similarly to theater group when playback is paused.
  Turns the Lifx lights in `Ambilight` group in to a room-sized  environment.

### Static Group
  Static lights act opposite to the theater lights -- they are turned on when playback starts, turned off when you pause the playback and go back to initial state after the playback stops.

## Features
- Fully customizable
  - Each group fully configurable with a discovery and selection wizard.
  - `Override` brightness/hue/saturation/temperature for different states in each of the theater/ambilight/static group - playback started/resumed, paused and stopped.
  - Option to forcefully `turn on` or `ignore` lights which are powered off (not switched off)
  - Option to `flash` lights once on discovery
  - Option to disable the Theater/Ambilight mode for `short videos`
    - Option to customize what is considered a *short* video
  - ~~`Experimental`: Option to undim lights when `credits` start rolling. (Uses ChapterDB.org)~~
    - ~~Option to delay the credits start time.~~
    - ~~*Does not always work, may ruin your movie-watching experience*~~
  - `Restore` the lights to original states (color and power) when movie stops.
- 3 groups for your Lifx powered media center room
  - `Theatre`
    - `Dim` or Turn off the lights when Movie starts `playing`
    - `Undim` or Turn on the lights when you `pause` the movie
    - Return the lights to `original` settings when Movie ends.
    - Option to configure Fading time to be `proportional` to the current brightness. (e.g. take 7 seconds to change brightness from 100% to 30%, while taking 5 seconds to change from 50% to 0%)
  - `Ambilight`
    - Option to `Dim` the lights when Movie starts playing
    - Option to change `minimum` and `maximum` brightness
    - Option to configure threshold (minimum) values for brightness and saturation when calculating the color/brightness from picture frame.
    - Option to set different colors for different lights or same color for all lights
    - Option to configure bias value (lower the bias - more variety of colors, higher the bias - less variety of colors, but higher accuracy)
  - `Static`
    - Option to set random color to the static lights that turn on when the video playback starts.
    - Option to override hue, saturation, brightness or temperature values



## Demo
### Kodi + Lifx + Ambilight + Movie (LOTR) Test
[![Kodi + Lifx + Ambilight + Movie (LOTR) Test](http://img.youtube.com/vi/LZui0Ui4hTQ/0.jpg)](http://www.youtube.com/watch?v=LZui0Ui4hTQ "Kodi + Lifx + Ambilight + Movie (LOTR) Test")

### Kodi (XBMC) + Lifx + Ambilight + Video Test
[![Kodi (XBMC) + Lifx + Ambilight + Video Test](http://img.youtube.com/vi/UbWo8LaXDlE/0.jpg)](http://www.youtube.com/watch?v=UbWo8LaXDlE "Kodi (XBMC) + Lifx + Ambilight + Video Test")

### Other Ambient Lighting Demo
[![Kodi Philips hue Ambilight mode](http://img.youtube.com/vi/iQ6W_JA42KQ/default.jpg)](http://www.youtube.com/watch?v=iQ6W_JA42KQ "Kodi Philips hue Ambilight mode")
[![Kodi und Hue](http://img.youtube.com/vi/sOO6BBXTcYM/default.jpg)](http://www.youtube.com/watch?v=sOO6BBXTcYM "Kodi und Hue")
[![Philips Hue Kodi Ambilight Color Demo using two Hue Blooms - 4k](http://img.youtube.com/vi/5aU4EZEX0is/default.jpg)](http://www.youtube.com/watch?v=5aU4EZEX0is "Philips Hue Kodi Ambilight Color Demo using two Hue Blooms - 4k")
[![Kodi + Philips hue](http://img.youtube.com/vi/i3bzet-EbWc/default.jpg)](http://www.youtube.com/watch?v=i3bzet-EbWc "Kodi + Philips hue")
[![Kodi with Hue ambilight](http://img.youtube.com/vi/_t4RpS4Dwag/default.jpg)](http://www.youtube.com/watch?v=_t4RpS4Dwag "Kodi + Philips hue")

## Screenshots
### [v1.0.0 (Mar 09, 2018)](https://imgur.com/gallery/lomzL)



## Installation

[![Installation](https://i.imgur.com/zBTnlvo.gif)](https://i.imgur.com/zBTnlvo.gif)

- Download the add-on as a ZIP file from the top of this page
  - (Click on the green "Clone or download button" then click on the "Download ZIP" link)
- Open Kodi
- Go to System -> Settings -> Add-ons -> Install from zip file.
- Select the zip file from the location where you downloaded the zip file
- Restart Kodi and configure the add-on:
  - System -> Settings -> Add-ons -> Enabled add-ons -> Services -> Lifx Ambilight
  - Configure available settings.


## Configurations

[![Configurations](https://i.imgur.com/1tZhC9G.gif)](https://i.imgur.com/1tZhC9G.gif)

## Example Use Case
I have 7 Lifx lights - `TV Left`, `TV Right`, `Ceiling 1`, `Ceiling 2`, `Kitchen 1`, `Kitchen 2`, `Hallway`.

I want to use
  - `TV Left`, `TV Right` as ambilight.
  - `Ceilin 1`, `Ceiling 2` as theater lights, so they dim/turn off when the video playback starts, undim on pause and restore original state when video stops.
  - `Hallway` light as `Static` light that will turn on when we are watching movie
  - Leave `Kitchen 1` and `Kitchen 2` untouched.

For this, you can configure the addon settings as the following
  - Click start discovery to find all your Lifx lights first.
  - Click Setup for each group that you want to configure and select the lights you want to add in each of those groups.
  - Next, configure the settings for each of the groups.
  - Click ok to save the settings.


## Changelog

- [Link](https://github.com/sanghviharshit/script.kodi.lifx.ambilight/blob/develop/changelog.txt
)

## Known Issues

**Raspberry Pi users:**
  - Save the add-on configuration by exiting Kodi before shutting down the Pi completely
Ambilight mode doesn't work on a Raspberry Pi due to the way it renders video

**ARM based devices/Nexus Player/Any other Android devices:**
  - Try disabling Mediacodec (Surface) in Settings > Video> Acceleration. This seems to fix the problem. [Reference](https://github.com/michaelrcarroll/script.kodi.hue.ambilight/issues/30)

**AppleTV 4K:**
  - Ambilight mode doesn't properly work with 4k-HD codecs (>1080p) when "hardware acceleration AVFoundation" is enabled.

**Nvidia Shield / most Android boxes:**
  - Ambilight mode doesn't properly work with 4k-HD codecs (>1080p) when "allow hardware acceleration - Mediacodec (Surface)" is enabled.

**Addon settings:**
  - When configuring groups, for window to properly react, one has to press OK after selecting the bulbs and then OK to exit the configuration and re-enter it

## Todo:
  - Credits undimming was removed, will be reimplemented when the state checking gets more robust
  - Add tests
  - Theater sunset/sunrise
  - Force lights `on` based on time of day
  - Lifx Z Multi-zone support
  - Update screenshots
  - Update Demo video
  - Add better descriptions for each settings for more use cases
  - Bring the addon debug setting back
  - IFTTT integration
  - Home assistant integration ?
  - Maintain kodi branch of sanghviharshit/lifxlan repository
  - Add settings for broadcast IP address for LifxLAN discovery, since we are not using netifaces module from LifxLAN
  - Rename the addon to [script.service.lifxkodi](https://kodi.wiki/view/Add-on_structure#Directory_Name)
  - Translations for settings


## Support
  - If you find a problem or missing feature, open an issue or a pull requests on https://github.com/sanghviharshit/script.kodi.lifx.ambilight
  - To have a higher chance of issue being solved, please attach a log file. To record one, go to settings wheel -> System settings -> Logging -> Enable Debug Logging and follow the procedure at http://kodi.wiki/view/Log_file/Easy


## Credits

- [@mclarkk](https://github.com/mclarkk) for creating [lifxlan](https://github.com/mclarkk/lifxlan/) - a Python library for accessing LIFX devices locally using the official LIFX LAN protocol.
- [@mpolednik](https://github.com/mpolednik), [@michaelrcarroll](https://github.com/michaelrcarroll) and others for maintaining [script.kodi.hue.ambilight](https://github.com/mpolednik/script.kodi.hue.ambilight), originally started by [@cees-elzinga](https://github.com/mclarkk/cees-elzinga)


## Pingbacks

  - http://forum.kodi.tv/showthread.php?tid=289230
  - https://www.reddit.com/r/lifx/comments/4z6wpt/kodi_xbmc_lifx_ambilight_video_test/
  - https://www.reddit.com/r/Addons4Kodi/comments/501xm9/lifx_ambilight_addon_for_kodi/
  - https://community.lifx.com/t/kodi-add-on-for-lifx-lights-with-ambilight-support/1673?u=harct

[![Analytics](https://ga-beacon.appspot.com/UA-59542024-4/script.kodi.lifx.ambilight/)](https://github.com/igrigorik/ga-beacon)
