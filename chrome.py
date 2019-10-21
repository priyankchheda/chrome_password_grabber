""" Get unencrypted 'Saved Password' from Google Chrome
    Supported platform: Mac, Linux and Windows
"""

import json
import platform
import sqlite3
import string
import subprocess
import os
from getpass import getuser
from importlib import import_module
from os import unlink
from shutil import copy

__author__ = 'Priyank Chheda'
__email__ = 'p.chheda29@gmail.com'


class ChromeMac:
    """ Decryption class for chrome mac installation """
    def __init__(self):
        """ Mac Initialization Function """
        my_pass = subprocess.Popen(
            "security find-generic-password -wa 'Chrome'",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        stdout, _ = my_pass.communicate()
        my_pass = stdout.replace(b'\n', b'')

        iterations = 1003
        salt = b'saltysalt'
        length = 16

        kdf = import_module('Crypto.Protocol.KDF')
        self.key = kdf.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = (f"/Users/{getuser()}/Library/Application Support/"
                       "Google/Chrome/Default/")

    def decrypt_func(self, enc_passwd):
        """ Mac Decryption Function """
        aes = import_module('Crypto.Cipher.AES')
        initialization_vector = b' ' * 16
        enc_passwd = enc_passwd[3:]
        cipher = aes.new(self.key, aes.MODE_CBC, IV=initialization_vector)
        decrypted = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode('utf8')


class ChromeWin:
    """ Decryption class for chrome windows installation """
    def __init__(self):
        """ Windows Initialization Function """
        # search the genral chrome version path
        win_path = f"C:\\Users\\{getuser()}\\AppData\\Local\\Google" "\\{chrome}\\User Data\\Default\\"
        win_chrome_ver = [
            item for item in
            ['chrome', 'chrome dev', 'chrome beta', 'chrome canary']
            if os.path.exists(win_path.format(chrome=item))
        ]
        self.dbpath = win_path.format(chrome=''.join(win_chrome_ver))
        # self.dbpath = (f"C:\\Users\\{getuser()}\\AppData\\Local\\Google"
        #                "\\Chrome\\User Data\\Default\\")

    def decrypt_func(self, enc_passwd):
        """ Windows Decryption Function """
        win32crypt = import_module('win32crypt')
        data = win32crypt.CryptUnprotectData(enc_passwd, None, None, None, 0)
        return data[1].decode('utf8')


class ChromeLinux:
    """ Decryption class for chrome linux installation """
    def __init__(self):
        """ Linux Initialization Function """
        my_pass = 'peanuts'.encode('utf8')
        iterations = 1
        salt = b'saltysalt'
        length = 16

        kdf = import_module('Crypto.Protocol.KDF')
        self.key = kdf.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = f"/home/{getuser()}/.config/google-chrome/Default/"

    def decrypt_func(self, enc_passwd):
        """ Linux Decryption Function """
        aes = import_module('Crypto.Cipher.AES')
        initialization_vector = b' ' * 16
        enc_passwd = enc_passwd[3:]
        cipher = aes.new(self.key, aes.MODE_CBC, IV=initialization_vector)
        decrypted = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode('utf8')


class Chrome:
    """ Generic OS independent Chrome class """
    def __init__(self):
        """ determine which platform you are on """
        target_os = platform.system()
        if target_os == 'Darwin':
            self.chrome_os = ChromeMac()
        elif target_os == 'Windows':
            self.chrome_os = ChromeWin()
        elif target_os == 'Linux':
            self.chrome_os = ChromeLinux()

    @property
    def get_login_db(self):
        """ getting "Login Data" sqlite database path """
        return self.chrome_os.dbpath

    def get_password(self, prettyprint=False):
        """ get URL, username and password in clear text
            :param prettyprint: if true, print clear text password to screen
            :return: clear text data in dictionary format
        """
        copy(self.chrome_os.dbpath + "Login Data", "Login Data.db")
        conn = sqlite3.connect("Login Data.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action_url, username_value, password_value
            FROM logins; """)
        data = {'data': []}
        for result in cursor.fetchall():
            _passwd = self.chrome_os.decrypt_func(result[2])
            passwd = ''.join(i for i in _passwd if i in string.printable)
            if result[1] or passwd:
                _data = {}
                _data['url'] = result[0]
                _data['username'] = result[1]
                _data['password'] = passwd
                data['data'].append(_data)
        conn.close()
        unlink("Login Data.db")

        if prettyprint:
            print(json.dumps(data, indent=4))
        return data


def main():
    """ Operational Script """
    chrome_pwd = Chrome()
    print(chrome_pwd.get_login_db)
    chrome_pwd.get_password(prettyprint=True)


if __name__ == '__main__':
    main()
