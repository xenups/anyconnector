from cryptography.fernet import Fernet
from util import *


class EncryptData:
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

        c = PrivateKeyHandler()
        c.save_private_key()

        if not os.path.isfile("prvkey.pkl"):
            PrivateKeyHandler.save_private_key()
        generated_key = PrivateKeyHandler().load_private_key()
        cipher_hw_suit = Fernet(generated_key)
        encrypted_key = cipher_hw_suit.encrypt(key)
        encyrpted.append(encrypted_key)
        self.encryptDictionary = dict(zip(keys, encyrpted))

    @property
    def get_encrypted_data(self):
        return self.encryptDictionary


class DecryptData:

    def __init__(self, dictionary):
        try:
            if not os.path.isfile("prvkey.pkl"):
                PrivateKeyHandler.save_private_key()
            generated_key = PrivateKeyHandler().load_private_key()
            cipher_hw_suite = Fernet(generated_key)
            key = cipher_hw_suite.decrypt(bytes(dictionary.get('key')))
            cipher_suite = Fernet(key)
            decrypted = []
            cipher_username = cipher_suite.decrypt(bytes(dictionary.get('username'), encoding='utf8'))
            decrypted.append(cipher_username.decode("utf-8"))
            cipher_password = cipher_suite.decrypt(bytes(dictionary.get('password'), encoding='utf8'))
            decrypted.append(cipher_password.decode("utf-8"))
            cipher_address = cipher_suite.decrypt(bytes(dictionary.get('address'), encoding='utf8'))
            decrypted.append(cipher_address.decode("utf-8"))
            cipher_root_password = cipher_suite.decrypt(bytes(dictionary.get('root_password'), encoding='utf8'))
            decrypted.append(cipher_root_password.decode("utf-8"))
            keys = ['username', 'password', 'address', 'root_password', 'key']
            self.decrypt_dictionary = dict(zip(keys, decrypted))
        except ImportError:
            self.decrypt_dictionary = []
            print("decryption failed")

    def get_decrypted_data(self):
        return self.decrypt_dictionary


def load_decrypt_pkl(file_name):
    pkl = PickleHandler().load_obj(file_name)
    if pkl is not None:
        return DecryptData(pkl).get_decrypted_data()
    else:
        return False


def encrypt_save_pkl(data):
    try:
        en = EncryptData(data)
        cn = PickleHandler().save_obj(en.get_encrypted_data, 'file.pkl')
        return True
    except ImportError:
        return False


def save_generated_private_key():
    pass
