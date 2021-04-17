#!/usr/bin/python3

import datetime
import os
import time
import sys

algorithms = ['rsa', 'dilithium2', 'dilithium3', 'dilithium5', 'falcon512', 'falcon1024'] #, 'rsa3072_dilithium2', 'rsa3072_dilithium3', 'rsa3072_falcon512', 'p256_dilithium2', 'p256_dilithium3', 'p256_dilithium4', 'p256_falcon512']

if len(sys.argv) >= 4:
	interface = sys.argv[1]
	algorithm = sys.argv[2]
	zeroRoundTrip = sys.argv[3] == 'True'
else:
	print('Not enough parameters given')
	print('Parameters are [interface, algorithm, zeroRoundTrip==True]')
	sys.exit()

if algorithm not in algorithms:
	print(f'Unsupported algorithm: "{algorithm}"')

print('Starting PCAP Logger...')

# Send commands to the Linux terminal
def terminal(cmd):
	return os.popen(cmd).read()

zrtStr = ''
if zeroRoundTrip: zrtStr = '_0RTT'

terminal(f'sudo tcpdump -i {interface} -w fullyAutomatedLogs/TCPDUMP_{algorithm}{zrtStr}.pcap \'port 4433\'')

#terminal('sudo tcpdump -i any -w newLogs/WIRESHARK_dilithium5-aes_0RTT.pcap \'port 4433\'')
#terminal('tshark -i any -d tcp.port==4433,http -w Logs/WIRESHARK_LOG')