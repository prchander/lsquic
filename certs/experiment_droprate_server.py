import os
import sys
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

algorithm = ''
algorithms = ['rsa', 'Dilithium2', 'Dilithium3', 'Dilithium4', 'Falcon512', 'Falcon1024', 'rsa3072_Dilithium2', 'rsa3072_Dilithium3', 'rsa3072_Falcon512', 'p256_Dilithium2', 'p256_Dilithium3', 'p256_Dilithium4', 'p256_Falcon512']
print('Pick an algorithm:')
for i, v in enumerate(algorithms):
	print(f'{i + 1}\t\t{v}')
selection = int(input(f'Pick your algorithm to use (1 to {len(algorithms)}): '))
if selection > 0 and selection <= len(algorithms):
	algorithm = algorithms[selection - 1]
else:
	print('Invalid input.')
	sys.exit()

print('USING ' + algorithm)
myCmd= f'{lsquic_dir}/build/bin/./http_server -c www.example.com,{lsquic_dir}/certs/{algorithm}/key_crt.pem,{lsquic_dir}/certs/Dilithium2/key_srv.pem -s {server_ip}:4433 -p /'
os.system(myCmd)