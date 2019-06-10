import os
import pickle

from cryptography.fernet import Fernet
from Kthread import *
import pexpect
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

app = QApplication(sys.argv)


class MyStream(QObject):
    message = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyStream, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))

    def flush(self):
        pass


class MyWindow(QWidget):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'icon.png'))
        self.setWindowTitle("OPEN CONNECT")

        self.pushButton = QPushButton(self)
        self.pushButton.setText("Sent to tray")
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        MyWindow.closeEvent = self.closeEvent
        self.textEdit = QTextEdit(self)
        self.layoutVertical = QVBoxLayout(self)
        self.layoutVertical.addWidget(self.pushButton)
        self.layoutVertical.addWidget(self.textEdit)

    def closeEvent(self, event):
        print("event")
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            os._exit(1)
        else:
            event.ignore()

    @pyqtSlot()
    def on_pushButton_clicked(self):
        self.hide()

    @pyqtSlot(str)
    def on_myStream_message(self, message):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(message)


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        self.third = QLineEdit(self)
        self.fourth = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("username: ", self.first)
        layout.addRow("password: ", self.second)
        layout.addRow("address: ", self.third)
        layout.addRow("root Password", self.fourth)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return (self.first.text(), self.second.text(), self.third.text(), self.fourth.text())


class encryptData():
    def __init__(self, *args, **keywords):
        anyconnect_login_info = []
        for arg in args:
            anyconnect_login_info.extend(arg)
        keys = ['username', 'password', 'address', 'root_password', 'key']
        dictionary = dict(zip(keys, anyconnect_login_info))
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encyrpted = []
        cipher_username = cipher_suite.encrypt(bytes(dictionary.get('username'), encoding='utf8'))
        encyrpted.append(cipher_username.decode("utf-8"))
        cipher_password = cipher_suite.encrypt(bytes(dictionary.get('password'), encoding='utf8'))
        encyrpted.append(cipher_password.decode("utf-8"))
        cipher_address = cipher_suite.encrypt(bytes(dictionary.get('address'), encoding='utf8'))
        encyrpted.append(cipher_address.decode("utf-8"))
        cipher_rootpassword = cipher_suite.encrypt(bytes(dictionary.get('root_password'), encoding='utf8'))
        encyrpted.append(cipher_rootpassword.decode("utf-8"))
        encyrpted.append(key)
        self.encryptDictionary = dict(zip(keys, encyrpted))

    def getencryptedData(self):
        return (self.encryptDictionary)


class decryptData():
    def __init__(self, dictionary):
        key = bytes(dictionary.get('key'))
        cipher_suite = Fernet(key)
        deyrpted = []
        cipher_username = cipher_suite.decrypt(bytes(dictionary.get('username'), encoding='utf8'))
        deyrpted.append(cipher_username.decode("utf-8"))
        cipher_password = cipher_suite.decrypt(bytes(dictionary.get('password'), encoding='utf8'))
        deyrpted.append(cipher_password.decode("utf-8"))
        cipher_address = cipher_suite.decrypt(bytes(dictionary.get('address'), encoding='utf8'))
        deyrpted.append(cipher_address.decode("utf-8"))
        cipher_rootpassword = cipher_suite.decrypt(bytes(dictionary.get('root_password'), encoding='utf8'))
        deyrpted.append(cipher_rootpassword.decode("utf-8"))
        keys = ['username', 'password', 'address', 'root_password', 'key']
        self.decryptDictionary = dict(zip(keys, deyrpted))

    def getdecryptedData(self):
        return (self.decryptDictionary)


class pickleHandler():
    def save_obj(self, dictionary):
        f = open("file.pkl", "wb")
        pickle.dump(dictionary, f)
        f.close()

    def load_obj(self, name):
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)


def setConnectionValues():
    dialog = InputDialog()
    if dialog.exec():
        en = encryptData(dialog.getInputs())
        cn = pickleHandler().save_obj(en.getencryptedData())


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)
        settingAction = menu.addAction("Settings")
        LogAction = menu.addAction("Logs")
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(self.exitction)
        settingAction.triggered.connect(self.setValues)
        LogAction.triggered.connect(self.showLogWindow)

        self.setContextMenu(menu)

    def exitction(self):
        os._exit()

    def setValues(self):
        setConnectionValues()

    def showLogWindow(self):
        main.show()


def connection(address, rootPass, username, password, status):
    if status == False:
        child = pexpect.spawn('sudo /usr/sbin/openconnect  ' + 'disconnect')
        child.close(True)
        child.expect("disconnect")
        return
    child = pexpect.spawn('sudo /usr/sbin/openconnect  ' + address, maxread=2000)
    # child.logfile = sys.stdout.buffer

    child.delaybeforesend = 1
    child.sendline(rootPass)
    child.sendline('yes')
    child.sendline(username)
    print("user name sent")
    # child.logfile = None
    child.sendline(password)
    print("password sent")
    child.logfile = sys.stdout
    child.delaybeforesend = 1
    child.expect(pexpect.EOF, timeout=None)


if __name__ == '__main__':
    if not os.path.exists('file.pkl'):
        setConnectionValues()
    pkl = pickleHandler().load_obj("file")
    dData = decryptData(pkl).getdecryptedData()

    t2 = KThread(target=connection, args=(
        dData.get('address'), dData.get('root_password'), dData.get('username'), dData.get('password'), True))
    t2.start()

    main = MyWindow()

    myStream = MyStream()
    myStream.message.connect(main.on_myStream_message)
    sys.stdout = myStream
    w = QWidget()
    trayIcon = SystemTrayIcon(QIcon("icon.png"), w)
    trayIcon.show()

    main.setWindowFlags(main.windowFlags() | Qt.CustomizeWindowHint)
    main.setWindowFlags(main.windowFlags() & ~Qt.WindowMinimizeButtonHint)
    main.show()
    sys.exit(app.exec_())
