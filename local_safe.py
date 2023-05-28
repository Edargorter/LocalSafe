#!/usr/bin/env python3

import multiprocessing
import random
import string 
from getpass import getpass
import base64
import hashlib
from shutil import copyfile 
from Crypto.Cipher import AES
from Crypto import Random
from sys import argv 
from os import remove

master_key = None
filename = None
saved_copy = None
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def error(msg):
    print("ERROR: ", msg)

def encrypt(raw):
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(master_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(bytes(raw.encode('utf-8'))))
 
def decrypt(enc):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(master_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))

def get_keyval():
    keyval = {}
    try:
        with open(filename, 'r') as f:
            lines = [i.strip() for i in f.readlines()]
            for line in lines:
                d_line = line
                dd_line = bytes.decode(decrypt(d_line))
                key, val = dd_line.split()
                d_key = bytes.decode(decrypt(key))
                keyval[d_key] = val
    except Exception as e:
        error(e)
        print("You are not authenticated.")
        return None

    return keyval

def retrieve():
    keyval = get_keyval()
    if keyval is None:
        return 
    key = input("Key: ")
    e_val = keyval.get(key, -1)
    if e_val != -1:
        d_val = decrypt(e_val)
        print("Value: ", bytes.decode(d_val))

def store():
    key = input("Key: ")
    value = input("Value: ")
    if key == "" or value == "":
        error("Key and value must be non-empty.")
    e_key = bytes.decode(encrypt(key))
    e_value = bytes.decode(encrypt(value))
    row = encrypt(e_key + " " + e_value)
    try:
        with open(filename, 'a') as f:
            f.write("{}\n".format(bytes.decode(row)))
    except Exception as e:
        error(e)

def authenticate():
    global master_key
    master = getpass("Enter password: ")
    master_key = hashlib.sha256(master.encode("utf-8")).digest()

options = [authenticate, store, retrieve]

def menu():
    print("\n--- LocalSafe Key-Value Store ---\n")
    print("1) Authenticate")
    print("2) Store key-value pair")
    print("3) Retrieve value from key")
    print("4) Exit")
    print("\n-> ", end=" ")

def interpreter():
    for i in range(100):
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
    copyfile(filename, saved_copy)

    interpreter()
    try:
        remove(saved_copy)
    except Exception as e:
        error(e)
    
    '''
    p = multiprocessing.Process(target = interpreter, name = "interpreter")
    p.start()
    p.join(60)

    if p.is_alive():
        print("Timeout... exiting.")
        p.terminate()
        p.join()
        '''
