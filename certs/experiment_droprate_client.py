import os
import re
import socket
import time
import sys
import paramiko

# sudo apt-get install python3-paramiko


global ssh_obj


numSamples = 1000
zeroRoundTrip = True
droprates = [0, 10, 40]

print('Number of samples', numSamples)

# Send a command to the linux terminal
def terminal(cmd):
	#print(cmd)
	return os.popen(cmd).read()

def call_ssh(cmd):
	#print('Calling ', cmd)
	ssh_stdin, ssh_stdout, ssh_stderr = ssh_obj.exec_command(cmd)
	outlines = ssh_stdout.readlines()
	response = ''.join(outlines)
	#print('Ending ', cmd)
	return response


def clearFilters():
	terminal(f'sudo tc qdisc del dev {interface} root netem')

def applyFilters(droprate):
	if droprate != 0:
		terminal(f'sudo tc qdisc add dev {interface} root netem loss {droprate}%')

def networkDelimeter(serverIP):
	terminal(f'nc -vz {serverIP} 4433 >/dev/null 2>/dev/null')

def getServerProcessID(serverIP):
	output = call_ssh('ps -A | grep http_server')
	output = output.strip().split(' ')
	if len(output) == 0 or output[0] == '': return None
	pid = int(output[0])
	return pid

def stopServerSSH(serverIP):
	pid = getServerProcessID(serverIP)
	if pid != None:
		print('Stopping server...')
		call_ssh(f'kill {pid}')

def restartServerSSH(algorithm, serverIP):
	stopServerSSH(serverIP)
	print('Starting server...')
	output = call_ssh(f'python3 ~/oqs/lsquic/certs/experiment_droprate_client.py {algorithm} </dev/null &>/dev/null &')
	print()
	print('Server started! Waiting 5 seconds...')
	time.sleep(5)

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 1))
	return s.getsockname()[0]

# Return an array of networking interfaces
def get_interfaces():
	raw = terminal('ip link show')
	interfaces = re.findall(r'[0-9]+: ([^:]+): ', raw)
	interfaces.remove('lo')

	interface = ''
	if len(interfaces) == 0:
		print(terminal('ifconfig'))
		print()
		print('No networking interfaces were found.')
		sys.exit()

	elif len(interfaces) == 1:
		interface = interfaces[0]

	else:
		for i in range(0, len(interfaces)):
			print(f'{i + 1} : {interfaces[i]}')
		selection = -1
		while selection < 1 or selection > len(interfaces):
			try:
				selection = int(input(f'Please select an interface (1 to {len(interfaces)}): '))
			except: pass
		interface = interfaces[selection - 1]
		print()
	return interface

lsquic_dir = os.path.expanduser('~/oqs/lsquic')


ssh_port = 22
ssh_username = 'bitcoin'
ssh_password = 'password'
print('Server username:', ssh_username)
print('Server password:', ssh_password)
print()

client_ip = getIP()
print(f'Client IP: {client_ip}')
serverIP = input('Please enter the server IP: ')
interface = get_interfaces()

print('Connecting to SSH...')
ssh_obj = paramiko.SSHClient()
ssh_obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_obj.connect(serverIP, ssh_port, ssh_username, ssh_password)


try:
	os.remove('0rttTest.txt')
except: pass

if zeroRoundTrip:
	myCmd= f'{lsquic_dir}/build/bin/./http_client -0 0rttTest.txt -H www.example.com -s {serverIP}:4433 -p /'
else:
	myCmd= f'{lsquic_dir}/build/bin/./http_client -H www.example.com -s {serverIP}:4433 -p /'



algorithms = ['rsa', 'dilithium2', 'dilithium3', 'dilithium5', 'falcon512', 'falcon1024'] #, 'rsa3072_dilithium2', 'rsa3072_dilithium3', 'rsa3072_falcon512', 'p256_dilithium2', 'p256_dilithium3', 'p256_dilithium4', 'p256_falcon512']

for algorithm in algorithms:
	print(f'Using algorithm: "{algorithm}"')

	clearFilters()
	networkDelimeter(serverIP)
	networkDelimeter(serverIP)
	networkDelimeter(serverIP)
	restartServerSSH(algorithm, serverIP)

	for droprate in droprates:
		print(f'Testing delay: {droprate}')
		samples = numSamples
		while samples > 0:

			clearFilters()
			networkDelimeter(serverIP)
			applyFilters(droprate)

			os.system(myCmd)
			samples -=1
		print('Waiting 3 minutes before starting next droprate test...')
		time.sleep(120)
	time.sleep(120)


print()
print('Experiment completed.')
