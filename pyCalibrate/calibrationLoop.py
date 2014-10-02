def loop(qTo,qFrom,timestampMethod,viewingDistance,stimDisplayWidth,stimDisplayRes,stimDisplayPosition,mirrorDisplayPosition,mirrorDownSize,calibrationDotSizeInDegrees,manualCalibrationOrder):
	print stimDisplayPosition
	import numpy #for image and display manipulation
	import scipy.misc #for image and display manipulation
	from PIL import Image #for creating visual stimuli
	import math #for trig and other math stuff
	import sys #for quitting
	import sdl2
	import sdl2.ext
	import random
	import time
	if (timestampMethod==0) or (timestampMethod==1):
		#initialize timer
		sdl2.SDL_Init(sdl2.SDL_INIT_TIMER)
		if timestampMethod==0:
			#define a function to use the high-precision timer, returning a float in seconds
			def getTime():
				return sdl2.SDL_GetPerformanceCounter()*1.0/sdl2.SDL_GetPerformanceFrequency()
			
		elif timestampMethod==1:
			#use the SDL_GetTicks timer
			def getTime():
				return sdl2.SDL_GetTicks()/1000.0	
	elif timestampMethod==2:
		#use time.time()
		import time
		getTime = time.time
	#initialize video
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	sdl2.SDL_SetHint("SDL_HINT_VIDEO_MINIMIZE_ON_FOCUS_LOSS","0")
	mirrorDisplay = sdl2.ext.Window("Mirror", size=(stimDisplayRes[0]/mirrorDownSize,stimDisplayRes[1]/mirrorDownSize),position=mirrorDisplayPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	mirrorDisplaySurf = sdl2.SDL_GetWindowSurface(mirrorDisplay.window)
	mirrorDisplayArray = sdl2.ext.pixels3d(mirrorDisplaySurf.contents)
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	time.sleep(1)
	# stimDisplay = sdl2.ext.Window("Calibration",size=stimDisplayRes,position=stimDisplayPosition,flags=sdl2.SDL_WINDOW_SHOWN|sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP|sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
	stimDisplay = sdl2.ext.Window("Calibration",size=stimDisplayRes,position=stimDisplayPosition,flags=sdl2.SDL_WINDOW_SHOWN|sdl2.SDL_WINDOW_BORDERLESS|sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
	stimDisplaySurf = sdl2.SDL_GetWindowSurface(stimDisplay.window)
	stimDisplayArray = sdl2.ext.pixels3d(stimDisplaySurf.contents)
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	sdl2.SDL_PumpEvents() #to show the windows
	########
	#Perform some calculations to convert stimulus measurements in degrees to pixels
	########
	stimDisplayWidthInDegrees = math.degrees(math.atan((stimDisplayWidth/2.0)/viewingDistance)*2)
	PPD = stimDisplayRes[0]/stimDisplayWidthInDegrees #compute the pixels per degree (PPD)
	calibrationDotSize = int(calibrationDotSizeInDegrees*PPD)
	#initialize font
	sdl2.sdlttf.TTF_Init()
	font = sdl2.sdlttf.TTF_OpenFont('./pytracker/Resources/DejaVuSans.ttf', int(PPD)*2)
	########
	# Define some useful colors for SDL2
	########
	white = sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255)
	black = sdl2.pixels.SDL_Color(r=0, g=0, b=0, a=255)
	grey = sdl2.pixels.SDL_Color(r=127, g=127, b=127, a=255)
	lightGrey = sdl2.pixels.SDL_Color(r=200, g=200, b=200, a=255)
	def drawDot(loc):
		cy,cx = loc
		cx =  stimDisplayRes[1]/2 + cx
		cy =  stimDisplayRes[0]/2 + cy
		radius = calibrationDotSize/2
		y, x = numpy.ogrid[-radius: radius, -radius: radius]
		index = numpy.logical_and( (x**2 + y**2) <= (radius**2) , (x**2 + y**2) >= ((radius/4)**2) )
		stimDisplayArray[ (cy-radius):(cy+radius) , (cx-radius):(cx+radius) , ][index] = [255,255,255,255]
	
	calibrationLocations = dict()
	calibrationLocations['CENTER'] = numpy.array([0,0])
	calibrationLocations['N'] = numpy.array([0,int(0-stimDisplayRes[1]/2.0+calibrationDotSize)])
	calibrationLocations['S'] = numpy.array([0,int(0+stimDisplayRes[1]/2.0-calibrationDotSize)])
	calibrationLocations['E'] = numpy.array([int(0-stimDisplayRes[0]/2.0+calibrationDotSize),0])
	calibrationLocations['W'] = numpy.array([int(0+stimDisplayRes[0]/2.0-calibrationDotSize),0])
	calibrationLocations['NE'] = numpy.array([int(0+stimDisplayRes[0]/2.0-calibrationDotSize),int(0-stimDisplayRes[1]/2.0+calibrationDotSize)])
	calibrationLocations['SE'] = numpy.array([int(0+stimDisplayRes[0]/2.0-calibrationDotSize),int(0+stimDisplayRes[1]/2.0-calibrationDotSize)])
	calibrationLocations['NW'] = numpy.array([int(0-stimDisplayRes[0]/2.0+calibrationDotSize),int(0-stimDisplayRes[1]/2.0+calibrationDotSize)])
	calibrationLocations['SW'] = numpy.array([int(0-stimDisplayRes[0]/2.0+calibrationDotSize),int(0+stimDisplayRes[1]/2.0-calibrationDotSize)])
	calibrationKey = {'q':'NW','w':'N','e':'NE','a':'E','s':'CENTER','d':'W','z':'SW','x':'S','c':'SE'}
	# calibrationLocations['N2'] = numpy.array([0,int((0-stimDisplayRes[1]/2.0+calibrationDotSize)/2.0)])
	# calibrationLocations['S2'] = numpy.array([0,int((0+stimDisplayRes[1]/2.0-calibrationDotSize)/2.0)])
	# calibrationLocations['W2'] = numpy.array([int((0-stimDisplayRes[0]/2.0+calibrationDotSize)/2.0),0])
	# calibrationLocations['E2'] = numpy.array([int((0+stimDisplayRes[0]/2.0-calibrationDotSize)/2.0),0])
	# calibrationLocations['NE2'] = numpy.array([int((0+stimDisplayRes[0]/2.0-calibrationDotSize)/2.0),int((0-stimDisplayRes[1]/2.0+calibrationDotSize)/2.0)])
	# calibrationLocations['SE2'] = numpy.array([int((0+stimDisplayRes[0]/2.0-calibrationDotSize)/2.0),int((0+stimDisplayRes[1]/2.0-calibrationDotSize)/2.0)])
	# calibrationLocations['NW2'] = numpy.array([int((0-stimDisplayRes[0]/2.0+calibrationDotSize)/2.0),int((0-stimDisplayRes[1]/2.0+calibrationDotSize)/2.0)])
	# calibrationLocations['SW2'] = numpy.array([int((0-stimDisplayRes[0]/2.0+calibrationDotSize)/2.0),int((0+stimDisplayRes[1]/2.0-calibrationDotSize)/2.0)])
	
	#define a function that will kill everything safely
	def exitSafely():
		sdl2.ext.quit()
		sys.exit()
	
	def checkInput():
		response = None
		return None

	#define a function that waits for a given duration to pass
	def simpleWait(duration):
		start = getTime()
		while getTime() < (start + duration):
			sdl2.SDL_PumpEvents()
	
	#define a function to draw a numpy array on  surface centered on given coordinates
	def blitArray(src,dst,xOffset=0,yOffset=0):
		x1 = dst.shape[0]/2+xOffset-src.shape[0]/2
		y1 = dst.shape[1]/2+yOffset-src.shape[1]/2
		x2 = x1+src.shape[0]
		y2 = y1+src.shape[1]
		dst[x1:x2,y1:y2,:] = src
	
	def blitSurf(srcSurf,dst,dstSurf,xOffset=0,yOffset=0):
		x = dst.size[0]/2+xOffset-srcSurf.w/2
		y = dst.size[1]/2+yOffset-srcSurf.h/2
		sdl2.SDL_BlitSurface(srcSurf, None, dstSurf, sdl2.SDL_Rect(x,y,srcSurf.w,srcSurf.h))
		sdl2.SDL_UpdateWindowSurface(dst.window) #should this really be here? (will it cause immediate update?)
		# sdl2.SDL_FreeSurface(srcSurf)
	
	#define a function that waits for a response
	def waitForResponse():
		done = False
		while not done:
	 		sdl2.SDL_PumpEvents()
			for event in sdl2.ext.get_events():
				if event.type==sdl2.SDL_KEYDOWN:
					response = sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()
					if response=='escape':
						exitSafely()
					else:
						done = True
		return response
	
	def refreshWindows():
		stimDisplay.refresh()
		image = stimDisplayArray[:,:,0:3]
		image = scipy.misc.imresize(image, (stimDisplayRes[0]/2,stimDisplayRes[1]/2), interp='nearest')
		mirrorDisplayArray[:,:,0:3] = image
		mirrorDisplay.refresh()
		return None
	
	def clearScreen(color):
		sdl2.ext.fill(stimDisplaySurf.contents,color)
	
	def drawText(myText, myFont, textColor,textWidth=.9):
		lineHeight = sdl2.sdlttf.TTF_RenderText_Blended(myFont,'T',textColor).contents.h
		textWidthMax = int(stimDisplay.size[0])
		paragraphs = myText.splitlines()
		renderList = []
		textHeight = 0
		for thisParagraph in paragraphs:
			words = thisParagraph.split(' ')
			if len(words)==1:
				renderList.append(words[0])
				if (thisParagraph!=paragraphs[len(paragraphs)-1]):
					renderList.append(' ')
					textHeight = textHeight + lineHeight
			else:
				thisWordIndex = 0
				while thisWordIndex < (len(words)-1):
					lineStart = thisWordIndex
					lineWidth = 0
					while (thisWordIndex < (len(words)-1)) and (lineWidth <= textWidthMax):
						thisWordIndex = thisWordIndex + 1
						lineWidth = sdl2.sdlttf.TTF_RenderText_Blended(myFont,' '.join(words[lineStart:(thisWordIndex+1)]),textColor).contents.w
					if thisWordIndex < (len(words)-1):
						#last word went over, paragraph continues
						renderList.append(' '.join(words[lineStart:(thisWordIndex-1)]))
						textHeight = textHeight + lineHeight
						thisWordIndex = thisWordIndex-1
					else:
						if lineWidth <= textWidthMax:
							#short final line
							renderList.append(' '.join(words[lineStart:(thisWordIndex+1)]))
							textHeight = textHeight + lineHeight
						else:
							#full line then 1 word final line
							renderList.append(' '.join(words[lineStart:thisWordIndex]))
							textHeight = textHeight + lineHeight
							renderList.append(words[thisWordIndex])
							textHeight = textHeight + lineHeight
						#at end of paragraph, check whether a inter-paragraph space should be added
						if (thisParagraph!=paragraphs[len(paragraphs)-1]):
							renderList.append(' ')
							textHeight = textHeight + lineHeight
		numLines = len(renderList)*1.0
		for thisLine in range(len(renderList)):
			thisRender = sdl2.sdlttf.TTF_RenderText_Blended(myFont,renderList[thisLine],textColor).contents
			x = int(stimDisplay.size[0]/2.0 - thisRender.w/2.0)
			y = int(stimDisplay.size[1]/2.0 - thisRender.h/2.0 + 1.0*thisLine/numLines*textHeight)
			sdl2.SDL_BlitSurface(thisRender, None, stimDisplaySurf, sdl2.SDL_Rect(x,y,thisRender.w,thisRender.h))
			sdl2.SDL_UpdateWindowSurface(stimDisplay.window) #should this really be here? (will it cause immediate update?)
	
	#define a function that prints a message on the stimDisplay while looking for user input to continue. The function returns the total time it waited
	def showMessage(myText,lockWait=False):
		messageViewingTimeStart = getTime()
		clearScreen(black)
		refreshWindows()
		clearScreen(black)
		drawText(myText, font, lightGrey)
		simpleWait(0.500)
		refreshWindows()
		clearScreen(black)
		if lockWait:
			response = None
			while response not in ['return','y','n']:
				response = waitForResponse()
		else:
			response = waitForResponse()
		refreshWindows()
		clearScreen(black)
		simpleWait(0.500)
		messageViewingTime = getTime() - messageViewingTimeStart
		return [response,messageViewingTime]
	

	displayCoords = calibrationLocations[calibrationKey['s']]
	clearScreen(black)
	drawDot(displayCoords)
	refreshWindows()

	done = False
	while not done:
		dotLocation = waitForResponse()
		if dotLocation in calibrationKey:
			print dotLocation
			displayCoords = calibrationLocations[calibrationKey[dotLocation]]
			clearScreen(black)
			drawDot(displayCoords)
			refreshWindows()

	exitSafely()
