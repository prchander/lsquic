#!/usr/bin/python3

import os
import sys
import socket

algorithm = 'dilithium2'
algorithms = ['rsa', 'dilithium2', 'dilithium3', 'dilithium5', 'falcon512', 'falcon1024'] #, 'rsa3072_dilithium2', 'rsa3072_dilithium3', 'rsa3072_falcon512', 'p256_dilithium2', 'p256_dilithium3', 'p256_dilithium4', 'p256_falcon512']
if len(sys.argv) > 1:
	algorithm = sys.argv[1]
	
if algorithm not in algorithms:
	print(f'ARGUMENT "{algorithm}" NOT VALID ALGORITHM')
	sys.exit()

print('Using algorithm: "' + algorithm + '"')

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 1))
	return s.getsockname()[0]

lsquic_dir = os.path.expanduser('~/oqs/lsquic')
server_ip = getIP()
print()
print(f'Server IP: {server_ip}')
print()

#algorithm = ''
#print('Pick an algorithm:')
#for i, v in enumerate(algorithms):
#	print(f'{i + 1}\t\t{v}')
#selection = int(input(f'Pick your algorithm to use (1 to {len(algorithms)}): '))
#if selection > 0 and selection <= len(algorithms):
#	algorithm = algorithms[selection - 1]
#else:
#	print('Invalid input.')
#	sys.exit()

print('USING ALGORITHM: ' + algorithm)
myCmd= f'{lsquic_dir}/build/bin/./http_server -c www.example.com,{lsquic_dir}/certs/{algorithm}/key_crt.pem,{lsquic_dir}/certs/{algorithm}/key_srv.pem -s {server_ip}:4433 -p /'

os.system(myCmd)