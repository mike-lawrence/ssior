class writerClass:
	def start(self,windowSize=(200,10),windowPosition=(0,0)):
		import billiard
		billiard.forking_enable(0)
		self.qTo = billiard.Queue()
		self.qFrom = billiard.Queue()
		self.process = billiard.Process( target=writerLoop , args=(windowSize,windowPosition,self.qTo,) )
		self.process.start()
		return None
	def quit(self):
		self.qTo.put(['quit'])
		self.process.terminate()
		del self.qTo
		return None

def writerLoop(windowSize,windowPosition,qTo):
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
	window = sdl2.ext.Window("pyWriter",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	windowID = sdl2.SDL_GetWindowID(window.window)
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
	window.refresh()
	done = False
	files = {}
	while not done:
		if not qTo.empty():
			message = qTo.get()
			if message[0]=='quit':
				for index,fileObj in files.items():
					fileObj.close()
				done = True
				break
			elif message[0]=='newFile':
				files[message[1]] = open(message[2],'w')
			elif message[0]=='write':
				files[message[1]].write(message[2]+'\n')
		else:
			time.sleep(1)
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='escape':
					sys.exit()		



