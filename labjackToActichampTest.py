triggerIntervals = range(1000)
repetitions = 10

# windowSize = [200,200]
# windowPosition = [0,0]
# Resolution = 0
# ScanFrequency = 2500

# import sdl2
# import sdl2.ext
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
# import numpy as np

d = u3.U3()
d.configU3()
d.getCalibrationData()
# d.configAnalog(u3.FIO0)
# d.streamConfig(NumChannels=1,PChannels=[0],NChannels=[31],Resolution=Resolution,ScanFrequency=ScanFrequency)
# d.streamStart()
# lastSampleTime = time.time()
# interScanInterval = 1.0/ScanFrequency
# checkForNextZeroTime = False
# checkForTrialNextZeroTime = False

def exitSafely():
	d.streamStop()
	d.close()
	sys.exit()

i = 0
j = 0
nextState = 1
nextTriggerTime = time.time()+1
done = False
# for content in d.streamData():
while not done:
	if time.time()>nextTriggerTime:
		d.getFeedback(u3.BitStateWrite(IONumber=8,State=nextState))
		nextTriggerTime = time.time()+triggerIntervals[i]
		i = i + 1
		if i==len(triggerIntervals):
			i = 0
			j = j + 1
			if j = repetitions:
				done = True
		nextState = 1-nextState
	# if content is not None:
	# 	data = content['AIN0']
	# 	times = [lastSampleTime + t*interScanInterval for t in range(len(data))]
	# 	lastSampleTime = times[-1] + interScanInterval
	# sdl2.SDL_PumpEvents()
	# for event in sdl2.ext.get_events():
	# 	if event.type==sdl2.SDL_WINDOWEVENT:
	# 		if (event.window.event==sdl2.SDL_WINDOWEVENT_CLOSE):
	# 			exitSafely()
