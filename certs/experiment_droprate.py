import os
import re
import socket
import time
import sys
import paramiko
import threading
import atexit

# sudo apt-get install python3-paramiko


global ssh_obj
global closingApplication

numSamples = 1000
zeroRoundTrip = False
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
	terminal(f'sudo tc qdisc del dev {interface} root netem > /dev/null 2>&1')

def applyFilters(droprate):
	if droprate != 0:
		terminal(f'sudo tc qdisc add dev {interface} root netem loss {droprate}%')

def networkDelimeter(serverIP):
	terminal(f'nc -vz {serverIP} 4433 >/dev/null 2>/dev/null')


threads = []

# Run a fuction in parallel to other code
class Task(threading.Thread):
	def __init__(self, name, function, *args):
		assert isinstance(name, str), 'Argument "name" is not a string'
		assert callable(function), 'Argument "function" is not callable'
		threading.Thread.__init__(self)
		self._stop_event = threading.Event()

		self.setName(name)
		self.function = function
		self.args = args

	def run(self):
		self.function(*self.args)
		self._stop_event.set()

	def stop(self):
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()

# Creates a new thread and starts it
def create_task(name, function, *args):
	if len(threads) >= 200:
		# Remove the first 10 threads if it exceeds 200, to balance it out
		for i in range(10):
			threads[i].stop()
			del threads[i]
	task = Task(name, function, *args)
	threads.append(task)
	task.start()
	return task

# This function is ran when the script is stopped
def on_close():
	global closingApplication
	closingApplication = True
	print('Stopping active threads')

	stopServerSSH(serverIP)
	for thread in threads:
		thread.stop()
	stopTcpdump()
	
	print()
	print('Goodbye.')

atexit.register(on_close) # Make on_close() run when the script terminates


def getTcpdumpProcessID():
	output = terminal('ps -A | grep tcpdump')
	output = output.strip().split(' ')
	if len(output) == 0 or output[0] == '': return None
	pid = int(output[0])
	return pid

def stopTcpdump():
	pid = getTcpdumpProcessID()
	if pid != None:
		print('Stopping TCPDUMP...')
		call_ssh(f'sudo pkill -f tcpdump')
	

def startTcpdump(interface, algorithm, zeroRoundTrip):
	stopTcpdump()
	myCmd = f'python3 experiment_run_tcpdump.py {interface} {algorithm} {zeroRoundTrip}'
	print(myCmd)
	create_task('tcpdump', terminal, myCmd)


def startCPUlogger():
	print('Starting CPU logger...')
	myCmd = f'python3 experiment_log_cpu.py'
	print(myCmd)
	create_task('cpu logger', terminal, myCmd)


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
		call_ssh(f'sudo pkill -f http_server')

def restartServerSSH(algorithm, serverIP):
	stopServerSSH(serverIP)
	print('Starting server...')
	output = call_ssh(f'python3 ~/oqs/lsquic/certs/experiment_droprate_client.py {algorithm} </dev/null &>/dev/null &')
	print()
	print('Server started! Waiting 5 seconds to be certain...')
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
cert = os.path.expanduser('~/oqs/lsquic/certs')

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

stopServerSSH(serverIP)
stopTcpdump()

numLoops = 0
closingApplication = False
while not closingApplication:
	try:
		for algorithm in algorithms:
			print(f'Using algorithm: "{algorithm}"')
			startTcpdump(interface, algorithm, zeroRoundTrip)
			time.sleep(1)

			if zeroRoundTrip:
				myCmd= f'{lsquic_dir}/build/bin/./http_client -0 0rttTest.txt -C {cert}/{algorithm}/key_CA.pem -H www.example.com -s {serverIP}:4433 -p /'
			else:
				myCmd= f'{lsquic_dir}/build/bin/./http_client -C {cert}/{algorithm}/key_CA.pem -H www.example.com -s {serverIP}:4433 -p /'
			
			print('Starting...')

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
			stopTcpdump()
		
		numLoops += 1
		print('Number of times through each algorithm:', numLoops)
	except KeyboardInterrupt():
		sys.exit()


print()
print('Experiment completed.')
