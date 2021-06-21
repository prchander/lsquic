import csv
import os
import re
import sys
import time

# List the files with a regular expression
def listFiles(regex, directory = ''):
	path = os.path.join(os.curdir, directory)
	return [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and bool(re.match(regex, file))]


csvFiles = listFiles(r'.*_parsed_handshake.csv', 'handshakeLevel')

for inputFileName in csvFiles:

	match = re.match(r'WIRESHARK_([^_]+(?:_aes)?(?:_drop)?)_parsed_handshake.csv', os.path.basename(inputFileName))
	if match is None:
		print('ERROR:', 'File name\"', inputFileName, '\" does not have a valid algorithm name, please ensure that the algorithm name does not contain an underscore, as this will mess up the regular expression.')
		continue
	algorithm = match.group(1).upper()
	
	match = re.match(r'WIRESHARK_([^_]+(?:_aes)?(?:_drop)?)_parsed_handshake.csv', os.path.basename(inputFileName))
	if match is None:
		print('ERROR:', 'Unable to find CPU file name for file \"', inputFileName, '\"')
		continue

	cpuFileName = 'LOGGED_CPU_' + match.group(1) + '.csv'
	if not os.path.exists(cpuFileName):
		print('ERROR:', 'Unable to find CPU file \"', cpuFileName, '\"')
		continue

	#inputFileName = selectFile(r'.*\_parsed.csv', False)
	#if inputFileName == '':
	#	sys.exit()
	print('\nOPENING', inputFileName)
	print('OPENING', cpuFileName, '\n')

	directory = 'finalPostProcessed'
	fileName = os.path.join(directory, 'FINAL_' + algorithm + '.csv')
	outputFile = open(fileName, 'w', newline='')

	readerFile = open(inputFileName, 'r')
	reader = csv.reader(x.replace('\0', '') for x in readerFile)
	readerHeader = next(reader)

	cpuReaderFile = open(cpuFileName, 'r')
	cpuReader = csv.reader(x.replace('\0', '') for x in cpuReaderFile)
	cpuReaderHeader = next(cpuReader)
	cpuData = []
	print('Reading CPU data...')
	for cpuSample in cpuReader:
		timestamp = cpuSample[1]
		cpu = cpuSample[2]
		mem = cpuSample[5]
		disk = cpuSample[9]
		cpuData.append([timestamp, cpu, mem, disk])


	newHeader = readerHeader
	newHeader.append('CPU utilization')
	newHeader.append('Memory bytes')
	newHeader.append('Disk bytes')
	outputFile.write(','.join(newHeader) + ',\n')

	cpuDataIndex = 0

	for handshake in reader:
		startTime = float(handshake[0])
		endTime = float(handshake[1])
		handshakeNum = int(handshake[2])

		if handshakeNum % 100 == 0:
			print(fileName, 'Handshake', handshakeNum)

		newRow = handshake

		cpuSum = 0
		cpuNum = 0
		memStart = 0
		memEnd = 0
		diskStart = 0
		diskEnd = 0

		foundStart = False
		for i in range(cpuDataIndex, len(cpuData)):
			cpuSample = cpuData[i]
			timestamp = float(cpuSample[0])
			if timestamp >= startTime and timestamp <= endTime:
				if foundStart == False:
					foundStart = True
					memStart = float(cpuSample[2])
					diskStart = float(cpuSample[3])
					cpuDataIndex = i # Next time, start at where the last one started

				cpuSum += float(cpuSample[1])
				cpuNum += 1
				memEnd = float(cpuSample[2])
				diskEnd = float(cpuSample[3])
			elif foundStart == True or timestamp > endTime: # End of sequence reached
				break

		if cpuNum == 0: cpuNum = 1 # Avoid divide by zero
		newRow.append(cpuSum / cpuNum)
		#print(cpuSum, cpuNum, cpuSum / cpuNum)
		newRow.append(max(0, memEnd - memStart))
		newRow.append(max(0, diskEnd - diskStart))

		outputFile.write(','.join(map(str,newRow)) + ',\n')




