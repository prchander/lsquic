import os 
import socket

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 1))
	return s.getsockname()[0]

lsquic_dir = os.path.expanduser('~/oqs/lsquic')
key_crt_dir = f'{lsquic_dir}/certs/rsa/key_crt.pem'
key_srv_dir = f'{lsquic_dir}/certs/rsa/key_srv.pem'

print(f'Key CRT Directory: {key_crt_dir}')
print(f'Key SRV Directory: {key_srv_dir}')

server_ip = getIP()
print()
print(f'Server IP: {server_ip}')
print()

myCmd= f'{lsquic_dir}/build/bin/./echo_server -c www.example.com,{key_crt_dir},{key_srv_dir} -s {server_ip}:4433'
os.system(myCmd)
