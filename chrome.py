""" Get unencrypted 'Saved Password' from Google Chrome
    Supported platform: Mac, Linux and Windows
"""
import json
import os
import os.path
import platform
import sqlite3
import string
import subprocess
from getpass import getuser
from importlib import import_module
from os import unlink,rename
from shutil import copy

import secretstorage

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
        try:
            decrypted = cipher.decrypt(enc_passwd)
            return decrypted.strip().decode('utf8')
        except BaseException as err:
            if reraise:
                raise
            return("FAILED DECODE: "+str(err))

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
        try:
           data = win32crypt.CryptUnprotectData(enc_passwd, None, None, None, 0)
           return data[1].decode('utf8')
        except BaseException as err:
            if reraise:
                raise
            return("FAILED DECODE: "+str(err))



class ChromeLinux:
    """ Decryption class for chrome linux installation """
    def __init__(self):
        """ Linux Initialization Function """
        my_pass = 'peanuts'.encode('utf8')
        bus = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(bus)
        for item in collection.get_all_items():
            if item.get_label() == 'Chrome Safe Storage':
                my_pass = item.get_secret()
                break
        iterations = 1
        salt = b'saltysalt'
        length = 16

        kdf = import_module('Crypto.Protocol.KDF')
        self.key = kdf.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = f"/home/{getuser()}/.config/google-chrome/Default/"

    def decrypt_func(self, enc_passwd, reraise = False):
        """ Linux Decryption Function """
        aes = import_module('Crypto.Cipher.AES')
        initialization_vector = b' ' * 16
        enc_passwd = enc_passwd[3:]
        cipher = aes.new(self.key, aes.MODE_CBC, IV=initialization_vector)
        decrypted = cipher.decrypt(enc_passwd)
        try:
            return decrypted.strip().decode('utf8')
        except BaseException as err:
            if reraise:
                raise
            return("FAILED DECODE: "+str(err))


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
            print(result[2])
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
            return json.dumps(data, indent=4)
        return data

    def rewrite_passwords(self):
        """ Write a new Login Data file in the current directory without garbled lines
        """

        # failsafe
        if os.path.exists("Login Data"):
            print ("Login Data exists. If you are running inside Chrome config directory, DON'T. Otherwise delete the file and rerun")
            return

        copy(self.chrome_os.dbpath + "Login Data", "Login Data Copy.db")
        conn = sqlite3.connect("Login Data Copy.db")
        new_conn = sqlite3.connect("Login Data.db")
        new_cursor = new_conn.cursor()

        password_param_index = -1

        for line in conn.iterdump():
            exec = True

            #print(line)

            if (line.find("CREATE TABLE logins") >= 0):
                # determine the index of the password
                password_param_index = 0
                mangle_line = line

                while (mangle_line.find(',')>=0) and (mangle_line.find(',')<mangle_line.find("password_value")):
                    password_param_index += 1
                    mangle_line = mangle_line[mangle_line.find(',')+1:]


            if (line.find('INSERT INTO "logins"') >= 0) and (password_param_index >= 0):
                # this line adds a line into logins, find the password, try to decrypt it
                mangle_line = line

                # remove all until the ( inclusive
                mangle_line = mangle_line[mangle_line.find('(')+1:]

                # process character by character
                # when a comma is encountered outside a '' delineated string, increase current_index
                # stop when the password_param_index is reached or the line is empty
                current_index = 0
                in_string = False
                while current_index < password_param_index:
                    # failsafe
                    if len(mangle_line) == 0:
                        break

                    # process double '' inside a string for escaping, special case
                    if in_string and (mangle_line[0:2] == "''"):
                        mangle_line = mangle_line[2:]
                        continue

                    # process a comma
                    if (not in_string) and (mangle_line[0] == ','):
                        current_index += 1

                    # process a single quote to enter or exit a string
                    if mangle_line[0] == "'":
                        in_string = not in_string

                    mangle_line = mangle_line[1:]

                if (len(mangle_line) == 0) or (mangle_line.find(',')<mangle_line.find("'")):
                    print("Password value not found: "+line)
                else:
                    # retrieve password value
                    mangle_line = mangle_line[mangle_line.find("'")+1:]
                    mangle_line = mangle_line[:mangle_line.find("'")]
                    password_value = bytes.fromhex(mangle_line)
                    try:
                        _passwd = self.chrome_os.decrypt_func(password_value, reraise = True)
                    except BaseException:
                        print("Failed and excluded: "+line)
                        exec = False

            if exec:
                new_cursor.execute(line)
            else:
                print("Line skipped")


        conn.close()
        new_conn.close()
        unlink("Login Data Copy.db")
        rename("Login Data.db","Login Data")
        print("New Login Data ready, use at your own risk")




def main():
    """ Operational Script """
    chrome_pwd = Chrome()
    print(chrome_pwd.get_login_db)
    chrome_pwd.get_password(prettyprint=True)


if __name__ == '__main__':
    main()
