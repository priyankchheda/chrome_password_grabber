#include <stdio.h>
#include <windows.h>
#include <wincrypt.h>

int main (int argc, char* argv[])
{
	DATA_BLOB DataIn;
	DATA_BLOB DataOut;
	DATA_BLOB DataVerify;
	DATA_BLOB Data;
	BYTE *pbDataInput =(BYTE *)"Hello world of data protection.";
	DWORD cbDataInput = strlen((char *)pbDataInput)+1;
	
	DataIn.pbData = pbDataInput;    
	DataIn.cbData = cbDataInput;

	printf("The data to be encrypted is: %s\n",pbDataInput);

	if (CryptProtectData(&DataIn, NULL, NULL, NULL, NULL, 0, &DataOut)) 
		printf("The encryption phase worked.\n");
	else
		printf("Encryption Error!\n");

	Data = DataOut;
	if (CryptUnprotectData(&DataOut, NULL, NULL, NULL, NULL, 0, &DataVerify))
		printf("The decrypted data is: %s\n", DataVerify.pbData);
	else
		printf("Decryption Error!\n");

	while (*Data.pbData)
		printf("%x ", (unsigned int) *Data.pbData++);
	printf("\n");

	return 0;
}