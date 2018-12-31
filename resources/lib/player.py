import xbmc

from tools import xbmclog
from ga_client import GoogleAnalytics

class Player(xbmc.Player):
    duration = 0
    playingvideo = False
    playlistlen = 0
    movie = False
    hue_service = None
    ga = None

    def __init__(self):
        xbmclog('In KodiPlayer.__init__()')
        xbmc.Player.__init__(self)
        self.ga = GoogleAnalytics()

    def onAVStarted(self):
        xbmclog('In KodiPlayer.onAVStarted()')
        if self.isPlayingVideo():
            self.playingvideo = True
            self.duration = self.getTotalTime()
            self.ga.sendEventData("Playback", "Started", "Video")
            self.ga.sendScreenView("Video")
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            self.playlistlen = playlist.size()
            self.playlistpos = playlist.getposition()
            self.hue_service.state_changed("started", self.duration)

    def onPlayBackPaused(self):
        xbmclog('In KodiPlayer.onPlayBackPaused()')
        if self.isPlayingVideo():
            self.ga.sendEventData("Playback", "Paused", "Video")
            self.hue_service.state_changed("paused", self.duration)
            self.playingvideo = False

    def onPlayBackResumed(self):
        xbmclog('In KodiPlayer.onPlayBackResume()')
        if self.isPlayingVideo():
            self.ga.sendEventData("Playback", "Resumed", "Video")
            self.hue_service.state_changed("resumed", self.duration)
            self.playingvideo = True
            if self.duration == 0:
                self.duration = self.getTotalTime()

    def onPlayBackStopped(self):
        xbmclog('In KodiPlayer.onPlayBackStopped()')
        self.ga.sendEventData("Playback", "Stopped", "Video")
        self.hue_service.state_changed("stopped", self.duration)
        self.playingvideo = False
        self.playlistlen = 0

    def onPlayBackEnded(self):
        xbmclog('In KodiPlayer.onPlayBackEnded()')
        self.ga.sendEventData("Playback", "Ended", "Video")
        # If there are upcoming plays, ignore
        if self.playlistpos < self.playlistlen-1:
            return

        self.playingvideo = False
        self.hue_service.state_changed("stopped", self.duration)
