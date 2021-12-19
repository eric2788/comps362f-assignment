import socket
import hashlib

HOST = "time-a-g.nist.gov"
PORT = 13

def fetch_datetime():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True: # sometimes it will receive none, so using while True for safety
            data = s.recv(1024)
            if data:
                return data

def fetch_excution_id():
    # production mode
    data = fetch_datetime()
    # debug mode
    #d ata = b"test_debug_time"
    print('The DateTime when server started is: ', data.decode('utf-8'))
    return hashlib.sha256(data).hexdigest() # hash the datetime string

EXE_ID = fetch_excution_id()


