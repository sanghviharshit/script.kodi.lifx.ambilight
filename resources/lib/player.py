import xbmc

from tools import xbmclog

class Player(xbmc.Player):
    duration = 0
    playingvideo = False
    playlistlen = 0
    movie = False
    hue_service = None

    def __init__(self):
        xbmclog('In KodiPlayer.__init__()')
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        xbmclog('In KodiPlayer.onPlayBackStarted()')
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        self.playlistlen = playlist.size()
        self.playlistpos = playlist.getposition()
        self.playingvideo = True
        self.duration = self.getTotalTime()
        self.hue_service.state_changed("started", self.duration)

    def onPlayBackPaused(self):
        xbmclog('In KodiPlayer.onPlayBackPaused()')
        self.hue_service.state_changed("paused", self.duration)
        if self.isPlayingVideo():
            self.playingvideo = False

    def onPlayBackResumed(self):
        xbmclog('In KodiPlayer.onPlayBackResume()')
        self.hue_service.state_changed("resumed", self.duration)
        if self.isPlayingVideo():
            self.playingvideo = True
            if self.duration == 0:
                self.duration = self.getTotalTime()

    def onPlayBackStopped(self):
        xbmclog('In KodiPlayer.onPlayBackStopped()')
        self.hue_service.state_changed("stopped", self.duration)
        self.playingvideo = False
        self.playlistlen = 0

    def onPlayBackEnded(self):
        xbmclog('In KodiPlayer.onPlayBackEnded()')
        # If there are upcoming plays, ignore
        if self.playlistpos < self.playlistlen-1:
            return

        self.playingvideo = False
        self.hue_service.state_changed("stopped", self.duration)
