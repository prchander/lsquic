import os 
import socket

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 1))
	return s.getsockname()[0]

lsquic_dir = os.path.expanduser('~/oqs/lsquic')
server_ip = getIP()
print()
print(f'Server IP: {server_ip}')
print()

myCmd= f'{lsquic_dir}/build/bin/./http_server -c www.example.com,{lsquic_dir}/certs/dilithium2/key_crt.pem,{lsquic_dir}/certs/dilithium2/key_srv.pem -s {server_ip}:4433 -p /'
os.system(myCmd)
