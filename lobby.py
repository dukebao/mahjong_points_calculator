import json
import math
import os
import re
import sys
import time

from mutagen.mp3 import MP3
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
                             QLineEdit, QMainWindow, QMessageBox, QPushButton,
                             QSizePolicy, QSpacerItem, QWidget)
from PyQt5.uic import loadUi

STARTING_POINT = 40000

def submit(text, label, names, position):
    def update_names(position, text):
        names[str(position)] = text
        return names
    names = update_names(position, text.text())
    entered_text = text.text()
    print('You entered:', entered_text)
    print('Name list:', names)
    label.setText(entered_text)
    text.setText('')
    write_to_json(names)


def write_to_json(names):
    with open('players.json', 'w') as f:
        f.write(json.dumps(names))

def calculate_point_ron_oya(winner, pon):
    return 1.5*calculate_point_ron_ko(winner, pon)

def calculate_point_ron_ko(winner, pon):
    """
        Calculate the point for ron when the player is the ko position
    """
    pon = int(pon)
    if pon == 0:
        return 0
    if pon <= 3:
        print(f'{pon}飜')
        return 1000*2**(pon-1)
    elif pon == 4 or pon == 5:
        print('滿貫')
        return 8000
    elif pon == 6 or pon == 7:
        print('跳滿')
        return 12000
    elif pon >= 8 and pon <= 10:
        print('倍滿')
        return 16000
    elif pon >= 11 and pon <= 12:
        print('三倍滿')
        return 24000
    elif pon >= 13:
        print('役滿')
        return 32000

def play_ron_audio(winner , pon):
    if pon == 4 or pon == 5:
        play_audio(winner, 'game end - mangan')
    elif pon == 6 or pon == 7:
        play_audio(winner, 'game end - haneman')
    elif pon >= 8 and pon <= 10:
        play_audio(winner, 'game end - baiman')
    elif pon >= 11 and pon <= 12:
        play_audio(winner, 'game end - sanbaiman')
    elif pon >= 13:
        play_audio(winner, 'game end - yakuman')

def get_character_voice(winner):
    if winner.lower() == 'bao':
        return 'Yumeko Jabami'
    elif winner.lower() == 'kc':
        return 'C.C'
    elif winner.lower() == 'l3ldon':
        return 'Miki Nikaidou'
    elif winner.lower() == 'emma':
        return 'Xenia'
    else:
        return 'Ichihime'

def get_riichi_music(winner):
    if winner.lower() == 'bao':
        return 'liqi_23chunjie'
    elif winner.lower() == 'kc':
        return 'liqi1'
    elif winner.lower() == 'l3ldon':
        return 'liqi_8bit'
    elif winner.lower() == 'emma':
        return 'liqi_chuzhen'
    else:
        return 'liqi2'

def play_audio(winner, audio):
    CharacterVoice = get_character_voice(winner)
    audio_path = os.path.join(os.getcwd(), CharacterVoice, audio + '.mp3')
    #check duration of audio
    audio_duration = MP3(audio_path).info.length
    player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
    player.play()
    time.sleep(math.ceil(audio_duration))

def play_riichi_audio(winner):
    playlist.clear()
    CharacterVoice = get_character_voice(winner)
    playlist.addMedia(QMediaContent(QUrl.fromLocalFile(os.path.join(os.getcwd(),
                                                                    CharacterVoice, 'action - riichi.mp3'))))
    riichiMusic = get_riichi_music(winner)
    playlist.addMedia(QMediaContent(QUrl.fromLocalFile(os.path.join(os.getcwd(), 'music', riichiMusic + '.mp3'))))
    player.setPlaylist(playlist)
    player.play()

