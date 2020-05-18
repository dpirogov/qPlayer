#!/usr/bin/env python3

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from playerui import Ui_MainWindow


class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.playlist = playlist

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index):
        return self.playlist.mediaCount()


class App(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)

        self.player = QMediaPlayer()
        self.player.setVolume(50)
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.btnPlay.pressed.connect(self.player.play)
        self.btnPause.pressed.connect(self.player.pause)

        self.sldVolume.valueChanged.connect(self.player.setVolume)
        self.sldPosition.valueChanged.connect(self.player.setPosition)
        self.btnPrevious.pressed.connect(self.playlist.previous)
        self.btnNext.pressed.connect(self.playlist.next)
        self.btnAdd.pressed.connect(self.open_file)
        self.btnMute.pressed.connect(self.mute)

        self.player.durationChanged.connect(self.update_meta)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)

        self.model = PlaylistModel(self.playlist)
        self.listPlaylist.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)
        selection_model = self.listPlaylist.selectionModel()
        selection_model.selectionChanged.connect(self.playlist_selection_changed)

    def update_duration(self, duration):
        self.sldPosition.setMaximum(duration)

        if duration >= 0:
            self.lbTotalTime.setText(self.hhmmss(duration))

    def update_position(self, position):
        if position >= 0:
            self.lbPosition.setText(self.hhmmss(position))

        # Disable the events to prevent updating triggering a setPosition event (can cause stuttering).
        self.sldPosition.blockSignals(True)
        self.sldPosition.setValue(position)
        self.sldPosition.blockSignals(False)

    def hhmmss(self, ms):
        ms = int(ms)
        seconds = (ms / 1000) % 60
        seconds = int(seconds)
        minutes = (ms / (1000 * 60)) % 60
        minutes = int(minutes)
        hours = (ms / (1000 * 60 * 60)) % 60
        return ("%d:%02d:%02d" % (hours, minutes, seconds)) if hours >= 1 else ("%d:%02d" % (minutes, seconds))

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "mp3 Audio (*.mp3)")

        if path:
            self.playlist.addMedia(
                QMediaContent(
                    QUrl.fromLocalFile(path)
                )
            )

        self.model.layoutChanged.emit()

    def playlist_selection_changed(self, ix):
        # We receive a QItemSelection from selectionChanged.
        i = ix.indexes()[0].row()
        self.playlist.setCurrentIndex(i)

    def playlist_position_changed(self, i):
        if i > -1:
            ix = self.model.index(i)
            self.listPlaylist.setCurrentIndex(ix)
    def showmetadata(self):
        self.metadatakeylist = self.player.availableMetaData()
        self.lbTitle.setText(self.player.metaData("ContributingArtist") + " - " + self.player.metaData("Title"))
        for key in self.metadatakeylist:
            print(key + ":")
            print(self.player.metaData(key))
            print("\n")

    def update_meta(self):
        title = self.player.metaData("Title")
        artist = self.player.metaData("ContributingArtist")
        self.lbTitle.setText(title)
        self.lbArtist.setText(artist)

        if self.player.metaData("CoverArtImage") is None:
            cover = QPixmap("defCover.png")
            cover = QPixmap.scaled(cover, 170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.picCover.setPixmap(cover)
            self.picCover.show()
        else:
            cover = QPixmap.fromImage(self.player.metaData("CoverArtImage"))
            cover = QPixmap.scaled(cover, 170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.picCover.setPixmap(cover)
            self.picCover.show()


    def mute(self):
        if self.player.isMuted():
            self.player.setMuted(False)
        else:
            self.player.setMuted(True)


    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.playlist.addMedia(
                QMediaContent(url)
            )

        self.model.layoutChanged.emit()

        # If not playing, seeking to first of newly added + play.
        if self.player.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(e.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.player.play()


def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()

#TODO Fix duration timing
#TODO Add icons
#TODO Make scrollable labels
#TODO Make interface better
