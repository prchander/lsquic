import datetime
import os
import time

print('Starting PCAP Logger...')

# Send commands to the Linux terminal
def terminal(cmd):
	return os.popen(cmd).read()

def pause_until_next_minute():
	minute = datetime.datetime.now().minute
	print(f'Waiting until minute: { minute + 1 }')
	while minute == datetime.datetime.now().minute:
		time.sleep(0.001)
	print('Starting...')

pause_until_next_minute()
terminal('sudo tcpdump -i any -w Logs/WIRESHARK_LOG.pcap \'port 4433\'')
#terminal('tshark -i any -d tcp.port==4433,http -w Logs/WIRESHARK_LOG')