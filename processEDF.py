#need to tag trials data with blinks & saccades
#need to append trials data to samples for pupil analysis

file = open('temp.asc','r')
lastStart=0
samples = []
messages = []
trials = []
blinks = []
saccades = []
done = False
dataStarted = False
while not done:
	line = file.readline()
	if not dataStarted:
		if line[0].isdigit():
			dataStarted = True
	if dataStarted:
		if line[0:3]=='END':
			done = True
		elif line[0].isdigit():
			samples.append(line.replace(' ','').split('\t')[0:4])
		elif line[0:3]=='MSG':
			temp = line[4:-1]
			temp = temp.split(' ')
			if len(temp)==2:
				time = temp[0]
				temp = temp[1].split('\t')
				temp.insert(0,time)
				trials.append(temp)
			else:
				messages.append([temp[0],' '.join(temp[1:])])
		elif line[0:5]=='ESACC':
			saccades.append(line.split()[1:])
		elif line[0:6]=='EBLINK':
			blinks.append(line.split()[1:])
		elif line[0:4] in ['SFIX','EFIX','SSAC','SBLI']:
			pass
		else:
			print line

file.close()

samplesFile = open('samples.txt','w')
samplesFile.write('\n'.join(['\t'.join(thisSample) for thisSample in samples]))
samplesFile.close()

messagesFile = open('messages.txt','w')
messagesFile.write('\n'.join(['\t'.join(thisMessage) for thisMessage in messages]))
messagesFile.close()

trialsile = open('trials.txt','w')
trialsile.write('\n'.join(['\t'.join(thisTrial) for thisTrial in trials]))
trialsile.close()

file = open('blinks.txt','w')
file.write('\n'.join(['\t'.join(thisBlink) for thisBlink in blinks]))
file.close()

file = open('saccades.txt','w')
file.write('\n'.join(['\t'.join(thisSaccade) for thisSaccade in saccades]))
file.close()

for line in file.readlines():
	if line[0:3]==