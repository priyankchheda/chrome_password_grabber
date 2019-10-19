# Chrome-Password-Grabber
Get unencrypted 'Saved Password' from Google Chrome

## Introduction
Like other browsers Chrome also has built-in login password manager functionality which keeps track of the login secrets of all visited websites. Whenever user logins to any website, he/she will be prompted to save the credentials for later use and if user chooses so, then the username & passwords will be stored in internal login database. So next time onwards whenever user visits that website, he/she will be automatically logged in using these stored credentials which saves hassle of entering the credentials every time.

Chrome stores all the sign-on secrets into the internal database file called 'Web data' in the current user profile folder. Newer version has moved the login passwords related database into new file named 'Login Data'.This database file is in SQLite format and contains number of tables storing different kind of data such as auto complete, search keyword, ie7logins etc in addition to login secrets.

The logins table mainly contains the information about sign-on secrets such as website URL, username, password fields etc. All this information is stored in the clear text except passwords which are in encrypted format. 

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

#### Usage
```python
>>> from chrome_passwd import ChromePasswd
>>> chrome_pwd = ChromePasswd()
>>> print(chrome_pwd.get_login_db)
/Users/x899/Library/Application Support/Google/Chrome/Default/
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

## Contribute
Feel free to contribute. Please Follow PEP8 Guidelines.

TO DO:
* Cookie support
* Updating database password directly


