import socket
import hashlib
import time

# loop every hosts
VARS = [ 'a', 'b', 'c', 'd', 'e' ]
HOSTS = [ "time-<v>-g.nist.gov", "time-<v>-wwv.nist.gov", "time-<v>-b.nist.gov" ]

PORT = 13

# connect to datetime server and get datetime
def connect_and_fetch(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        return s.recv(1024)


# fetch datetime with retry mechanism
def fetch_datetime():
    for host_var in HOSTS:
        for var in VARS:
            host = host_var.replace('<v>', var)
            print(f'using {host}:{PORT} to fetch datetime...')
            data = connect_and_fetch(host, PORT)
            if data:
                return data
            else:
                print(f'fetch failed, wait 3 seconds and using next host...')
                time.sleep(3) # request slowly
        print(f'All hosts failed. wait 10 seconds and rerun fetch...')
        time.sleep(10) # request slowly

def fetch_excution_id():
    # production mode
    data = fetch_datetime()
    # debug mode
    #d ata = b"test_debug_time"
    print('The DateTime when server started is: ', data.decode('utf-8'))
    return hashlib.sha256(data).hexdigest() # hash the datetime string

EXE_ID = fetch_excution_id()


