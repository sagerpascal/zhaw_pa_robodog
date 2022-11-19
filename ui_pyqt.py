import os
import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QWidget
import subprocess  # For executing a shell command

ui_startwindow = 'ui/start_window.ui'
ui_control_window = 'ui/control_window.ui'


class StartScreen(QDialog):
    def __init__(self):
        super(StartScreen, self).__init__()
        loadUi(ui_startwindow, self)
        self.connectButton.clicked.connect(self.go_to_control)
        self.exitButton.clicked.connect(self.close_app)

    def go_to_control(self):
        if self.check_connection():
            control = ControlScreen()
            widget.addWidget(control)
            # ToDo: Implement connectivity check with robot. If it fails: Show label with error.
            widget.setCurrentWidget(control)
        else:
            self.errorLabel.setText("Connection failed. Please check if Wifi is connected.")

    def close_app(self):
        sys.exit()

    def check_connection(self):
        command = ['ping', '-c', '1', '192.168.123.12']
        return subprocess.call(command) == 0


class ControlScreen(QDialog):
    def __init__(self):
        super(ControlScreen, self).__init__()
        loadUi(ui_control_window, self)


os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
app = QApplication(sys.argv)
start = StartScreen()
widget = QStackedWidget()
widget.addWidget(start)
widget.setFixedHeight(419)
widget.setFixedWidth(698)
widget.show()

try:
    sys.exit(app.exec())
except:
    print("Exiting")
