from Kthread import *
import pexpect
import base64
from uuid import getnode as get_mac
from argon2 import *
import pickle


def generate_key():
    password = str(get_mac()).encode()
    salt = "connector"
    password_hash = argon2_hash(password=password, salt=salt)
    return base64.urlsafe_b64encode(password_hash[:32])


class PrivateKeyHandler:
    @staticmethod
    def save_private_key():
        try:
            generated_key_from_mac = generate_key()
            private_key_dict = generated_key_from_mac
            PickleHandler.save_obj(private_key_dict, 'prvkey.pkl')
        except ImportError:
            return False

    @staticmethod
    def load_private_key():
        try:
            private_key = PickleHandler().load_obj('prvkey')
            return private_key

        except ImportError:
            return False


class PickleHandler:
    @staticmethod
    def save_obj(dictionary, filename):
        try:
            f = open(filename, "wb")
            pickle.dump(dictionary, f)
            f.close()
            return True
        except ImportError:
            return False

    @staticmethod
    def load_obj(name):
        try:
            with open(name + '.pkl', 'rb') as f:
                return pickle.load(f)
        except ImportError:
            print("load has some issues")


def connection(address, root_pass, username, password, status):
    if not status:
        child = pexpect.spawn('sudo /usr/sbin/openconnect  ' + 'disconnect')
        child.close(True)
        child.expect("disconnect")
        return
    child = pexpect.spawn('sudo /usr/sbin/openconnect  ' + address, maxread=2000)
    # child.logfile = sys.stdout.buffer

    child.delaybeforesend = 1
    child.sendline(root_pass)
    child.sendline('yes')
    child.sendline(username)
    print("user name sent")
    child.sendline(password)
    print("password sent")
    child.logfile = sys.stdout
    child.expect(pexpect.EOF, timeout=None)


def connect_vpn(d_data):
    try:
        t2 = KThread(target=connection, args=(
            d_data.get('address'), d_data.get('root_password'), d_data.get('username'), d_data.get('password'), True))
        t2.start()
    except ImportError:
        print("cannot create connection")
