import os
import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QWidget
from auxillary_funcs.ssh_access import check_connection
from gestrec import Gestrec
from auxillary_funcs.interprocess_comms import get_conn_client, MSG_GESTREC_OFF, MSG_GESTREC_ON, DEFAULTPORT

from time import sleep

ui_startwindow = 'ui/start_window.ui'
ui_control_window = 'ui/control_window.ui'


class StartScreen(QDialog):
    def __init__(self):
        super(StartScreen, self).__init__()
        loadUi(ui_startwindow, self)
        self.connectButton.clicked.connect(self.go_to_control)
        self.exitButton.clicked.connect(self.close_app)

    def go_to_control(self):
        if check_connection():
            control = ControlScreen()
            widget.addWidget(control)
            # ToDo: Implement connectivity check with robot. If it fails: Show label with error.
            widget.setCurrentWidget(control)
        else:
            self.errorLabel.setText("Connection failed. Please check if Wifi is connected.")

    def close_app(self):
        sys.exit()


class ControlScreen(QDialog):
    def __init__(self):
        super(ControlScreen, self).__init__()
        loadUi(ui_control_window, self)
        self.activateButton.clicked.connect(self.start_recognition)
        self.stopButton.clicked.connect(self.stop_recognition)
        self.exitButton.clicked.connect(self.close_app)
        self.gestrec = Gestrec()
        self.gestrec.start()

    def start_recognition(self):
        self.gestrec.gestrec_on()
        self.recognitionLabel.setText("Gesture Recognition: on ")

    def stop_recognition(self):
        self.gestrec.gestrec_off()
        self.recognitionLabel.setText("Gesture Recognition: off")

    def close_app(self):
        self.gestrec.stop()
        sys.exit()


def start_ui():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    # start = StartScreen()
    start = ControlScreen()
    widget = QStackedWidget()
    widget.addWidget(start)
    widget.setFixedHeight(419)
    widget.setFixedWidth(698)
    widget.show()

    try:
        sys.exit(app.exec())
    except:
        print("Exiting")


if __name__ == '__main__':
    start_ui()