def ron(winner:str):
    play_audio(winner, 'action - ron')
    def calculate_round_fee(round_count, is_tsumo):
        round_fee_base = 300
        if is_tsumo:
            round_fee = (round_fee_base/3 + 100) * round_count
            return round_fee
        else:
            round_fee = round_count * round_fee_base
            return round_fee
    def calculate_richi_points():
        richi_point = 0
        if window.north_richi.isChecked():
            richi_point += 1000
        if window.east_richi.isChecked():
            richi_point += 1000
        if window.south_richi.isChecked():
            richi_point += 1000
        if window.west_richi.isChecked():
            richi_point += 1000
        return richi_point
    def get_pon(pon):
        return re.search(r'(\d+)', pon).group(1)
    def get_round_count():
        return re.search(r'(\d+)', window.round_count.text()).group(1)
    richi_points = calculate_richi_points()
    namelist = json.loads(open('players.json').read())
    is_tsumo = False
    pon = get_pon(window.pon.text())
    round_count = int(get_round_count())
    try:
        pon = int(pon)
    except:
        pon = 0
    msg = QMessageBox()
    msg.setWindowTitle("Ron")
    msg.setText("Choose the ron type")
    msg.setIcon(QMessageBox.Question)
    oya = current_oya(window)
    if winner == namelist['north']:
        west = QPushButton(namelist['west'])  # change to player name
        east = QPushButton(namelist['east'])
        south = QPushButton(namelist['south'])
        tsumo = QPushButton('Tsumo')
        msg.addButton(west, QMessageBox.YesRole)
        msg.addButton(east, QMessageBox.YesRole)
        msg.addButton(south, QMessageBox.YesRole)
        msg.addButton(tsumo, QMessageBox.YesRole)
        button_clicked = msg.exec_()
        if oya == winner:
            hand_worth = calculate_point_ron_oya(winner, pon)
        else:
            hand_worth = calculate_point_ron_ko(winner, pon)
        # find out which button is clicked
        if msg.clickedButton() == west:
            if namelist['west'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_west_point.display(int(window.player_west_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == east:
            if namelist['east'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_east_point.display(int(window.player_east_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == south:
            if namelist['south'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_south_point.display(int(window.player_south_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == tsumo:
            play_audio(winner, 'action - tsumo')
            is_tsumo = True
            if namelist['north'] == oya:
                for player in [window.player_west_point, window.player_east_point, window.player_south_point]:
                    player.display(int(player.value()) - hand_worth/3 - calculate_round_fee(round_count, is_tsumo))
            else:
                for player in [window.player_west_point, window.player_east_point, window.player_south_point]:
                    player.display(int(player.value()) - hand_worth/4 - calculate_round_fee(round_count, is_tsumo))
                if namelist['west'] == oya:
                    window.player_west_point.display(int(window.player_west_point.value()) - hand_worth/4)
                elif namelist['east'] == oya:
                    window.player_east_point.display(int(window.player_east_point.value()) - hand_worth/4)
                elif namelist['south'] == oya:
                    window.player_south_point.display(int(window.player_south_point.value()) - hand_worth/4)
        if is_tsumo:
            player_north_point = int(window.player_north_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) * 3 + richi_points
        else:
            player_north_point = int(window.player_north_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) + richi_points

        window.player_north_point.display(player_north_point)
    elif winner == namelist['west']:
        east = QPushButton(namelist['east'])  # change to player name
        north = QPushButton(namelist['north'])
        south = QPushButton(namelist['south'])
        tsumo = QPushButton('Tsumo')
        msg.addButton(east, QMessageBox.YesRole)
        msg.addButton(north, QMessageBox.YesRole)
        msg.addButton(south, QMessageBox.YesRole)
        msg.addButton(tsumo, QMessageBox.YesRole)
        button_clicked = msg.exec_()
        if oya == winner:
            hand_worth = calculate_point_ron_oya(winner, pon)
        else:
            hand_worth = calculate_point_ron_ko(winner, pon)
        if msg.clickedButton() == east:
            if namelist['east'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_east_point.display(int(window.player_east_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == north:
            if namelist['north'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_north_point.display(int(window.player_north_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == south:
            if namelist['south'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_south_point.display(int(window.player_south_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == tsumo:
            play_audio(winner, 'action - tsumo')
            time.sleep(2)
            is_tsumo = True
            if namelist['west'] == oya:
                for player in [window.player_east_point, window.player_north_point, window.player_south_point]:
                    player.display(int(player.value()) - hand_worth/3 - calculate_round_fee(round_count, is_tsumo))
            else:
                for player in [window.player_east_point, window.player_north_point, window.player_south_point]:
                    player.display(int(player.value()) - hand_worth/4 - calculate_round_fee(round_count, is_tsumo))
                if namelist['east'] == oya:
                    window.player_east_point.display(int(window.player_east_point.value()) - hand_worth/4)
                elif namelist['north'] == oya:
                    window.player_north_point.display(int(window.player_north_point.value()) - hand_worth/4)
                elif namelist['south'] == oya:
                    window.player_south_point.display(int(window.player_south_point.value()) - hand_worth/4)
        if is_tsumo:
            player_west_point = int(window.player_west_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) * 3 + richi_points
        else:
            player_west_point = int(window.player_west_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) + richi_points
        window.player_west_point.display(player_west_point)
    elif winner == namelist['east']:
        west = QPushButton(namelist['west'])
        north = QPushButton(namelist['north'])
        south = QPushButton(namelist['south'])
        tsumo = QPushButton('Tsumo')
        msg.addButton(west, QMessageBox.YesRole)
        msg.addButton(north, QMessageBox.YesRole)
        msg.addButton(south, QMessageBox.YesRole)
        msg.addButton(tsumo, QMessageBox.YesRole)
        button_clicked = msg.exec_()
        if oya == winner:
            hand_worth = calculate_point_ron_oya(winner, pon)
        else:
            hand_worth = calculate_point_ron_ko(winner, pon)
        if msg.clickedButton() == west:
            if namelist['west'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_west_point.display(int(window.player_west_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == north:
            if namelist['north'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_north_point.display(int(window.player_north_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == south:
            if namelist['south'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_south_point.display(int(window.player_south_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == tsumo:
            play_audio(winner, 'action - tsumo')
            time.sleep(2)
            is_tsumo = True
            if namelist['east'] == oya:
                for player in [window.player_west_point, window.player_north_point, window.player_south_point]:
                    player.display(int(player.value()) - hand_worth/3 - calculate_round_fee(round_count, is_tsumo))
            else:
                for player in [window.player_west_point, window.player_north_point, window.player_south_point]:
                    player.display(int(player.value()) - hand_worth/4 - calculate_round_fee(round_count, is_tsumo))
                if namelist['west'] == oya:
                    window.player_west_point.display(int(window.player_west_point.value()) - hand_worth/4)
                elif namelist['north'] == oya:
                    window.player_north_point.display(int(window.player_north_point.value()) - hand_worth/4)
                elif namelist['south'] == oya:
                    window.player_south_point.display(int(window.player_south_point.value()) - hand_worth/4)
        if is_tsumo:
            player_east_point = int(window.player_east_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) * 3 + richi_points
        else:
            player_east_point = int(window.player_east_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) + richi_points
        window.player_east_point.display(player_east_point)
    elif winner == namelist['south']:
        print('winner is south')
        west = QPushButton(namelist['west'])
        east = QPushButton(namelist['east'])
        north = QPushButton(namelist['north'])
        tsumo = QPushButton('Tsumo')
        msg.addButton(west, QMessageBox.YesRole)
        msg.addButton(east, QMessageBox.YesRole)
        msg.addButton(north, QMessageBox.YesRole)
        msg.addButton(tsumo, QMessageBox.YesRole)
        button_clicked = msg.exec_()
        if oya == winner:
            hand_worth = calculate_point_ron_oya(winner, pon)
        else:
            hand_worth = calculate_point_ron_ko(winner, pon)
        if msg.clickedButton() == west:
            if namelist['west'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_west_point.display(int(window.player_west_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == east:
            if namelist['east'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_east_point.display(int(window.player_east_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == north:
            if namelist['north'] == oya:
                hand_worth = calculate_point_ron_oya(winner, pon)
            window.player_north_point.display(int(window.player_north_point.value()) - hand_worth - calculate_round_fee(round_count, is_tsumo))
        elif msg.clickedButton() == tsumo:
            play_audio(winner, 'action - tsumo')

            is_tsumo = True
            if namelist['south'] == oya:
                for player in [window.player_west_point, window.player_east_point, window.player_north_point]:
                    player.display(int(player.value()) - hand_worth/3 - calculate_round_fee(round_count, is_tsumo))
            else:
                for player in [window.player_west_point, window.player_east_point, window.player_north_point]:
                    player.display(int(player.value()) - hand_worth/4 - calculate_round_fee(round_count, is_tsumo))
                if namelist['west'] == oya:
                    window.player_west_point.display(int(window.player_west_point.value()) - hand_worth/4)
                elif namelist['east'] == oya:
                    window.player_east_point.display(int(window.player_east_point.value()) - hand_worth/4)
                elif namelist['north'] == oya:
                    window.player_north_point.display(int(window.player_north_point.value()) - hand_worth/4)
        if is_tsumo:
            player_south_point = int(window.player_south_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) * 3 + richi_points
        else:
            player_south_point = int(window.player_south_point.value()) + hand_worth + calculate_round_fee(round_count, is_tsumo) + richi_points
        window.player_south_point.display(player_south_point)
    else:
        print('error')

    window.north_richi.setChecked(False)
    window.south_richi.setChecked(False)
    window.east_richi.setChecked(False)
    window.west_richi.setChecked(False)
    play_ron_audio(winner, pon)
    window.pon.setValue(0)

def richi(player):
    play_riichi_audio(player)
    if player == namelist['north'] and window.north_richi.isChecked():
        window.player_north_point.display(int(window.player_north_point.value()) - 1000)
    elif player == namelist['west'] and window.west_richi.isChecked():
        window.player_west_point.display(int(window.player_west_point.value()) - 1000)
    elif player == namelist['east'] and window.east_richi.isChecked():
        window.player_east_point.display(int(window.player_east_point.value()) - 1000)
    elif player == namelist['south'] and window.south_richi.isChecked():
        window.player_south_point.display(int(window.player_south_point.value()) - 1000)

def init_player_pos(window, namelist):
    window.northPB.clicked.connect(lambda: ron(namelist['north']))
    window.player_north.setText(namelist['north'])
    window.north_richi.clicked.connect(lambda: richi(namelist['north']))

    window.westPB.clicked.connect(lambda: ron(namelist['west']))
    window.player_west.setText(namelist['west'])
    window.west_richi.clicked.connect(lambda: richi(namelist['west']))

    window.eastPB.clicked.connect(lambda: ron(namelist['east']))
    window.player_east.setText(namelist['east'])
    window.east_richi.clicked.connect(lambda: richi(namelist['east']))

    window.southPB.clicked.connect(lambda: ron(namelist['south']))
    window.player_south.setText(namelist['south'])
    window.south_richi.clicked.connect(lambda: richi(namelist['south']))

    set_player_points(window)
def set_player_points(window):

    window.player_south_point.display(STARTING_POINT)
    window.player_east_point.display(STARTING_POINT)
    window.player_west_point.display(STARTING_POINT)
    window.player_north_point.display(STARTING_POINT)

def init_player_list(window, namelist):
    name_strings = [namelist[key] for key in namelist.keys()]

    combo_box = window.findChild(QComboBox, 'current_oya')
    combo_box.addItems(name_strings)

    # print('currently the displayed name is:', window.current_oya.currentText())

def current_oya(window):
    return window.current_oya.currentText()

def reset(window, namelist):
    init_player_pos(window, namelist)

app = QApplication([])
window = loadUi('main.ui')
namelist = json.loads(open('players.json').read())
init_player_pos(window, namelist)  # initialize player position
init_player_list(window, namelist)  # initialize player list
window.reset.clicked.connect(lambda: set_player_points(window))

main_window = QMainWindow()
main_window.setCentralWidget(window)
main_window.setGeometry(100, 100, 900, 900)

player = QMediaPlayer()
playlist = QMediaPlaylist()

main_window.show()

app.exec_()
