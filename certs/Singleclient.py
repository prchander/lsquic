import os
import socket

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 1))
	return s.getsockname()[0]

lsquic_dir = os.path.expanduser('~/oqs/lsquic')
cert = os.path.expanduser('~/oqs/lsquic/certs/new_certs')

n = 1

client_ip = getIP()
print(f'Client IP: {client_ip}')
print(f'Number of samples: ', n)
serverIP = input('Please enter the server IP: ')

#myCmd = f'{lsquic_dir}/build/bin/./http_client -H www.example.com -s {serverIP}:4433 -p /'
myCmd = f'{lsquic_dir}/build/bin/./http_client -L warn -C {cert}/dilithium2/key_CA.pem -H www.example.com -s {serverIP}:4433 -p /'


while n>0:
    os.system(myCmd)
    n -= 1