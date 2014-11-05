	# class dummyQTo:
	# 	def empty(self):
	# 		return True


	# class dummyQFrom:
	# 	def put(self,message):
	# 		print message


	# qTo = dummyQTo()
	# qFrom = dummyQFrom()

	# windowSize = [200,200]
	# windowPosition = [0,0]
	# stimDisplayRes = [1920,1080]
	# eyelinkIP = '100.1.1.1'
	# edfFileName = 'ssior.edf'
	# edfPath = './_Data/'
	# saccadeSoundFile = '_Stimuli/stop.wav'
	# blinkSoundFile = '_Stimuli/stop.wav'

def eyelinkChildFunction(
qTo
, qFrom
, windowSize = [200,200]
, windowPosition = [0,0]
, stimDisplayRes = [1920,1080]
, eyelinkIP = '100.1.1.1'
, edfFileName = 'temp.edf'
, edfPath = './_Data/'
, saccadeSoundFile = '_Stimuli/stop.wav'
, blinkSoundFile = '_Stimuli/stop.wav'
):
	import sdl2
	import sdl2.ext
	import sdl2.sdlmixer
	import pylink
	import sys
	import shutil
	import time
	try:
		import appnope
		appnope.nope()
	except:
		pass


	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	window = sdl2.ext.Window("eyelink",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	windowID = sdl2.SDL_GetWindowID(window.window)
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
	window.refresh()

	for i in range(10):
		sdl2.SDL_PumpEvents() #to show the windows


	sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
	sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
	class Sound:
		def __init__(self, fileName):
			self.sample = sdl2.sdlmixer.Mix_LoadWAV(sdl2.ext.compat.byteify(fileName, "utf-8"))
			self.started = False
		def play(self):
			self.channel = sdl2.sdlmixer.Mix_PlayChannel(-1, self.sample, 0)
			self.started = True
		def stillPlaying(self):
			if self.started:
				if sdl2.sdlmixer.Mix_Playing(self.channel):
					return True
				else:
					self.started = False
					return False

	saccadeSound = Sound(saccadeSoundFile)
	blinkSound = Sound(blinkSoundFile)

	def exitSafely():
		try:
			eyelink.stopRecording()
			print 'eyelink stopped'
		except:
			pass
		try:
			eyelink.setOfflineMode()
			print 'eyelink offline'
			time.sleep(.1)
			try:
				eyelink.closeDataFile()
				print 'eyelink file closed'
				eyelink.receiveDataFile('temp.edf','temp.edf')
				print 'eyelink file received'
				shutil.move('temp.edf', edfPath)
				print 'eyelink file moved'
			except:
				pass
			eyelink.close()
			print 'eyelink closed'
		except:
			pass
		sys.exit()


	edfPath = './_Data/' #temporary default location, to be changed later when ID is established
	eyelink = pylink.EyeLink(eyelinkIP)
	eyelink.sendCommand('select_parser_configuration 0')# 0--> standard (cognitive); 1--> sensitive (psychophysical)
	eyelink.sendCommand('sample_rate 2000')
	eyelink.setLinkEventFilter("SACCADE,BLINK")
	eyelink.openDataFile(edfFileName)
	eyelink.sendCommand("screen_pixel_coords =  0 0 %d %d" %(stimDisplayRes[0],stimDisplayRes[1]))
	eyelink.sendMessage("DISPLAY_COORDS  0 0 %d %d" %(stimDisplayRes[0],stimDisplayRes[1]))
	eyelink.sendCommand("saccade_velocity_threshold = 60")
	eyelink.sendCommand("saccade_acceleration_threshold = 19500")
	eyelink.doTrackerSetup()
	eyelink.startRecording(1,1,1,1) #this retuns immediately takes 10-30ms to actually kick in on the tracker

	doSounds = False
	while True:
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='escape':
					exitSafely()
		if not qTo.empty():
			message = qTo.get()
			if message=='quit':
				exitSafely()
			elif message[0]=='edfPath':
				edfPath = edfPath
			elif message[0]=='doSounds':
				doSounds = message[1]
			elif message[0]=='sendMessage':
				eyelink.sendMessage(message[1])				
		eyeData = eyelink.getNextData()
		if doSounds:
			if (eyeData==pylink.STARTSACC) or (eyeData==pylink.STARTBLINK):
				eyeEvent = eyelink.getFloatData()
				if isinstance(eyeEvent,pylink.StartSaccadeEvent):
					# print 'Saccade started'
					if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
						saccadeSound.play()
				elif isinstance(eyeEvent,pylink.StartBlinkEvent):
					# print 'Blink started'
					if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
						blinkSound.play()

eyelinkChildFunction(qTo,qFrom,**initDict)