import base64
import os
import pickle
# a lesani 2019
from tendo import singleton
from argon2 import *
from cryptography.fernet import Fernet
from Kthread import *
import pexpect
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from uuid import getnode as get_mac

app = QApplication(sys.argv)


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
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'icon.png'))
        self.setWindowTitle("OPEN CONNECT")

        self.pushButton = QPushButton(self)
        self.pushButton.setText("Settings")
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        MyWindow.closeEvent = self.closeEvent
        MyWindow.changeEvent = self.changeEvent

        self.textEdit = QTextEdit(self)
        self.layoutVertical = QVBoxLayout(self)
        self.layoutVertical.addWidget(self.pushButton)
        self.layoutVertical.addWidget(self.textEdit)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

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
    def on_pushButton_clicked(self):
        setConnectionValues(self)

    @pyqtSlot(str)
    def on_myStream_message(self, message):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(message)


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
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

    def setInputs(self, dData):
        self.first.setText(dData.get('username'))
        self.second.setText(dData.get('password'))
        self.third.setText(dData.get('address'))
        self.fourth.setText(dData.get('root_password'))


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

        cipherhw_suit = Fernet(generateKey())
        encryptedkey = cipherhw_suit.encrypt(key)
        encyrpted.append(encryptedkey)
        self.encryptDictionary = dict(zip(keys, encyrpted))

    def getencryptedData(self):
        return (self.encryptDictionary)


class decryptData():
    def __init__(self, dictionary):
        cipher_hwsuite = Fernet(generateKey())
        key = cipher_hwsuite.decrypt(bytes(dictionary.get('key')))
        # key = bytes(dictionary.get('key'))

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
        try:
            f = open("file.pkl", "wb")
            pickle.dump(dictionary, f)
            f.close()
            return True
        except:
            return False

    def load_obj(self, name):
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)


def loadAndDecryptPkl(fileName):
    try:
        pkl = pickleHandler().load_obj(fileName)
        dData = decryptData(pkl).getdecryptedData()
        return dData
    except:
        return None


def encryptAndSavePkl(data):
    try:
        en = encryptData(data)
        cn = pickleHandler().save_obj(en.getencryptedData())
        return True
    except:
        return False


def setConnectionValues(self):
    dialog = InputDialog()
    dData = loadAndDecryptPkl("file")
    if dData != None:
        dialog.setInputs(dData)
    if dialog.exec():
        if encryptAndSavePkl(dialog.getInputs()):
            connectVPN(loadAndDecryptPkl("file"))
        else:
            print("some error happened")


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.activated.connect(self.onTrayIconActivated)
        menu = QMenu(parent)
        settingAction = menu.addAction("Settings")
        LogAction = menu.addAction("Logs")
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(self.exitction)
        settingAction.triggered.connect(self.setValues)
        LogAction.triggered.connect(self.showLogWindow)
        self.setContextMenu(menu)

    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showLogWindow()

    def exitction(self):
        os._exit(0)

    def setValues(self):
        setConnectionValues(self)

    def showLogWindow(self):
        main.center()
        main.show()
        main.activateWindow()


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


def generateKey():
    password = str(get_mac()).encode()
    salt = "connector"
    password_hash = argon2_hash(password=password, salt=salt)
    return base64.urlsafe_b64encode(password_hash[:32])


def connectVPN(dData):
    print("connecting to :" + dData.get('address'))
    try:
        t2 = KThread(target=connection, args=(
            dData.get('address'), dData.get('root_password'), dData.get('username'), dData.get('password'), True))
        t2.start()
    except:
        print("cannot create connection")


if __name__ == '__main__':
    me = singleton.SingleInstance()
    main = MyWindow()
    main.center()
    if not os.path.exists('file.pkl'):
        setConnectionValues(main)
    else:
        try:
            dData = loadAndDecryptPkl("file")
            connectVPN(dData)
        except:
            QMessageBox.about(main, ":( !",
                              "There is a problem with ur file.pkl \n  if u are using a new network adapter \n please delete file.pkl")

    myStream = MyStream()
    myStream.message.connect(main.on_myStream_message)
    sys.stdout = myStream

    w = QWidget()
    trayIcon = SystemTrayIcon(QIcon("icon.png"), w)
    trayIcon.show()

    main.show()
    sys.exit(app.exec_())
