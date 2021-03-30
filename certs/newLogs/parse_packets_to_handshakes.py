import csv
import os
import re
import sys
import time

numSamples = 1000

droprates = [0, 10, 40] # Default

#quic_fields = ['', 'connection_number', 'packet_length', 'header_form', 'fixed_bit', 'long_packet_type', 'long_reserved', 'packet_number_length', 'version', 'dcil', 'dcid', 'scil', 'scid', 'token_length', 'length', 'packet_number', 'payload', 'frame', 'frame_type', 'crypto_offset', 'crypto_length', 'crypto_crypto_data', 'tls_handshake', 'tls_handshake_type', 'tls_handshake_length', 'tls_handshake_version', 'tls_handshake_random', 'tls_handshake_session_id_length', 'tls_handshake_cipher_suites_length', 'tls_handshake_ciphersuites', 'tls_handshake_ciphersuite', 'tls_handshake_comp_methods_length', 'tls_handshake_comp_methods', 'tls_handshake_comp_method', 'tls_handshake_extensions_length', 'tls_handshake_extension_type', 'tls_handshake_extension_len', 'tls_handshake_extensions_server_name_list_len', 'tls_handshake_extensions_server_name_type', 'tls_handshake_extensions_server_name_len', 'tls_handshake_extensions_server_name', 'tls_handshake_extensions_supported_groups_length', 'tls_handshake_extensions_supported_groups', 'tls_handshake_extensions_supported_group', 'tls_handshake_extensions_alpn_len', 'tls_handshake_extensions_alpn_list', 'tls_handshake_extensions_alpn_str_len', 'tls_handshake_extensions_alpn_str', 'tls_handshake_sig_hash_alg_len', 'tls_handshake_sig_hash_algs', 'tls_handshake_sig_hash_alg', 'tls_handshake_sig_hash_hash', 'tls_handshake_sig_hash_sig', 'tls_handshake_extensions_key_share_client_length', 'tls_handshake_extensions_key_share_group', 'tls_handshake_extensions_key_share_key_exchange_length', 'tls_handshake_extensions_key_share_key_exchange', 'tls_extension_psk_ke_modes_length', 'tls_extension_psk_ke_mode', 'tls_handshake_extensions_supported_versions_len', 'tls_handshake_extensions_supported_version', 'tls_parameter_type', 'tls_parameter_length', 'tls_parameter_value', 'tls_parameter_max_idle_timeout', 'tls_parameter_initial_max_data', 'tls_parameter_initial_max_stream_data_bidi_local', 'tls_parameter_initial_max_stream_data_uni', 'tls_parameter_initial_max_streams_bidi', 'tls_parameter_initial_max_streams_uni', 'tls_parameter_active_connection_id_limit', 'tls_parameter_min_ack_delay', 'tls_parameter_enable_time_stamp_v2', 'tls_parameter_loss_bits', 'tls_parameter_initial_source_connection_id', 'tls_handshake_extensions_padding_data', 'padding_length']


# Given a regular expression, list the files that match it, and ask for user input
def selectFile(regex, subdirs = False):
	files = []
	if subdirs:
		for (dirpath, dirnames, filenames) in os.walk('.'):
			for file in filenames:
				path = os.path.join(dirpath, file)
				if path[:2] == '.\\': path = path[2:]
				if bool(re.match(regex, path)):
					files.append(path)
	else:
		for file in os.listdir(os.curdir):
			if os.path.isfile(file) and bool(re.match(regex, file)):
				files.append(file)
	
	print()
	if len(files) == 0:
		print(f'No files were found that match "{regex}"')
		print()
		return ''

	print('List of files:')
	for i, file in enumerate(files):
		print(f'  File {i + 1}  -  {file}')
	print()

	selection = None
	while selection is None:
		try:
			i = int(input(f'Please select a file (1 to {len(files)}): '))
		except KeyboardInterrupt:
			sys.exit()
		except:
			pass
		if i > 0 and i <= len(files):
			selection = files[i - 1]
	print()
	return selection


def header():
	line = 'Handshake number,'
	line += 'Handshake duration (MS),'
	line += 'Droprate (%),'
	line += 'Number of packets,'
	line += 'Number of bytes,'
	line += 'Number of long headers,'
	line += 'Number of short headers,'
	line += 'Bytes for long headers,'
	line += 'Bytes for short headers,'
	#line = 'Timestamp,'
	#line += 'Timestamp (Seconds),'
	#line += 'Packet Num,'
	#line += 'Num Connections,'
	#line += 'Num Successful Connections,'
	#line += 'Total Bytes,'
	#line += 'QUIC Bytes,'
	#line += 'Layers,'
	#line += 'Long Packet Type,'
	#line += 'Frame,'
	#line += 'Frame Type,'
	return line



inputFileName = selectFile(r'.*\_parsed.csv', False)
if inputFileName == '':
	sys.exit()

