# LocalSafe 

A simple key-value store with encryption using multiple master keys 

## Run binary example 
```
$ ./dist/local_safe testfile 

File in use: testfile
With backup (deleted on exit): testfile_uZAydC2a

--- LocalSafe Key-Value Store ---

1) Authenticate
2) Authenticate with Check
3) Store key-value pair
4) Get value from key
5) Copy value from key
6) List keys
7) Exit

->  1
Enter password: 

--- LocalSafe Key-Value Store ---

1) Authenticate
2) Authenticate with Check
3) Store key-value pair
4) Get value from key
5) Copy value from key
6) List keys
7) Exit

->  3
Key: myemail@example.com
Value: password123

--- LocalSafe Key-Value Store ---

1) Authenticate
2) Authenticate with Check
3) Store key-value pair
4) Get value from key
5) Copy value from key
6) List keys
7) Exit

->  6
1) okay
2) this@mail.com
3) ok@ok.com
4) myemail@example.com

--- LocalSafe Key-Value Store ---

1) Authenticate
2) Authenticate with Check
3) Store key-value pair
4) Get value from key
5) Copy value from key
6) List keys
7) Exit

->  4
Key: myemail@example.com
Value: password123

--- LocalSafe Key-Value Store ---

1) Authenticate
2) Authenticate with Check
3) Store key-value pair
4) Get value from key
5) Copy value from key
6) List keys
7) Exit

->  
```
