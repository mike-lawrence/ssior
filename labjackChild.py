# class dummyQTo:
# 	def empty(self):
# 		return True
# 
# class dummyQFrom:
# 	def put(self,message):
# 		print message
# 
# qTo = dummyQTo()
# qFrom = dummyQFrom()

# windowSize = [200,200]
# windowPosition = [0,0]
# Resolution = 0
# ScanFrequency = 2500
# qToWriter = dummyQTo()

def labjackChildFunction(
qTo
, qFrom
, windowSize = [200,200]
, windowPosition = [0,0]
, Resolution = 0
, ScanFrequency = 2500
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
	import numpy as np
	global d
	d = u3.U3()
	d.configU3()
	d.getCalibrationData()
	d.configAnalog(u3.FIO0)
	d.streamConfig(NumChannels=1,PChannels=[0],NChannels=[31],Resolution=Resolution,ScanFrequency=ScanFrequency)
	d.streamStart()
	startTime = time.time()
	last = startTime
	interScanInterval = 1.0/ScanFrequency
	checkForZeroTime = False

	print 'labjack OK!'

	# def exitSafely():
	# 	d.streamStop()
	# 	d.close()
	# 	del d
	# 	time.sleep(1)
	# 	sys.exit()

	sendTriggers = False
	for content in d.streamData():
		if sendTriggers and checkForZeroTime:
			if time.time()>=nextZeroTime:
				d.getFeedback(u3.BitStateWrite(IONumber=11,State=0))
				checkForZeroTime = False
		if content is not None:
			data = content['AIN0']
			times = [last + t*interScanInterval for t in range(len(data))]
			last = times[-1] + interScanInterval
			if sendTriggers and not checkForZeroTime:
				if np.any(np.array(data)>1):#light exceeds criterion
					d.getFeedback(u3.BitStateWrite(IONumber=11,State=1)) #11@1=s15, 11@0=s11; 9&10@0=r9, 9@0&10@1=r11, 9@1&10@0=r13, 9&10@1=15 
					nextZeroTime = time.time()+1
					checkForZeroTime = True
				# qToWriter.put(['write','labjack','\n'.join([ "%0.23f"%times[i] + '\t' + "%0.28f"%data[i] for i in range(len(data)) ])])
		if not qTo.empty():
			message = qTo.get()
			if message[0]=='quit':
				# exitSafely()
				d.streamStop()
				d.close()
				del d
				time.sleep(1)
				sys.exit()
			elif message[0]=='sendTriggers':
				# qToWriter.put(['newFile','labjack',message[1]])
				sendTriggers = True
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='escape':
					# exitSafely()		
					d.streamStop()
					d.close()
					del d
					time.sleep(1)
					sys.exit()

labjackChildFunction(qTo,qFrom,**initDict)