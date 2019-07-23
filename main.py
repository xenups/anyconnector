import os
# a lesani 2019
from tendo import singleton

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from protection import *


# from util import load_decrypt_pkl, encrypt_save_pkl, connect_vpn, sys


class MyStream(QObject):
    message = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyStream, self).__init__(parent)

    def write(self, message):
        if type(message) != str:
            message = message.decode("utf-8")
            self.message.emit(str(message))
        else:
            self.message.emit(str(message))

    def flush(self):
        pass


class MyWindow(QWidget):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(script_dir + os.path.sep + 'icon.png'))
        self.setWindowTitle("OPEN CONNECT")

        self.settingsPushButton = QPushButton(self)
        self.settingsPushButton.setText("Settings")
        self.settingsPushButton.clicked.connect(self.on_pushbutton_clicked)

        MyWindow.closeEvent = self.closeEvent
        MyWindow.changeEvent = self.changeEvent

        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.layoutVertical = QVBoxLayout(self)
        self.layoutVertical.addWidget(self.settingsPushButton)
        self.layoutVertical.addWidget(self.textEdit)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()
                dialog.hide()

    def center(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def closeEvent(self, event):
        print("shutdown app")
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            os._exit(0)
        else:
            event.ignore()

    @pyqtSlot()
    def on_pushbutton_clicked(self):
        set_connection_values(self)

    @pyqtSlot(str)
    def on_my_stream_message(self, message):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(message)


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.address = QLineEdit(self)
        self.root_pass = QLineEdit(self)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("username: ", self.username)
        layout.addRow("password: ", self.password)
        layout.addRow("address: ", self.address)
        layout.addRow("root Password", self.root_pass)
        self.root_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def get_inputs(self):
        return self.username.text(), self.password.text(), self.address.text(), self.root_pass.text()

    def set_inputs(self, d_data):
        if d_data:
            self.username.setText(d_data.get('username'))
            self.password.setText(d_data.get('password'))
            self.address.setText(d_data.get('address'))
            self.root_pass.setText(d_data.get('root_password'))
        else:
            return None


def set_connection_values(self, ):
    if not dialog.isVisible():
        dialog.show()
        if os.path.isfile("file.pkl"):
            d_data = load_decrypt_pkl("file")
            dialog.set_inputs(d_data)
        if dialog.exec():
            if encrypt_save_pkl(dialog.get_inputs()):
                connect_vpn(load_decrypt_pkl("file"))
            else:
                print("some error happened")


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.activated.connect(self.on_tray_icon_activated)
        menu = QMenu(parent)
        setting_action = menu.addAction("Settings")
        log_action = menu.addAction("Logs")
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_action)
        setting_action.triggered.connect(self.set_values)
        log_action.triggered.connect(self.show_log_window)
        self.setContextMenu(menu)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_log_window()

    @pyqtSlot()
    def exit_action(self):
        os._exit(0)

    @pyqtSlot()
    def set_values(self):
        self.show_log_window()
        set_connection_values(self)

    @pyqtSlot()
    def show_log_window(self):
        main.center()
        main.show()
        main.activateWindow()


def get_black_pallet():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.darkGreen)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)

    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    return palette


if __name__ == '__main__':
    me = singleton.SingleInstance()
    app = QApplication(sys.argv)
    dialog = InputDialog()
    main = MyWindow()
    main.center()

    if not os.path.isfile("file.pkl"):
        set_connection_values(main)
    else:
        try:
            d_data = load_decrypt_pkl("file")
            connect_vpn(d_data)
        except ImportError:
            QMessageBox.about(main, ":( !",
                              "There is a problem with ur file.pkl")

    myStream = MyStream()
    myStream.message.connect(main.on_my_stream_message)
    sys.stdout = myStream
    # app.setStyle('Fusion')
    # app.setPalette(getBlackPallet())

    w = QWidget()
    trayIcon = SystemTrayIcon(QIcon("icon.png"), w)
    trayIcon.show()

    main.show()
    sys.exit(app.exec_())
