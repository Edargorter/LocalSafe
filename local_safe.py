#!/usr/bin/env python3

import multiprocessing
import random
import string 
from getpass import getpass
import base64
import hashlib
import shutil
from Crypto.Cipher import AES
from Crypto import Random
from sys import argv 

master = None
filename = None
saved_copy = None
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def error(msg):
    print("ERROR: ", msg)

def encrypt(raw, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(bytes(raw.encode('utf-8'))))
 
def decrypt(enc, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))

def get_keyval():
    keyval = {}

    try:
        with open(filename, 'r') as f:
            lines = [i.strip() for i in f.readlines()]
            for line in lines:
                d_line = decrypt(line, master)
                k, v = d_line.split(" ")
                keyval[k] = v
    except Exception as e:
        error(e)
        return None

    return keyval

def retrieve():
    keyval = get_keyval()
    if keyval is None:
        return 
    key = input("Key: ")
    e_key = encrypt(key)
    e_val = keyval.get(e_key, -1)
    if e_val != -1:
        d_val = decrypt(bytes(e_val), master)
        print("Value: ", bytes.decode(d_val))

def store():
    #keyval = get_keyval()
    print(master)
    key = input("Key: ")
    value = input("Value: ")
    if key == "" or value == "":
        error("Key and value must be non-empty.")
    e_key = encrypt(key, master) 
    e_value = encrypt(value, master) 
    row = encrypt(str(e_key) + " " + str(e_value), master)
    try:
        with open(filename, 'a') as f:
            f.write("{}\n".format(str(row)))
    except Exception as e:
        error(e)

def authenticate():
    global master
    master = getpass("Enter password: ")

options = [authenticate, store, retrieve]

def menu():
    print("\n--- LocalSafe Key-Value Store ---\n")
    print("1) Authenticate")
    print("2) Store key-value pair")
    print("3) Retrieve value from key")
    print("4) Exit")
    print("\n-> ", end=" ")

def interpreter():
    inp = -1 
    while inp != 4:
        menu()
        inp = input()
        if inp.isdigit():
            if 0 < int(inp) <= len(options):
                options[int(inp) - 1]()
            else:
                break
        else:
            error("Input is NaN")   

if __name__ == "__main__":
    if len(argv) > 1:
        filename = argv[1]
    else:
        print("No argument given. Exiting.")
        exit(1)

    saved_copy = filename + "_" + ''.join(random.choices(string.ascii_letters + string.digits, k = 8))
    shutil.copyfile(filename, saved_copy)

    interpreter()
    
    '''
    p = multiprocessing.Process(target = interpreter, name = "interpreter")
    p.start()
    p.join(60)

    if p.is_alive():
        print("Timeout... exiting.")
        master = None
        p.terminate()
        p.join()
        '''
