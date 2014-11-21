triggerIntervals = [(i+1)/1000.0 for i in range(1000)]
repetitions = 10

# windowSize = [200,200]
# windowPosition = [0,0]
Resolution = 0
ScanFrequency = 2500

# import sdl2
# import sdl2.ext
import struct
import sys
import time
try:
	import appnope
	appnope.nope()
except:
	pass

# sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
# window = sdl2.ext.Window("labjack",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
# windowID = sdl2.SDL_GetWindowID(window.window)
# windowSurf = sdl2.SDL_GetWindowSurface(window.window)
# sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
# window.refresh()

# for i in range(10):
# 	sdl2.SDL_PumpEvents() #to show the windows

import u3
import numpy as np

d = u3.U3()
d.configU3()
d.getCalibrationData()
d.configAnalog(u3.FIO0)
d.streamConfig(NumChannels=1,PChannels=[0],NChannels=[31],Resolution=Resolution,ScanFrequency=ScanFrequency)
d.streamStart()
lastSampleTime = time.time()
interScanInterval = 1.0/ScanFrequency
checkForNextZeroTime = False
checkForTrialNextZeroTime = False

def exitSafely():
	d.streamStop()
	d.close()
	sys.exit()

numBytes = 14 + (d.streamSamplesPerPacket * 2)
print [numBytes,d.packetsPerRequest]
i = 0
j = 0
nextState = 1
nextTriggerTime = time.time()+1
done = False
lastTime = time.time()
while not done:
	now = time.time()
	print now-lastTime
	lastTime = now
	result = d.read(numBytes * d.packetsPerRequest, stream = True)
	if len(result)>0:
		numPackets = len(result) // numBytes
		errors = 0
		missed = 0
		firstPacket = ord(result[10])
		for i in range(numPackets):
			e = ord(result[11+(i*numBytes)])
			if e != 0:
				errors += 1
				if d.debug and e != 60 and e != 59: print e
				if e == 60:
					missed += struct.unpack('<I', result[6+(i*numBytes):10+(i*numBytes)] )[0]
		returnDict = dict(numPackets = numPackets, result = result, errors = errors, missed = missed, firstPacket = firstPacket )		
		returnDict.update(d.processStreamData(result, numBytes = numBytes))
	#for content in d.streamData(convert=True):
	# if time.time()>nextTriggerTime:
	# 	print [i,j,time.time()-nextTriggerTime]
	# 	d.getFeedback(u3.BitStateWrite(IONumber=8,State=nextState))
	# 	nextTriggerTime = time.time()+triggerIntervals[i]
	# 	i = i + 1
	# 	if i==len(triggerIntervals):
	# 		i = 0
	# 		j = j + 1
	# 		if j == repetitions:
	# 			done = True
	# 	nextState = 1-nextState
	# if content is not None:
		# now = time.time()
		# print now-lastTime
		# lastTime = now
		# time.sleep(.4)
		# data = content['AIN0']
		# times = [lastSampleTime + t*interScanInterval for t in range(len(data))]
		# lastSampleTime = times[-1] + interScanInterval
	# sdl2.SDL_PumpEvents()
	# for event in sdl2.ext.get_events():
	# 	if event.type==sdl2.SDL_WINDOWEVENT:
	# 		if (event.window.event==sdl2.SDL_WINDOWEVENT_CLOSE):
	# 			exitSafely()
