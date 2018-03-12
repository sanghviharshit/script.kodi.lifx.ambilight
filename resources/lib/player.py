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

    def onPlayBackStarted(self):
        xbmclog('In KodiPlayer.onPlayBackStarted()')
        self.ga.sendEventData("Video", "Playback", "Started")
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        self.playlistlen = playlist.size()
        self.playlistpos = playlist.getposition()
        self.playingvideo = True
        self.duration = self.getTotalTime()
        self.hue_service.state_changed("started", self.duration)

    def onPlayBackPaused(self):
        xbmclog('In KodiPlayer.onPlayBackPaused()')
        self.ga.sendEventData("Video", "Playback", "Paused")
        self.hue_service.state_changed("paused", self.duration)
        if self.isPlayingVideo():
            self.playingvideo = False

    def onPlayBackResumed(self):
        xbmclog('In KodiPlayer.onPlayBackResume()')
        self.ga.sendEventData("Video", "Playback", "Resumed")
        self.hue_service.state_changed("resumed", self.duration)
        if self.isPlayingVideo():
            self.playingvideo = True
            if self.duration == 0:
                self.duration = self.getTotalTime()

    def onPlayBackStopped(self):
        xbmclog('In KodiPlayer.onPlayBackStopped()')
        self.ga.sendEventData("Video", "Playback", "Stopped")
        self.hue_service.state_changed("stopped", self.duration)
        self.playingvideo = False
        self.playlistlen = 0

    def onPlayBackEnded(self):
        xbmclog('In KodiPlayer.onPlayBackEnded()')
        self.ga.sendEventData("Video", "Playback", "Ended")
        # If there are upcoming plays, ignore
        if self.playlistpos < self.playlistlen-1:
            return

        self.playingvideo = False
        self.hue_service.state_changed("stopped", self.duration)
