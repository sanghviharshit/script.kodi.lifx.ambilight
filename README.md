# script.kodi.lifx.ambilight

A [Kodi](https://kodi.tv/) add-on that controls [Lifx](http://www.lifx.com/) lights. In `Theater mode` the add-on dims the Lifx lights as soon as a movie starts playing, and turns the lights back to original settings once the movie is done. `Ambilight mode` turns your Lifx lights in a room-sized **[ambilight](https://en.wikipedia.org/wiki/Ambilight).**

>Ambilight creates light effects around the television that correspond to the video content. Philips claims that a "more immersive viewing experience" can result. Ambilight is a lighting system that actively adjusts both brightness and color based upon picture content. Integrated into the television cabinet, Ambilight technology is aimed to enable the viewer to see more picture detail, contrast and color while eliminating on-screen reflections.

>Ambilight technology works by projecting light from the rear of the TV cabinet in a very wide range of colors, shades and intensities. Viewers can choose to have Ambilight follow the color and brightness of the programme content – automatically changing with the colors on the screen

## Features

- Fully customizable
  - Select `All lights` or a `Group of lights`.
  - `Override` brightness/hue/saturation for different states in ambilight mode - playback started/resumed and paused.
  - Option to forcefully `turn on` or `ignore` lights which are powered off (not switched off)
  - Option to `flash` lights once on discovery
  - Option to disable the theatre/ambilight mode for `short videos`
    - Option to customize what is considered a *short* video
  - `Experimental`: Option to undim lights when `credits` start rolling. (Uses ChapterDB.org)
    - Option to delay the credits start time.
    - *does not always work, may ruin your movie-watching experience*
  
- 2 Modes for your Lifx powered media center room
  - `Theatre Mode`
    - `Dim` or Turn off the lights when Movie starts `playing`
    - `Undim` or Turn on the lights when you `pause` the movie
    - Return the lights to `original` settings when Movie ends.
    - Option to configure Fading time to be `proportional` to the current brighness. (e.g. take 7 seconds to change brighness from 100% to 30%)
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

## Installation

- Download the add-on as a ZIP file from the top of this page
  - (Right click on the "ZIP" icon and select "Download Linked File")
- Open Kodi
- Go to System -> Settings -> Add-ons -> Install from zip file
- Restart Kodi and configure the add-on:
- System -> Settings -> Add-ons -> Enabled add-ons -> Services -> Lifx Ambilight
- Configure available settings.

## Issues

**Raspberry Pi users:**
  - Save the add-on configuration by exiting Kodi before shutting down the Pi completely
Ambilight mode doesn't work on a Raspberry Pi due to the way it renders video

**ARM based devices/Nexus Player/Any other Android devices:**
  - Try disabling Mediacodec (Surface) in Settings > Video> Acceleration. This seems to fix the problem. [Reference](https://github.com/michaelrcarroll/script.kodi.hue.ambilight/issues/30)

**Other issues:**
  - Please use github issue tracker for reporting new issues.

## Credits

- [@mclarkk](https://github.com/mclarkk) for creating [lifxlan](https://github.com/mclarkk/lifxlan/) - a Python library for accessing LIFX devices locally using the official LIFX LAN protocol.
- [@mpolednik](https://github.com/mpolednik), [@michaelrcarroll](https://github.com/michaelrcarroll) and others for maintaining [script.kodi.hue.ambilight](https://github.com/mpolednik/script.kodi.hue.ambilight), originally started by [@cees-elzinga](https://github.com/mclarkk/cees-elzinga)
  
[![Analytics](https://ga-beacon.appspot.com/UA-59542024-4/script.kodi.lifx.ambilight/)](https://github.com/igrigorik/ga-beacon)
