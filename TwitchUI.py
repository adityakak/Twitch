import os
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import Twitch_Farmer


class Window(QWidget):
    def __init__(self):
        super().__init__()

        def stop_watching():
            print("Stopped Watching")
            start_button.setDisabled(False)
            username_box.setDisabled(False)
            password_box.setDisabled(False)
            prev_profiles.setDisabled(False)
            niceness_levels.setDisabled(False)
            open_profile_button.setDisabled(False)
            save_profile_button.setDisabled(False)

            stop_button.setDisabled(True)
            Twitch_Farmer.stop()

        def start_watching():
            print("Started Watching")
            start_button.setDisabled(True)
            username_box.setDisabled(True)
            password_box.setDisabled(True)
            prev_profiles.setDisabled(True)
            niceness_levels.setDisabled(True)
            open_profile_button.setDisabled(True)
            save_profile_button.setDisabled(True)

            stop_button.setDisabled(False)

            username = username_box.text().strip()
            password = password_box.text().strip()
            if username != "" and password != "":
                Twitch_Farmer.watch_twitch([os.name, app.primaryScreen().size(), niceness_levels.currentText(), username, password])

        def close_program():
            print("Closing")
            self.close()

        def save_profile():
            username = username_box.text().strip()
            password = password_box.text().strip()
            if username != "" and password != "":
                pickle.dump([username, password, str(niceness_levels.currentText())],
                            open('twitch_user' + username + '.pkl', 'wb'))
                current_options = {prev_profiles.itemText(i) for i in range(prev_profiles.count())}
                if username not in current_options:
                    prev_profiles.addItem(username)
                prev_profiles.setCurrentText("--Profiles--")

        def open_profile():
            username = prev_profiles.currentText()
            if username != 'None' and username != '--Profiles--':
                data = pickle.load(open('twitch_user' + username + '.pkl', 'rb'))
                username_box.setText(data[0])
                password_box.setText(data[1])
                niceness_levels.setCurrentText(data[2])

        flags = Qt.WindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(flags)

        # Button Creation
        start_button = QPushButton('Start Watching')
        start_button.clicked.connect(start_watching)
        start_button.setStyleSheet("background-color : green")
        start_button.adjustSize()

        stop_button = QPushButton('Stop Watching')
        stop_button.clicked.connect(stop_watching)
        stop_button.setStyleSheet("background-color : red")
        stop_button.setDisabled(True)

        close_button = QPushButton('Close Program')
        close_button.clicked.connect(close_program)

        save_profile_button = QPushButton('Save Profile')
        save_profile_button.setStyleSheet("background-color : blue")
        save_profile_button.clicked.connect(save_profile)

        open_profile_button = QPushButton('Open Profile')
        open_profile_button.setStyleSheet("background-color : green")
        open_profile_button.clicked.connect(open_profile)

        grid = QGridLayout()

        # First Row
        username_label = QLabel("Twitch Username:")
        grid.addWidget(username_label, *(0, 0))

        username_box = QLineEdit()
        grid.addWidget(username_box, *(0, 1))

        saved_profs_label = QLabel("Saved Profiles:")
        grid.addWidget(saved_profs_label, *(0, 2))

        grid.addWidget(open_profile_button, *(0, 4))

        # Second Row
        password_label = QLabel("Twitch Password:")
        grid.addWidget(password_label, *(1, 0))

        password_box = QLineEdit()
        grid.addWidget(password_box, *(1, 1))

        process_priority_label = QLabel("Process Priority:")
        grid.addWidget(process_priority_label, *(1, 2))

        niceness_levels = QComboBox()
        niceness_levels.addItem('Below Normal (Recommended)')
        niceness_levels.addItem('Normal')
        niceness_levels.addItem('Above Normal')
        niceness_levels.addItem('High')
        grid.addWidget(niceness_levels, *(1, 3))

        grid.addWidget(save_profile_button, *(1, 4))

        # Third Row
        grid.addWidget(start_button, *(2, 0))
        grid.addWidget(stop_button, *(2, 2))
        grid.addWidget(close_button, *(2, 4))

        prev_profiles = QComboBox()
        prev_files = [f for f in os.listdir() if f.startswith('twitch_user')]
        if len(prev_files) != 0:
            prev_profiles.addItem("--Profiles--")
            for profile in prev_files:
                prev_profiles.addItem(profile[len("twitch_user"):-len(".pkl")])
        else:
            prev_profiles.addItem("None")
        grid.addWidget(prev_profiles, *(0, 3))

        self.setLayout(grid)
        self.setGeometry(500, 500, 600, 200)
        self.setWindowTitle("Twitch Farmer")

        # Move Window to Center
        center_rectangle = self.frameGeometry()
        center_loc = QDesktopWidget().availableGeometry().center()
        center_rectangle.moveCenter(center_loc)
        self.move(center_rectangle.topLeft())

        self.show()


app = QApplication([])
app.setStyle('Fusion')
window = Window()
sys.exit(app.exec_())
