#!/usr/bin/env python3

# LocalSafe by Edargorter 
#
# Simple key-value store with encryption using multiple master keys 
# 

from multiprocessing import Process
import random
import string 
from getpass import getpass
import base64
import hashlib
from shutil import copyfile 
from Crypto.Cipher import AES
from Crypto import Random
from sys import argv, exit
from os import remove
from pyperclip import copy
import signal

killed = False
master_key = None
filename = None
saved_copy = None
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def clean_terminate(*args):
    global killed
    try:
        if not killed:
            killed = True
            remove(saved_copy)
    except Exception as e:
        error(e)
    exit(0)
	
def needs_auth():
    return master_key is None

def error(msg):
    print("ERROR:", msg)

def encrypt(raw):
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    return base64.b64encode(iv + cipher.encrypt(bytes(raw.encode('utf-8'))))
 
def decrypt(enc):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    return unpad(cipher.decrypt(enc[16:]))

def get_keyval():
    keyval = {}
    kvref = []
    try:
        with open(filename, 'r') as f:
            lines = [i.strip() for i in f.readlines()]
            for line in lines:
                try:
                    d_line = line
                    dd_line = bytes.decode(decrypt(d_line))
                    key, val = dd_line.split()
                    d_key = bytes.decode(decrypt(key))
                    keyval[d_key] = val
                    kvref.append(d_key)
                except Exception as e:
                    pass
    except Exception as e:
        error(e)
        print("You are not authenticated.")
        return None

    return keyval, kvref

def getKeys():
    if needs_auth():
        error("Please authenticate first.")
        return
    keyval, kvref = get_keyval()
    if len(keyval.keys()) == 0:
        print("No keys to list.")
    else:
        print("Keys: ")
        for i in range(len(kvref)):
            print(f"{i+1}) {kvref[i]}")

def retrieve():
    keyval, kvref = get_keyval()
    if keyval is None:
        return 
    while True:
        key = input("Key: ")
        if len(key) == 0:
            continue
        if key.isdigit():
            key = int(key)
            if key > 0 and key <= len(kvref):
                key = kvref[key-1]
                break
        else:
            break
        
    e_val = keyval.get(key, None)
    if e_val is not None:
        d_val = decrypt(e_val)
        return bytes.decode(d_val)

    return None 

def retrieve_to_print():
    if needs_auth():
        error("Please authenticate first.")
        return
    val = retrieve()
    if val is not None:
        print("Value:", val)
    else:
        print("Key not found.")

def retrieve_to_copy():
    if needs_auth():
        error("Please authenticate first.")
        return
    val = retrieve()
    if val is not None:
        copy(val)
        print("Value copied to clipboard.")
    else:
        print("Key not found.")

def store():
    if needs_auth():
        error("Please authenticate first.")
        return
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

def authenticate_with_check():
    global master_key
    for i in range(3):
        master = getpass("Enter password: ")
        master_confirm = getpass("Re-enter password: ")
        if master == master_confirm:
            master_key = hashlib.sha256(master.encode("utf-8")).digest()
            break
        else:
            error("Passwords mismatch")

options = [authenticate, authenticate_with_check, store, retrieve_to_print, retrieve_to_copy, getKeys]

def menu():
    print("\n--- LocalSafe Key-Value Store ---\n")
    print("1) Authenticate")
    print("2) Authenticate with Check")
    print("3) Store key-value pair")
    print("4) Get value from key")
    print("5) Copy value from key")
    print("6) List keys")
    print("7) Exit")
    print("\n-> ", end=" ")

def interpreter():
    print("\nFile in use: {}\nWith backup (deleted on exit): {}".format(filename, saved_copy))
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
    clean_terminate()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, clean_terminate)
    signal.signal(signal.SIGTERM, clean_terminate)

    if len(argv) > 1:
        filename = argv[1]
    else:
        print("No argument given. Exiting.")
        exit(1)

    saved_copy = filename + "_" + ''.join(random.choices(string.ascii_letters + string.digits, k = 8))
    try:
        copyfile(filename, saved_copy)
    except Exception as e:
        print("File not found.")
        exit(1)
    interpreter()
    
    '''
    p = Process(target = interpreter, name = "interpreter")
    p.start()
    p.join(60)

    if p.is_alive():
        print("Time's up!")
        p.terminate()
        p.join()
        '''
