if __name__=='__main__':
	import time
	import fileForker
	eyelinkChild = fileForker.childClass(childFile='eyelinkChild.py')
	eyelinkChild.initDict['windowSize'] = [100,100]
	eyelinkChild.initDict['windowPosition'] = [0,0]
	eyelinkChild.initDict['stimDisplayRes'] = [1920,1080]
	eyelinkChild.initDict['stimDisplayPosition'] = [1920,0]
	eyelinkChild.initDict['calibrationDotSize'] = 50
	eyelinkChild.initDict['eyelinkIP'] = '100.1.1.1'
	eyelinkChild.initDict['edfFileName'] = 'temp.edf'
	eyelinkChild.initDict['edfPath'] = 'temp.edf'
	eyelinkChild.initDict['saccadeSoundFile'] = '_Stimuli/stop.wav'
	eyelinkChild.initDict['blinkSoundFile'] = '_Stimuli/stop.wav'
	eyelinkChild.start()
	while eyelinkChild.isAlive():
		time.sleep(1)
