import os
import sys
import webbrowser
import csv
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QFileDialog, QApplication, QWidget, QTreeWidgetItem

import databaseTracks
import music
from SoundpadWidget import Ui_MainWindow
from newSetDialog import newSetDialog


class Soundpad(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Музыкальный плеер")
        self.show_sets()

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.media_slider)
        timer.start(500)

        self.quit.triggered.connect(self.close)
        self.add_files.triggered.connect(self.add_sounds)
        self.save_cur_list.triggered.connect(self.export_list)
        self.add_new_list.triggered.connect(self.add_set)
        self.folders.itemDoubleClicked.connect(self.change_set)
        self.sounds.itemDoubleClicked.connect(self.tracks_click)
        self.sounds.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sounds.customContextMenuRequested.connect(self.get_sounds_menu)
        self.folders.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.folders.customContextMenuRequested.connect(self.get_folders_menu)
        self.player = QtMultimedia.QMediaPlayer()
        self.cur_track = None
        self.cur_list = None
        self.player = QtMultimedia.QMediaPlayer()
        self.playBtn_2.clicked.connect(self.player.play)
        self.pauseBtn.clicked.connect(self.player.pause)
        self.stopBtn.clicked.connect(self.player.stop)
        self.headphonesBtn.clicked.connect(self.mute_headphones)
        self.headphonesSlider.sliderMoved.connect(self.player.setVolume)
        self.show_maximized.triggered.connect(self.showMaximized)
        self.action_4.triggered.connect(lambda: webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.checkBox.clicked.connect(self.show_tracks)
        self.load_new_list.triggered.connect(self.import_list)
        self.showMaximized()

    def media_slider(self):
        if self.player.isSeekable():
            self.trackSlider.setValue(int(self.player.position() / self.player.duration() * 100))

    def change_set(self, item, column):
        self.cur_list = item.text(column)
        self.show_tracks()

    def hex_to_rgb(self, value: str):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def getCurWidget(self, row, color):
        row_len = len(row)
        item = QTreeWidgetItem(row)
        r, g, b = self.hex_to_rgb(color)
        r_copy, g_copy, b_copy = r, g, b
        text_color = 255, 255, 255
        if max(r, g, b) > 127:
            text_color = 0, 0, 0

        for i in range(row_len):
            item.setBackground(i, QtGui.QColor(r, g, b))
            item.setForeground(i, QtGui.QColor(*text_color))
        return item

    def show_sets(self):
        self.folders.clear()
        res = databaseTracks.get_all_tables()
        for row in res:
            self.folders.insertTopLevelItem(0, QTreeWidgetItem(row))

    def show_tracks(self):
        soundset = self.cur_list
        is_distinct = False
        if self.checkBox.isChecked():
            is_distinct = True
        self.sounds.clear()
        res = databaseTracks.get_tracks(soundset, is_distinct)
        self.sounds.setColumnCount(6)
        for i, row in enumerate(res):
            item = [str(len(res) - i)]
            color = row[2]
            if os.path.exists(row[1]):
                item.append(os.path.splitext(os.path.basename(row[1]))[0])
            else:
                text = f"{os.path.splitext(os.path.basename(row[1]))[0]} НЕ СУЩЕСТВУЕТ"
                item.append(text)
                return
            if music.is_correct(row[1]):
                try:
                    dur = int(music.get_duration(path=row[1]))
                    item.append(f"{int(dur // 60)}:{int(dur % 60):02}")
                except:
                    item.append("incorrect metadata")
            item.append(row[3])
            item.append(row[1])
            item.append(str(row[0]))
            self.sounds.insertTopLevelItem(0, self.getCurWidget(tuple(item), color))

    def add_sounds(self):
        if not self.cur_list:
            return
        fname = QFileDialog.getOpenFileNames(self, "Выбрать аудио", "", "Music files(*.mp3 *.wav *.ogg)")[0]
        if not fname:
            return
        databaseTracks.add_tracks(self.cur_list, fname)
        self.show_tracks()

    def add_set(self):
        self.nsDialog = newSetDialog()
        self.nsDialog.show()
        self.nsDialog.OkBtn.clicked.connect(self.add_nameSet)

    def add_nameSet(self):
        set_name = self.nsDialog.lineEdit.text()
        if set_name.count("'") or set_name.count('"') or set_name.count(" ") == len(set_name):
            self.nsDialog.label.setText("твы не прав")
        else:
            verdict = databaseTracks.add_table(f"{set_name}")
            if type(verdict) == bool:
                self.nsDialog.close()
                self.show_sets()
            else:
                self.nsDialog.label.setText(verdict)

    def tracks_click(self, item, column):
        if column != 3:
            self.play(item)
        else:
            pass

    def get_sounds_menu(self, point):
        sounds_menu = QtWidgets.QMenu()
        chosen_item = self.sounds.itemAt(point)
        if not chosen_item:
            return

        play = QtWidgets.QAction("Воспроизвести", sounds_menu)
        play.triggered.connect(lambda: self.play(chosen_item))
        sounds_menu.addAction(play)

        play_on_micro = QtWidgets.QAction("Воспроизвести на микрофоне", sounds_menu)
        play_on_micro.triggered.connect(lambda: self.play_on_micro(chosen_item))
        sounds_menu.addAction(play_on_micro)

        play_on_headphones = QtWidgets.QAction("Воспроизвести на гарнитуре", sounds_menu)
        play_on_headphones.triggered.connect(lambda: self.play_on_headphones(chosen_item))
        sounds_menu.addAction(play_on_headphones)

        sounds_menu.addSeparator()

        delete_audio = QtWidgets.QAction("Удалить аудио", sounds_menu)
        delete_audio.triggered.connect(lambda: self.delete_audio(chosen_item))
        sounds_menu.addAction(delete_audio)

        sounds_menu.addSeparator()

        choose_color = QtWidgets.QAction("Выбрать цвет", sounds_menu)
        choose_color.triggered.connect(lambda: self.choose_color(chosen_item))
        sounds_menu.addAction(choose_color)

        sounds_menu.exec(self.sounds.mapToGlobal(point))

    def get_folders_menu(self, point):
        folders_menu = QtWidgets.QMenu()
        chosen_item = self.folders.itemAt(point)
        if not chosen_item:
            return

        delete_table = QtWidgets.QAction("Удалить плейлист", folders_menu)
        delete_table.triggered.connect(lambda: self.delete_playlist(chosen_item.text(0), chosen_item))
        folders_menu.addAction(delete_table)

        folders_menu.exec(self.folders.mapToGlobal(point))

    def delete_playlist(self, table_name, item):
        if item.text(0) == self.cur_list:
            self.sounds.clear()
        databaseTracks.delete_table(table_name)
        self.show_sets()

    def delete_audio(self, item):
        databaseTracks.delete_audio(item.text(5))
        self.show_tracks()

    def choose_color(self, item):
        color = QtWidgets.QColorDialog.getColor()
        if not color.isValid():
            return
        databaseTracks.set_color(item.text(5), color.name().upper())
        self.show_tracks()

    def play(self, item):
        sound_path = item.text(4)
        media = QtCore.QUrl.fromLocalFile(sound_path)
        content = QtMultimedia.QMediaContent(media)
        self.player.setMedia(content)
        self.player.play()

    def mute_headphones(self):
        self.headphonesSlider.setValue(0)

    def export_list(self):
        if not self.cur_list:
            return
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", '/', '.csv')[0]
        with open(filename + '.csv', mode="w", encoding="utf-8", newline="") as f:
            csv_writer = csv.writer(f, delimiter=";")
            soundset = self.cur_list
            is_distinct = False
            if self.checkBox.isChecked():
                is_distinct = True
            self.sounds.clear()
            res = databaseTracks.get_tracks(soundset, is_distinct)
            csv_writer.writerows(res)

    def import_list(self):
        fname = QFileDialog.getOpenFileName(self, "Выбрать список", "", "CSV files(*.csv)")[0]
        if not fname:
            return
        with open(fname, encoding="utf-8", mode="r") as f:
            csv_reader = csv.reader(f, delimiter=";")
            name_without_extension = os.path.splitext(os.path.basename(fname))[0]
            if name_without_extension.count("'") or name_without_extension.count('"') or \
                    name_without_extension.count(" ") == len(name_without_extension):
                self.statusbar.showMessage("Некорректное имя")
            else:
                verdict = databaseTracks.add_table(f"{name_without_extension}")
                if type(verdict) == bool:
                    pass
                else:
                    self.statusbar.showMessage(verdict)
            data = [row for row in csv_reader]
            databaseTracks.add_rows(name_without_extension, data)
            self.show_sets()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Soundpad()
    ex.show()
    sys.exit(app.exec())
