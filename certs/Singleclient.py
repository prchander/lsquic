import os
import socket

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 1))
	return s.getsockname()[0]

lsquic_dir = os.path.expanduser('~/oqs/lsquic')
cert = os.path.expanduser('~/oqs/lsquic/certs/new_certs')


client_ip = getIP()
print(f'Client IP: {client_ip}')
serverIP = input('Please enter the server IP: ')

#myCmd = f'{lsquic_dir}/build/bin/./http_client -H www.example.com -s {serverIP}:4433 -p /'
myCmd = f'{lsquic_dir}/build/bin/./http_client -C {cert}/dilithium2/key_CA.pem -H www.example.com -s {serverIP}:4433 -p /'
n = 1000

while n>0:
    os.system(myCmd)
    n -= 1