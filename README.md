# Chrome-Password-Grabber
Get unencrypted 'Saved Password' from Google Chrome

## Introduction
Like other browsers Chrome also has built-in login password manager functionality which keeps track of the login secrets of all visited websites. Whenever user logins to any website, he/she will be prompted to save the credentials for later use and if user chooses so, then the username & passwords will be stored in internal login database. So next time onwards whenever user visits that website, he/she will be automatically logged in using these stored credentials which saves hassle of entering the credentials every time.

Chrome stores all the sign-on secrets into the internal database file called 'Web data' in the current user profile folder. Newer version has moved the login passwords related database into new file named 'Login Data'.This database file is in SQLite format and contains number of tables storing different kind of data such as auto complete, search keyword, ie7logins etc in addition to login secrets.

The logins table mainly contains the information about sign-on secrets such as website URL, username, password fields etc. All this information is stored in the clear text except passwords which are in encrypted format.

Unfortunately, sometimes a password gets garbled and cannot be decrypted. Chrome behaves rather erratically in this case, as it still fills in passwords and saves new ones, but cannot display or sync saved passwords. You can use this little utility to see all passwords except the garbled ones (which are presumed lost).

You can also use it to create a version of the password database without the garbled entries. However, you must copy the result into the Chrome directory yourself. We strongly recommend that you BACK UP the password database (named `Login Data`) before overwriting it with the new version, as the functionality is NOT VERY WELL TESTED. And then, if your passwords are lost, just restore the old file.

#### Prerequisites

Install the following packages using pip:

* secretstorage
* pycryptodome

#### Windows Implementation
Google Chrome encrypt the password with the help of CryptProtectData function, built into Windows. Now while this can be a very secure function using a triple-DES algorithm and creating user-specific keys to encrypt the data, it can still be decrypted as long as you are logged into the same account as the user who encrypted it.The CryptProtectData function has a twin, who does the opposite to it; CryptUnprotectData, which... well you guessed it, decrypts the data. And obviously this is going to be very useful in trying to decrypt the stored passwords.

#### Mac/Linux Implementation
Encryption Scheme: AES-128 CBC with a constant salt and constant iterations. The decryption key is a PBKDF2 key generated with the following:

* salt is b'saltysalt'
* key length is 16
* iv is 16 bytes of space b' ' * 16
* on Mac OSX:
  * password is in keychain under Chrome Safe Storage
    * I use the excellent keyring package to get the password
    * You could also use bash: security find-generic-password -w -s "Chrome Safe Storage"
  * number of iterations is 1003
* on Linux:
  * password is peanuts
  * number of iterations is 1


## Python Implementation (Working)

Stop Chrome before running this utility.

#### Usage
```python
>>> from chrome import Chrome
>>> chrome_pwd = Chrome()
>>> chrome_pwd.get_login_db
'/Users/x899/Library/Application Support/Google/Chrome/Default/'
>>> chrome_pwd.get_password(prettyprint=True)
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
```

To generate a new `Login Data` in the current directory:
```
>>> chrome_pwd.rewrite_passwords()
Failed and excluded: INSERT INTO "logins" VALUES('https://some.website.com/password/change/blah','https://some.website.com/password/change/blah','','some@user.com','password',X'FF00FF00FF00','','https://some.website.com/',1334343408358214120,0,0,0,0,X'9801000006000000000000005800000068747470733A2F2F617574682E6265656C647374656D6D656E9485349758394875394579348758616E67652F75663538575F4443433643663833776D713173796C46773874623979574C73335038676A5F366B3546586B3300000068747470733A2F2F617574682E6265656C647374656D6D656E2E6E6C2F70617373776F72642F6368616E67652F6368616E67650002000000080000000000000008000000700061007300730077006F0072006400000000000800000070617373776F726400000000FFFFFF7F000000000000000000000000010000000100000001000000020000000000000000000000000000000000000001000000000000000000000008000000000000000F000000700061007300730077006F007200640043006F006E006600690072006D000000000000000800000070617373776F726400000000FFFFFF7F00000000000000000000000001000000010000000100000002000000000000000000000000000000000000000500000000000000000000000100000000000000040000006E756C6C',0,'','','',0,0,X'00000000',4,1876808358214086,X'00000000');
New Login Data ready, use at your own risk
```

Then back up Chrome's `Login Data` file and overwrite it with the new one that is in your current directory.

## Contribute
Feel free to contribute. Please Follow PEP8 Guidelines.

TO DO:
* Cookie support
* Updating database password directly
