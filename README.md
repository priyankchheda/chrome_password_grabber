# Chrome-Password-Grabber
Get unencrypted 'Saved Password' from Google Chrome

## Introduction
Like other browsers Chrome also has built-in login password manager functionality which keeps track of the login secrets of all visited websites. Whenever user logins to any website, he/she will be prompted to save the credentials for later use and if user chooses so, then the username & passwords will be stored in internal login database. So next time onwards whenever user visits that website, he/she will be automatically logged in using these stored credentials which saves hassle of entering the credentials every time.

Chrome stores all the sign-on secrets into the internal database file called 'Web data' in the current user profile folder. Newer version has moved the login passwords related database into new file named 'Login Data'.This database file is in SQLite format and contains number of tables storing different kind of data such as auto complete, search keyword, ie7logins etc in addition to login secrets.

The logins table mainly contains the information about sign-on secrets such as website URL, username, password fields etc. All this information is stored in the clear text except passwords which are in encrypted format. 

Google Chrome encrypt the password with the help of CryptProtectData function, built into Windows. Now while this can be a very secure function using a triple-DES algorithm and creating user-specific keys to encrypt the data, it can still be decrypted as long as you are logged into the same account as the user who encrypted it.The CryptProtectData function has a twin, who does the opposite to it; CryptUnprotectData, which... well you guessed it, decrypts the data. And obviously this is going to be very useful in trying to decrypt the stored passwords.

## Python Implementation (Working)

#### Usage
```python
C:/> python PasswordGrabber.py
<website> - <username/email>:<plain_text_password>
C:/> 
```
## C Implementation (Not Working)

It compiled correctly without any error, but the decrypted data was not correct.

```c
C:/>gcc -o ChromePasswordGrabber ChromePasswordGrabber.c sqlite3.o -lcrypt32

C:/>ChromePasswordGrabber.exe
Opened database successfully
Callback function called: Important Data
Error Number 57.

Operation done successfully

C:/>
$
```

According to System Error Codes (0-499), 0x57 is for ERROR_INVALID_PARAMETER (The parameter is incorrect)

