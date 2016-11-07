# Lifx (Ambilight) Addon for Kodi

A [Kodi](https://kodi.tv/) add-on that controls [Lifx](http://www.lifx.com/) lights. In `Theater mode` the add-on dims the Lifx lights as soon as a movie starts playing, and turns the lights back to original settings once the movie is done. `Ambilight mode` turns your Lifx lights in a room-sized **[Ambilight](https://en.wikipedia.org/wiki/Ambilight).**

>Ambilight creates light effects around the television that correspond to the video content. Philips claims that a "more immersive viewing experience" can result. Ambilight is a lighting system that actively adjusts both brightness and color based upon picture content. Integrated into the television cabinet, Ambilight technology is aimed to enable the viewer to see more picture detail, contrast and color while eliminating on-screen reflections.

>Ambilight technology works by projecting light from the rear of the TV cabinet in a very wide range of colors, shades and intensities. Viewers can choose to have Ambilight follow the color and brightness of the programme content – automatically changing with the colors on the screen

## Features

- Fully customizable
  - Select `All lights` or a `Group of lights`.
  - `Override` brightness/hue/saturation for different states in Ambilight mode - playback started/resumed and paused.
  - Option to forcefully `turn on` or `ignore` lights which are powered off (not switched off)
  - Option to `flash` lights once on discovery
  - Option to disable the Theater/Ambilight mode for `short videos`
    - Option to customize what is considered a *short* video
  - `Experimental`: Option to undim lights when `credits` start rolling. (Uses ChapterDB.org)
    - Option to delay the credits start time.
    - *Does not always work, may ruin your movie-watching experience*
  - `Restore` the lights to original states (color and power) when movie stops.
- 2 Modes for your Lifx powered media center room
  - `Theatre Mode`
    - `Dim` or Turn off the lights when Movie starts `playing`
    - `Undim` or Turn on the lights when you `pause` the movie
    - Return the lights to `original` settings when Movie ends.
    - Option to configure Fading time to be `proportional` to the current brightness. (e.g. take 7 seconds to change brightness from 100% to 30%, while taking 5 seconds to change from 50% to 0%)
  - `Ambilight Mode`
    - Option to `Dim` the lights when Movie starts playing
    - Option to change `minimum` and `maximum` brightness

## Demo
### Kodi + Lifx + Ambilight + Movie (LOTR) Test 
[![Kodi + Lifx + Ambilight + Movie (LOTR) Test](http://img.youtube.com/vi/LZui0Ui4hTQ/0.jpg)]
(http://www.youtube.com/watch?v=LZui0Ui4hTQ "Kodi + Lifx + Ambilight + Movie (LOTR) Test")

### Kodi (XBMC) + Lifx + Ambilight + Video Test
[![Kodi (XBMC) + Lifx + Ambilight + Video Test](http://img.youtube.com/vi/UbWo8LaXDlE/0.jpg)]
(http://www.youtube.com/watch?v=UbWo8LaXDlE "Kodi (XBMC) + Lifx + Ambilight + Video Test")

### Other Ambient Lighting Demo
[![Kodi Philips hue Ambilight mode](http://img.youtube.com/vi/iQ6W_JA42KQ/default.jpg)](http://www.youtube.com/watch?v=iQ6W_JA42KQ "Kodi Philips hue Ambilight mode")
[![Kodi und Hue](http://img.youtube.com/vi/sOO6BBXTcYM/default.jpg)](http://www.youtube.com/watch?v=sOO6BBXTcYM "Kodi und Hue")
[![Philips Hue Kodi Ambilight Color Demo using two Hue Blooms - 4k](http://img.youtube.com/vi/5aU4EZEX0is/default.jpg)](http://www.youtube.com/watch?v=5aU4EZEX0is "Philips Hue Kodi Ambilight Color Demo using two Hue Blooms - 4k")
[![Kodi + Philips hue](http://img.youtube.com/vi/i3bzet-EbWc/default.jpg)](http://www.youtube.com/watch?v=i3bzet-EbWc "Kodi + Philips hue")
[![Kodi with Hue ambilight](http://img.youtube.com/vi/_t4RpS4Dwag/default.jpg)](http://www.youtube.com/watch?v=_t4RpS4Dwag "Kodi + Philips hue")

## [Screenshots](http://imgur.com/gallery/V9Dxh)
#### Addon Information
[![Addon Information](http://i.imgur.com/9eVRc8Nm.jpg)](http://i.imgur.com/9eVRc8N.jpg)

#### Addon Settings
[![Addon Settings - Main](http://i.imgur.com/3kpdmqVt.jpg)](http://i.imgur.com/3kpdmqV.jpg)
[![Addon Settings - Theater - 1](http://i.imgur.com/BmbPCR3t.jpg)](http://i.imgur.com/BmbPCR3.jpg)
[![Addon Settings - Theater - 2](http://i.imgur.com/K1Yr0nXt.jpg)](http://i.imgur.com/K1Yr0nX.jpg)
[![Addon Settings - Ambilight - 1](http://i.imgur.com/cL2EGTYt.jpg)](http://i.imgur.com/cL2EGTY.jpg)
[![Addon Settings - Ambilight - 2](http://i.imgur.com/S5yRWxlt.jpg)](http://i.imgur.com/S5yRWxl.jpg)
[![Addon Settings - Advance](http://i.imgur.com/wcawBM0t.jpg)](http://i.imgur.com/wcawBM0.jpg)


## Installation

- Download the add-on as a ZIP file from the top of this page
  - (Right click on the "ZIP" icon and select "Download Linked File")
- Open Kodi
- Go to System -> Settings -> Add-ons -> Install from zip file
- Restart Kodi and configure the add-on:
- System -> Settings -> Add-ons -> Enabled add-ons -> Services -> Lifx Ambilight
- Configure available settings.

## Settings for specific Use cases

**I have 3 (color/white) ceiling bulbs, 2 color bulbs behind the TV in my living room, and 4 more bulbs in my bedroom/bathroom. Would it be possible to set it up so that the 3 ceiling bulbs would dim (theater mode), use the 2 color lamps behind TV as ambilight, and don't use the 4 bulbs in bedroom/bathroom at all?**

  - From your lifx app
    1. Add the 3 ceiling bulbs to a separate group (e.g. theater)
    2. Add the 2 color lamps behind TV to a separate group (e.g. ambilight)
  - Now from addon settings
    1. In the main settings, select the mode as Ambilight mode and enable for group of lights instead of All lights and use the group name from previous steps (e.g. ambilight lamps).
    2. In the Ambilight settings - enable Dim before playback for group of lights and use appropriate group name (e.g. theater).

## Issues

**Raspberry Pi users:**
  - Save the add-on configuration by exiting Kodi before shutting down the Pi completely
Ambilight mode doesn't work on a Raspberry Pi due to the way it renders video

**ARM based devices/Nexus Player/Any other Android devices:**
  - Try disabling Mediacodec (Surface) in Settings > Video> Acceleration. This seems to fix the problem. [Reference](https://github.com/michaelrcarroll/script.kodi.hue.ambilight/issues/30)

**Other issues:**
  - Please use Github issue tracker for reporting new issues.

## Credits

- [@mclarkk](https://github.com/mclarkk) for creating [lifxlan](https://github.com/mclarkk/lifxlan/) - a Python library for accessing LIFX devices locally using the official LIFX LAN protocol.
- [@mpolednik](https://github.com/mpolednik), [@michaelrcarroll](https://github.com/michaelrcarroll) and others for maintaining [script.kodi.hue.ambilight](https://github.com/mpolednik/script.kodi.hue.ambilight), originally started by [@cees-elzinga](https://github.com/mclarkk/cees-elzinga)
  
## Pingbacks

  - http://forum.kodi.tv/showthread.php?tid=289230
  - https://www.reddit.com/r/lifx/comments/4z6wpt/kodi_xbmc_lifx_ambilight_video_test/
  - https://www.reddit.com/r/Addons4Kodi/comments/501xm9/lifx_ambilight_addon_for_kodi/
  - https://community.lifx.com/t/kodi-add-on-for-lifx-lights-with-ambilight-support/1673?u=harct

[![Analytics](https://ga-beacon.appspot.com/UA-59542024-4/script.kodi.lifx.ambilight/)](https://github.com/igrigorik/ga-beacon)
