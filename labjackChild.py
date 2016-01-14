# 8@0 9@0 : 138
# 8&1 9&0 : 139
# 8@0 9@1 : 142
# 8&1 9&1 : 143

def labjackChildFunction(
qTo
, qFrom
, windowSize = [200,200]
, windowPosition = [0,0]
):
	import sdl2
	import sdl2.ext
	import sys
	import time
	try:
		import appnope
		appnope.nope()
	except:
		pass

	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	window = sdl2.ext.Window("labjack",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	windowID = sdl2.SDL_GetWindowID(window.window)
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
	window.refresh()

	for i in range(10):
		sdl2.SDL_PumpEvents() #to show the windows

	import u3

	d = u3.U3()
	d.configU3()
	d.getCalibrationData()
	d.configAnalog(u3.FIO0)
	checkForNextZeroTime = False
	checkForTrialNextZeroTime = False

	def exitSafely():
		d.close()
		sys.exit()

	sendTriggers = False
	while True:
		if sendTriggers:
			if not checkForNextZeroTime:
				temp = d.getAIN(0)
				# print temp
				if temp>.5: #photosensor surpasses criterion
					d.getFeedback(u3.BitStateWrite(IONumber=8,State=1))
					nextZeroTime = time.time()+.010 #wait 10ms before setting the state back to zero, giving the amp time to pick it up
					checkForNextZeroTime = True
			else:
				if time.time()>=nextZeroTime: #time to turn the bit back off
					d.getFeedback(u3.BitStateWrite(IONumber=8,State=0))
					checkForNextZeroTime = False
			if checkForTrialNextZeroTime:
				if time.time()>=trialNextZeroTime:
					d.getFeedback(u3.BitStateWrite(IONumber=9,State=0))
					checkForTrialNextZeroTime = False
		if not qTo.empty():
			message = qTo.get()
			if message=='quit':
				exitSafely()
			elif message=='trialDone':
				sendTriggers = False
				checkForTrialNextZeroTime = False
				checkForNextZeroTime = False
				d.getFeedback(u3.BitStateWrite(IONumber=8,State=0)) #should be zero, but just in case...
				d.getFeedback(u3.BitStateWrite(IONumber=9,State=0)) #should be zero, but just in case...
			elif message=='trialStart':
				sendTriggers = True
				d.getFeedback(u3.BitStateWrite(IONumber=9,State=1))
				trialNextZeroTime = time.time()+.010 #wait 10ms before setting the state back to zero, giving the amp time to pick it up
				checkForTrialNextZeroTime = True
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_WINDOWEVENT:
				if (event.window.event==sdl2.SDL_WINDOWEVENT_CLOSE):
					exitSafely()

labjackChildFunction(qTo,qFrom,**initDict)