# Select the droprate sequence
if '_delay_' in inputFileName:
	droprates = [0, 60, 100, 400, 1000]

print('Droprate sequence order: ' + str(droprates))
modifyConnectionSequence = input('Would you like to modify this? ').lower() in ['y', 'yes']
if modifyConnectionSequence:
	dropratesStr = input('Enter a new connection sequence (separated by spaces): ').split()
	droprates = [int(x) for x in dropratesStr]
	print('Droprate sequence order: ' + str(droprates))
print()


fileName = inputFileName[:-4] + '_handshake.csv'

outputFile = open(fileName, 'w', newline='')
readerFile = open(inputFileName, 'r')
reader = csv.reader(x.replace('\0', '') for x in readerFile)

temp_header = next(reader)

outputFile.write(header() + '\n')

time_start = {}
time_end = {}
handshake_length = {}
handshake_bytes = {}
handshake_long_headers = {}
handshake_short_headers = {}
handshake_long_headers_bytes = {}
handshake_short_headers_bytes = {}
#sample_num = -1

experimental_setup_droprate = []
# Copying the experiment_droprate_client.py experimental setup
for droprate in droprates:
	samples = numSamples
	while samples > 0:
		experimental_setup_droprate.append(droprate)
		samples -=1
# Used to track the Wireshark connection counter, and compare it to the experimental_setup_droprate
#timeline_of_samples = [] # "At this experiment height, wireshark is at connection N"
successful_connection_max_value = 0
droprate_at_successful_connection = []


for packet in reader:
	if packet[4] == '': continue
	#prev_sample_num = sample_num
	sample_num = int(packet[3])
	num_successful_connections = int(packet[4])

	# Keep track of the maximum
	if num_successful_connections > successful_connection_max_value:
		print(f'Processing handshake {num_successful_connections}')

		successful_connection_max_value = num_successful_connections
		if sample_num >= len(experimental_setup_droprate):
			# If for some reason there are more samples, assume it is part of the last sample
			current_droprate_at_this_time = experimental_setup_droprate[-1]
		else:
			current_droprate_at_this_time = experimental_setup_droprate[sample_num]
		# Keep the droprate_at_successful_connection up to date
		while len(droprate_at_successful_connection) < num_successful_connections:
			droprate_at_successful_connection.append(current_droprate_at_this_time)


	# Logging section, if entry doesn't exist, create it, otherwise update it
	if num_successful_connections not in handshake_length:
		# First time, initialize entry in dictionary
		handshake_length[num_successful_connections] = 0
		handshake_bytes[num_successful_connections] = 0
		handshake_long_headers[num_successful_connections] = 0
		handshake_short_headers[num_successful_connections] = 0
		handshake_long_headers_bytes[num_successful_connections] = 0
		handshake_short_headers_bytes[num_successful_connections] = 0
		time_start[num_successful_connections] = float(packet[1])

	time_end[num_successful_connections] = float(packet[1])

	handshake_length[num_successful_connections] += 1
	handshake_bytes[num_successful_connections] += int(packet[5])

	# Count number of long and short headers
	long_short_list = packet[11].split(' ')
	quic_bytes = packet[6].split(' ')
	for i in range(len(long_short_list)):
		if long_short_list[i] == 'long':
			handshake_long_headers[num_successful_connections] += 1
			handshake_long_headers_bytes[num_successful_connections] += int(quic_bytes[i])
		elif long_short_list[i] == 'short':
			handshake_short_headers[num_successful_connections] += 1
			handshake_short_headers_bytes[num_successful_connections] += int(quic_bytes[i])

for i in range(0, successful_connection_max_value):
	try:
		line = ''
		line += f'{i},'
		line += f'{(time_end[i] - time_start[i]) * 1000},'
		line += f'{droprate_at_successful_connection[i]},'
		line += f'{handshake_length[i]},'
		line += f'{handshake_bytes[i]},'
		line += f'{handshake_long_headers[i]},'
		line += f'{handshake_short_headers[i]},'
		line += f'{handshake_long_headers_bytes[i]},'
		line += f'{handshake_short_headers_bytes[i]},'

		outputFile.write(line + '\n')
	except:
		print(f'Handshake {i} does not exist!')
		continue

#readerFile.seek(0) # Reset it back to the beginning
# for packet in reader:
# 	timestamp = packet[0]
# 	timestamp_seconds = packet[1]
# 	packet_num = packet[2]
# 	num_connections = packet[3]
# 	num_successful_connections = packet[4]
# 	total_bytes = packet[5]
# 	quic_bytes = packet[6]
# 	layers = packet[7]
# 	long_packet_type = packet[8]
# 	frame = packet[9]
# 	frame_type = packet[10]
# 	long_short_headers = packet[11]

#file = open(fileName, 'w+')
#file.write(header() + '\n')

print()
print(f'Saved to "{fileName}".')