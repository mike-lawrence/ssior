class jackClass:
	def start(self,qToWriter,Resolution=0,ScanFrequency=2500,windowSize=(200,10),windowPosition=(0,0)):
		import billiard
		billiard.forking_enable(0)
		self.qTo = billiard.Queue()
		self.qFrom = billiard.Queue()
		self.process = billiard.Process( target=jackLoop , args=(qToWriter,Resolution,ScanFrequency,windowSize,windowPosition,self.qTo,self.qFrom,) )
		self.process.start()
		return None
	def quit(self):
		self.qTo.put(['quit'])
		self.process.join()
		del self.qTo
		del self.qFrom
		return None


def jackLoop(qToWriter,Resolution,ScanFrequency,windowSize,windowPosition,qTo,qFrom):
	import sdl2
	import sdl2.ext
	import sys
	import time
	import u3
	import numpy as np
	try:
		import appnope
		appnope.nope()
	except:
		pass
	# try: #in case it's still open
	# 	d = u3.U3()
	# 	d.streamStop()
	# 	d.close()
	# except:
	# 	pass
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
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	window = sdl2.ext.Window("pyJack",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	windowID = sdl2.SDL_GetWindowID(window.window)
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
	window.refresh()
	writing = False
	for content in d.streamData():
		if checkForZeroTime:
			if time.time()>=nextZeroTime:
				d.getFeedback(u3.BitStateWrite(IONumber=11,State=0))
		if content is not None:
			data = content['AIN0']
			times = [last + t*interScanInterval for t in range(len(data))]
			last = times[-1] + interScanInterval
			if writing:
				if np.any(np.array(data)>.5):#light exceeds criterion
					d.getFeedback(u3.BitStateWrite(IONumber=11,State=1)) #11@1=s15, 11@0=s11; 9&10@0=r9, 9@0&10@1=r11, 9@1&10@0=r13, 9&10@1=15 
					nextZeroTime = time.time()+1
					# message = {}
					# message['type'] = 'labjack'
					# message['value'] = times[np.where(data>.5)[0]]
					# qFrom.put(message)
				#send data to be written
				qToWriter.put(['write','labjack','\n'.join([ "%0.23f"%times[i] + '\t' + "%0.28f"%data[i] for i in range(len(data)) ])])
		if not qTo.empty():
			message = qTo.get()
			if message[0]=='quit':
				d.streamStop()
				d.close()
				del d
				time.sleep(1)
				sys.exit()		
			elif message[0]=='write':
				qToWriter.put(['newFile','labjack',message[1]])
				writing = True
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='escape':
					d.streamStop()
					d.close()
					del d
					time.sleep(1)
					sys.exit()		

