if __name__ == '__main__':
	########
	#Important parameters
	########

	viewingDistance = 57.0 #units can be anything so long as they match those used in stimDisplayWidth below
	stimDisplayWidth = 54.5 #units can be anything so long as they match those used in viewingDistance above
	stimDisplayRes = (1920,1080) #pixel resolution of the stimDisplay
	stimDisplayPositionX = 2560
	dualDisplay = True

	writerWindowSize = (200,200)
	writerWindowPosition = (300,0)

	stamperWindowSize = (200,200)
	stamperWindowPosition = (0,0)
	stamperWindowColor = [255,255,255]
	stamperDoBorder = True

	doLabjack = True
	labjackWindowSize = (200,200)
	labjackWindowPosition = (500,0)
	labjackResolution = 0 #0 is highest precision
	labjackScanFrequency = 2500 #Hz

	doEyelink = False
	eyelinkWindowSize = (200,200)
	eyelinkWindowPosition = (700,0)
	eyelinkIP = '100.1.1.1'
	saccadeSoundFile = '_Stimuli/stop.wav'
	blinkSoundFile = '_Stimuli/stop.wav'
	calibrationDotSizeInDegrees = 1
	calibrationMirrorDisplayPosition = [0,0]
	calibrationMirrorDownsize = 2

	responseModality = 'trigger' # 'key' or 'trigger'
	triggerLeftAxis = 2
	triggerRightAxis = 5
	triggerCriterionValue = -(2**16/4) #16 bit precision on the triggers, split above/below 0

	brightSideList = ['left','right']
	fastSideList = ['left','right']
	cueSideList = ['left','right']
	targetSideList = ['left','right']
	targetIdentityList = ['square','diamond']

	#times are specified in frames @ 60Hz
	fixationDurationMin = 60 #1s
	fixationDurationMax = 120 #2s
	cueDuration = 6 #100ms
	cueCuebackSOA = 30 #500ms
	cuebackDuration = 6 #100ms
	cuebackTargetSOA = 60 #1s
	responseTimeout = 60 #1s

	feedbackDuration = 1.000 #specified in seconds

	slowCycleHalfFrames = 3 #half the cycle length
	fastCycleHalfFrames = 2 #half the cycle length

	numberOfBlocks = 10 
	trialsPerBlock = 32

	instructionSizeInDegrees = 1 
	feedbackSizeInDegrees = 1

	fixationSizeInDegrees = .25
	offsetSizeInDegrees = 13
	targetSizeInDegrees = 3
	targetThicknessProportion = .8
	flickerSizeInDegrees = 1

	textWidth = .9 #specify the proportion of the stimDisplay to use when drawing instructions


	########
	# Import libraries
	########
	import sdl2 #for input and display
	import sdl2.ext #for input and display
	import numpy #for image and display manipulation
	import scipy.misc #for resizing numpy images via scipy.misc.imresize
	from PIL import Image #for image manipulation
	from PIL import ImageFont
	from PIL import ImageOps
	#import aggdraw #for drawing
	import math #for rounding
	import sys #for quitting
	import os
	import random #for shuffling and random sampling
	import time #for timing
	import shutil #for copying files
	import hashlib #for encrypting
	import OpenGL.GL as gl
	try:
		os.nice(-20)
	except:
		pass#print('Can\'t nice')
	try:
		import appnope
		appnope.nope()
	except:
		pass
	import pyProcess


	########
	# Define a custom time function using the same clock as that which generates the SDL2 event timestamps
	########

	#define a function that gets the time (unit=seconds,zero=?)
	def getTime():
		return sdl2.SDL_GetPerformanceCounter()*1.0/sdl2.SDL_GetPerformanceFrequency()


	########
	# Initialize the timer and random seed
	########
	sdl2.SDL_Init(sdl2.SDL_INIT_TIMER)
	seed = getTime() #grab the time of the timer initialization to use as a seed
	random.seed(seed) #use the time to set the random seed


	########
	#Perform some calculations to convert stimulus measurements in degrees to pixels
	########
	stimDisplayWidthInDegrees = math.degrees(math.atan((stimDisplayWidth/2.0)/viewingDistance)*2)
	PPD = stimDisplayRes[0]/stimDisplayWidthInDegrees #compute the pixels per degree (PPD)

	calibrationDotSize = int(calibrationDotSizeInDegrees*PPD)
	instructionSize = int(instructionSizeInDegrees*PPD)
	feedbackSize = int(feedbackSizeInDegrees*PPD)
	fixationSize = int(fixationSizeInDegrees*PPD)
	offsetSize = int(offsetSizeInDegrees*PPD)
	targetSize = int(targetSizeInDegrees*PPD)
	targetThickness = int(targetSizeInDegrees*PPD*targetThicknessProportion)
	flickerSize = int(flickerSizeInDegrees*PPD)


	########
	# Initialize fonts
	########
	feedbackFontSize = 2
	feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
	feedbackHeight = feedbackFont.getsize('XXX')[1]
	while feedbackHeight<feedbackSize:
		feedbackFontSize = feedbackFontSize + 1
		feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
		feedbackHeight = feedbackFont.getsize('XXX')[1]

	feedbackFontSize = feedbackFontSize - 1
	feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
	
	instructionFontSize = 2
	instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
	instructionHeight = instructionFont.getsize('XXX')[1]
	while instructionHeight<instructionSize:
		instructionFontSize = instructionFontSize + 1
		instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
		instructionHeight = instructionFont.getsize('XXX')[1]

	instructionFontSize = instructionFontSize - 1
	instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)


	########
	# Initialize the writer
	########
	writerProcess = pyProcess.processClass(fileToRun='writerProcess.py')
	writerProcess.initVars['windowSize'] = writerWindowSize
	writerProcess.initVars['windowPosition'] = writerWindowPosition
	writerProcess.start()

	########
	# start the event timestamper
	########
	stamperProcess = pyProcess.processClass(fileToRun='stamperProcess.py')
	stamperProcess.initVars['windowSize'] = stamperWindowSize
	stamperProcess.initVars['windowPosition'] = stamperWindowPosition
	stamperProcess.initVars['windowColor'] = stamperWindowColor
	stamperProcess.initVars['doBorder'] = stamperDoBorder
	stamperProcess.start()

	########
	# start the labjack
	########
	if doLabjack:
		labjackProcess = pyProcess.processClass(fileToRun='labjackProcess.py')
		labjackProcess.initVars['windowSize'] = labjackWindowSize
		labjackProcess.initVars['windowPosition'] = labjackWindowPosition
		labjackProcess.initVars['Resolution'] = labjackResolution
		labjackProcess.initVars['ScanFrequency'] = labjackScanFrequency
		labjackProcess.initVars['qToWriter'] = writerProcess.qTo
		labjackProcess.start()

	########
	# initialize the eyelink
	########
	if doEyelink:
		eyelinkProcess = pyProcess.processClass(fileToRun='eyelinkProcess.py')
		eyelinkProcess.initVars['windowSize'] = eyelinkWindowSize
		eyelinkProcess.initVars['windowPosition'] = eyelinkWindowPosition
		eyelinkProcess.initVars['stimDisplayRes'] = stimDisplayRes
		eyelinkProcess.initVars['eyelinkIP'] = eyelinkIP
		eyelinkProcess.initVars['edfFileName'] = edfFileName
		eyelinkProcess.initVars['edfPath'] = edfPath
		eyelinkProcess.initVars['saccadeSoundFile'] = saccadeSoundFile
		eyelinkProcess.initVars['blinkSoundFile'] = blinkSoundFile
		eyelinkProcess.start()
		calibrationProcess = pyProcess.processClass(fileToRun='calibrationProcess.py')
		calibrationProcess.initVars['calibrationDotSize'] = calibrationDotSize
		calibrationProcess.initVars['fontSize'] = instructionFontSize
		calibrationProcess.initVars['stimDisplayRes'] = stimDisplayRes
		calibrationProcess.initVars['stimDisplayPosition'] = stimDisplayPosition
		calibrationProcess.initVars['mirrorDisplayPosition'] = calibrationMirrorDisplayPosition
		calibrationProcess.initVars['mirrorDownSize'] = calibrationMirrorDownsize
		calibrationProcess.start()
		while calibrationProcess.isAlive():
			pass

	########
	# Initialize the stimDisplay
	########
	time.sleep(5)
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	stimDisplay = sdl2.ext.Window("Experiment", size=stimDisplayRes,position=(stimDisplayPositionX,0),flags=sdl2.SDL_WINDOW_OPENGL|sdl2.SDL_WINDOW_SHOWN| sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP |sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
	glContext = sdl2.SDL_GL_CreateContext(stimDisplay.window)
	gl.glMatrixMode(gl.GL_PROJECTION)
	gl.glLoadIdentity()
	gl.glOrtho(0, stimDisplayRes[0],stimDisplayRes[1], 0, 0, 1)
	gl.glMatrixMode(gl.GL_MODELVIEW)
	gl.glDisable(gl.GL_DEPTH_TEST)

	if not dualDisplay:
		sdl2.mouse.SDL_ShowCursor(0)

	# 	if dualDisplay:
	# 		mirrorDisplay = sdl2.ext.Window("Preview", size=(stimDisplayRes[0]/2,stimDisplayRes[1]/2),position=(0,0),flags=sdl2.SDL_WINDOW_SHOWN)
	# 		mirrorDisplaySurf = sdl2.SDL_GetWindowSurface(mirrorDisplay.window)
	# 		mirrorDisplayArray = sdl2.ext.pixels3d(mirrorDisplaySurf.contents)

	for i in range(10):
		sdl2.SDL_PumpEvents() #to show the windows


	########
	# Drawing functions
	########

	def text2numpy(myText,myFont,fg=[255,255,255,255],bg=[0,0,0,0]):
		glyph = myFont.getmask(myText,mode='L')
		a = numpy.asarray(glyph)#,dtype=numpy.uint8)
		b = numpy.reshape(a,(glyph.size[1],glyph.size[0]),order='C')
		c = numpy.zeros((glyph.size[1],glyph.size[0],4))#,dtype=numpy.uint8)
		# c[:,:,0][b>0] = b[b>0]
		# c[:,:,1][b>0] = b[b>0]
		# c[:,:,2][b>0] = b[b>0]
		# c[:,:,3][b>0] = b[b>0]
		c[:,:,0][b>0] = fg[0]*b[b>0]/255.0
		c[:,:,1][b>0] = fg[1]*b[b>0]/255.0
		c[:,:,2][b>0] = fg[2]*b[b>0]/255.0
		c[:,:,3][b>0] = fg[3]*b[b>0]/255.0
		c[:,:,0][b==0] = bg[0]
		c[:,:,1][b==0] = bg[1]
		c[:,:,2][b==0] = bg[2]
		c[:,:,3][b==0] = bg[3]
		return c.astype(dtype=numpy.uint8)


	def blitNumpy(numpyArray,xLoc,yLoc,xCentered=True,yCentered=True):
		gl.glEnable(gl.GL_BLEND)
		gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
		ID = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
		gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE);
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
		gl.glTexImage2D( gl.GL_TEXTURE_2D , 0 , gl.GL_RGBA , numpyArray.shape[1] , numpyArray.shape[0] , 0 , gl.GL_RGBA , gl.GL_UNSIGNED_BYTE , numpyArray )
		gl.glEnable(gl.GL_TEXTURE_2D)
		gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
		gl.glBegin(gl.GL_QUADS)
		x1 = xLoc + 1.5 - 0.5
		x2 = xLoc + numpyArray.shape[1] - 0.0 + 0.5
		y1 = yLoc + 1.0 - 0.5
		y2 = yLoc + numpyArray.shape[0] - 0.5 + 0.5
		if xCentered:
			x1 = x1 - numpyArray.shape[1]/2.0
			x2 = x2 - numpyArray.shape[1]/2.0
		if yCentered:
			y1 = y1 - numpyArray.shape[0]/2.0
			y2 = y2 - numpyArray.shape[0]/2.0
		gl.glTexCoord2f( 0 , 0 )
		gl.glVertex2f( x1 , y1 )
		gl.glTexCoord2f( 1 , 0 )
		gl.glVertex2f( x2 , y1 )
		gl.glTexCoord2f( 1 , 1)
		gl.glVertex2f( x2 , y2 )
		gl.glTexCoord2f( 0 , 1 )
		gl.glVertex2f( x1, y2 )
		gl.glEnd()
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		gl.glDeleteTextures([ID])
		del ID
		gl.glDisable(gl.GL_TEXTURE_2D)
		return None


	def drawText( myText , myFont , textWidth , xLoc , yLoc , fg=[255,255,255,255] , bg=[0,0,0,0] , xCentered=True , yCentered=True , lineSpacing=1.2):
		lineHeight = myFont.getsize('Tj')[0]*lineSpacing
		paragraphs = myText.splitlines()
		renderList = []
		for thisParagraph in paragraphs:
			words = thisParagraph.split(' ')
			if len(words)==1:
				renderList.append(words[0])
				if (thisParagraph!=paragraphs[len(paragraphs)-1]):
					renderList.append(' ')
			else:
				thisWordIndex = 0
				while thisWordIndex < (len(words)-1):
					lineStart = thisWordIndex
					lineWidth = 0
					while (thisWordIndex < (len(words)-1)) and (lineWidth <= textWidth):
						thisWordIndex = thisWordIndex + 1
						lineWidth = myFont.getsize(' '.join(words[lineStart:(thisWordIndex+1)]))[0]
					if thisWordIndex < (len(words)-1):
						#last word went over, paragraph continues
						renderList.append(' '.join(words[lineStart:(thisWordIndex-1)]))
						thisWordIndex = thisWordIndex-1
					else:
						if lineWidth <= textWidth:
							#short final line
							renderList.append(' '.join(words[lineStart:(thisWordIndex+1)]))
						else:
							#full line then 1 word final line
							renderList.append(' '.join(words[lineStart:thisWordIndex]))
							renderList.append(words[thisWordIndex])
						#at end of paragraph, check whether a inter-paragraph space should be added
						if (thisParagraph!=paragraphs[len(paragraphs)-1]):
							renderList.append(' ')
		# print renderList
		numLines = len(renderList)
		for thisLineNum in range(numLines):
			if renderList[thisLineNum]==' ':
				pass
			else:
				thisRender = text2numpy( renderList[thisLineNum] , myFont , fg=fg , bg=bg )
				if xCentered:
					x = xLoc - thisRender.shape[1]/2.0
				else:
					x = xLoc
				if yCentered:
					y = yLoc - numLines*lineHeight/2.0 + thisLineNum*lineHeight
				else:
					y = yLoc + thisLineNum*lineHeight
				blitNumpy(numpyArray=thisRender,xLoc=x,yLoc=y,xCentered=False,yCentered=False)
		return None


	def drawBoxes(brightSide):
		if brightSide=='left':
			leftColor = 1
		else:
			leftColor = 0
		gl.glColor3f(leftColor,leftColor,leftColor)
		gl.glBegin(gl.GL_POLYGON)
		gl.glVertex2f(0,0)
		gl.glVertex2f(0,stimDisplayRes[1])
		gl.glVertex2f(stimDisplayRes[0]/2,stimDisplayRes[1])
		gl.glVertex2f(stimDisplayRes[0]/2,0)
		gl.glEnd()
		gl.glColor3f(1-leftColor,1-leftColor,1-leftColor)
		gl.glBegin(gl.GL_POLYGON)
		gl.glVertex2f(stimDisplayRes[0]/2,0)
		gl.glVertex2f(stimDisplayRes[0]/2,stimDisplayRes[1])
		gl.glVertex2f(stimDisplayRes[0],stimDisplayRes[1])
		gl.glVertex2f(stimDisplayRes[0],0)
		gl.glEnd()


	# def drawFixationStim(x,y,radius):
	# 	thisDegree = 0
	# 	for i in range(12):
	# 		thisDegree = i*30
	# 		if i%2==1:
	# 			gl.glColor3f(1,1,1)
	# 		else:
	# 			gl.glColor3f(0,0,0)
	# 		gl.glBegin(gl.GL_POLYGON)
	# 		gl.glVertex2f(x,y)
	# 		for j in range(30):
	# 			thisDegree = thisDegree+1
	# 			gl.glVertex2f( x + math.sin(thisDegree*math.pi/180)*radius , y + math.cos(thisDegree*math.pi/180)*radius )
	# 		gl.glEnd()


	def drawDot(size,xOffset=0):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*size , stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*size)
		gl.glEnd()


	def drawRing(xOffset,outer,inner):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_QUAD_STRIP)
		for i in range(360):
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*outer)
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*inner)
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*outer)
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*inner)
		gl.glEnd()


	def drawSquare(xOffset,outer,inner):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer/2 , stimDisplayRes[1]/2-outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner/2 , stimDisplayRes[1]/2-inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+outer/2 , stimDisplayRes[1]/2-outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+inner/2 , stimDisplayRes[1]/2-inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+outer/2 , stimDisplayRes[1]/2+outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+inner/2 , stimDisplayRes[1]/2+inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer/2 , stimDisplayRes[1]/2+outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner/2 , stimDisplayRes[1]/2+inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer/2 , stimDisplayRes[1]/2-outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner/2 , stimDisplayRes[1]/2-inner/2 )
		gl.glEnd()


	def drawDiamond(xOffset,outer,inner):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_QUAD_STRIP)
		outer = math.sqrt((outer**2)*2)/2
		inner = math.sqrt((inner**2)*2)/2
		yOffset = stimDisplayRes[1]/2
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset-outer )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset-inner )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+outer , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+inner , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset+outer )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset+inner )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner , yOffset )
		gl.glEnd()

	
	def setPhotoTrigger(on=False):
		if on:
			gl.glColor3f(1,1,1)
		else:
			gl.glColor3f(0,0,0)
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/30 , stimDisplayRes[1] )
		gl.glVertex2f( stimDisplayRes[0]/2 + stimDisplayRes[0]/30 , stimDisplayRes[1] )
		gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/30 , stimDisplayRes[1] - stimDisplayRes[1]/20 )
		gl.glVertex2f( stimDisplayRes[0]/2 + stimDisplayRes[0]/30 , stimDisplayRes[1] - stimDisplayRes[1]/20 )
		gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/30 , stimDisplayRes[1] )
		gl.glEnd()
		gl.glColor3f(0,0,0)
		# gl.glBegin(gl.GL_QUAD_STRIP)
		# gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/10 , stimDisplayRes[1] )
		# gl.glVertex2f( stimDisplayRes[0]/2 + stimDisplayRes[0]/10 , stimDisplayRes[1] )
		# gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/10 , stimDisplayRes[1] - stimDisplayRes[1]/10 )
		# gl.glVertex2f( stimDisplayRes[0]/2 + stimDisplayRes[0]/10 , stimDisplayRes[1] - stimDisplayRes[1]/10 )
		# gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/10 , stimDisplayRes[1] )
		# gl.glEnd()
		# if on:
		# 	gl.glColor3f(1,1,1)
		# 	gl.glBegin(gl.GL_QUAD_STRIP)
		# 	gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/10 , stimDisplayRes[1] )
		# 	gl.glVertex2f( stimDisplayRes[0]/2 + stimDisplayRes[0]/10 , stimDisplayRes[1] )
		# 	gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/10 , stimDisplayRes[1] - stimDisplayRes[1]/10 )
		# 	gl.glVertex2f( stimDisplayRes[0]/2 + stimDisplayRes[0]/10 , stimDisplayRes[1] - stimDisplayRes[1]/10 )
		# 	gl.glVertex2f( stimDisplayRes[0]/2 - stimDisplayRes[0]/10 , stimDisplayRes[1] )
		# 	gl.glEnd()


	########
	# Helper functions
	########

	#define a function that waits for a given duration to pass
	def simpleWait(duration):
		start = getTime()
		while getTime() < (start + duration):
			pass


	#define a function that will kill everything safely
	def exitSafely():
		if doEyelink:
			eyelinkProcess.stop(killAfter=60)
		stamperProcess.stop(killAfter=60)
		labjackProcess.stop(killAfter=60)
		writerProcess.stop(killAfter=60)
		sdl2.ext.quit()
		time.sleep(5)
		sys.exit()


	#define a function that waits for a response
	def waitForResponse():
		done = False
		while not done:
			if not stamperProcess.qFrom.empty():
				event = stamperProcess.qFrom.get()
				if event['type']=='key':
					response = event['value']
					if response=='escape':
						exitSafely()
					else:
						done = True
				elif event['type'] == 'axis':
					response = event['axis']
					if event['value']>triggerCriterionValue:
						done = True
		return response


	def refreshWindows():
		sdl2.SDL_GL_SwapWindow(stimDisplay.window)
		# if dualDisplay:
		# 	image = stimDisplayArray[:,:,0:3]
		# 	image = scipy.misc.imresize(image, (stimDisplayRes[0]/2,stimDisplayRes[1]/2), interp='nearest')
		# 	mirrorDisplayArray[:,:,0:3] = image
		# 	mirrorDisplay.refresh()
		return None


	#define a function that prints a message on the stimDisplay while looking for user input to continue. The function returns the total time it waited
	def showMessage(myText):
		messageViewingTimeStart = getTime()
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		refreshWindows()
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		simpleWait(0.500)
		refreshWindows()
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		waitForResponse()
		stimDisplay.refresh()
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		simpleWait(0.500)
		messageViewingTime = getTime() - messageViewingTimeStart
		return messageViewingTime


	#define a function that requests user input
	def getInput(getWhat):
		getWhat = getWhat
		textInput = ''
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		refreshWindows()
		simpleWait(0.500)
		myText = getWhat+textInput
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		refreshWindows()
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		done = False
		while not done:
			if not stamperProcess.qFrom.empty():
				event = stamperProcess.qFrom.get()
				if event['type'] == 'key' :
					response = event['value']
					if response=='escape':
						exitSafely()
					elif response == 'backspace':
						if textInput!='':
							textInput = textInput[0:(len(textInput)-1)]
							myText = getWhat+textInput
							gl.glClearColor(0,0,0,1)
							gl.glClear(gl.GL_COLOR_BUFFER_BIT)
							drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
							refreshWindows()
					elif response == 'return':
						done = True
					else:
						textInput = textInput + response
						myText = getWhat+textInput
						gl.glClearColor(0,0,0,1)
						gl.glClear(gl.GL_COLOR_BUFFER_BIT)
						drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
						refreshWindows()
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		refreshWindows()
		return textInput


	#define a function that obtains subject info via user input
	def getSubInfo():
		year = time.strftime('%Y')
		month = time.strftime('%m')
		day = time.strftime('%d')
		hour = time.strftime('%H')
		minute = time.strftime('%M')
		sid = getInput('ID (\'test\' to demo): ')
		if sid != 'test':
			sex = getInput('Sex (m or f): ')
			age = getInput('Age (2-digit number): ')
			handedness = getInput('Handedness (r or l): ')
			password = getInput('Please enter a password (ex. B00): ')
		else:
			sex = 'test'
			age = 'test'
			handedness = 'test'
			password = 'test'
		password = hashlib.sha512(password).hexdigest()
		subInfo = [ sid , year , month , day , hour , minute , sex , age , handedness , password ]
		return subInfo


	#define a function that generates a randomized list of trial-by-trial stimulus information representing a factorial combination of the independent variables.
	def getTrials():
		trials=[]
		for brightSide in brightSideList:
			for fastSide in fastSideList:
				for cueSide in cueSideList:
					for targetSide in targetSideList:
						for targetIdentity in targetIdentityList:
							trials.append([brightSide,fastSide,cueSide,targetSide,targetIdentity])
		random.shuffle(trials)
		return trials


	def checkInput(triggerData=None):
		if triggerData==None:
			triggerData = [[],[]]
			lastLeftTrigger = -(2**16/2)
			lastRightTrigger = -(2**16/2)
		else:
			if len(triggerData[0])<1:
				lastLeftTrigger = -(2**16/2)
			else:
				lastLeftTrigger = triggerData[0][-1][-1]
			if len(triggerData[1])<1:
				lastRightTrigger = -(2**16/2)
			else:
				lastRightTrigger = triggerData[1][-1][-1]
		responseMade = False
		rts = [[],[]]
		while not stamperProcess.qFrom.empty():
			event = stamperProcess.qFrom.get()
			if event['type'] == 'key' :
				if event['value']=='escape':
					exitSafely()
				else:
					responseMade = True
					rts[0].append(event['time'])
					rts[1].append(event['time'])
			if event['type'] == 'axis':
				if event['axis']==triggerLeftAxis:
					triggerData[0].append([event['time'],event['value']])
					if event['value']>=triggerCriterionValue:
						if lastLeftTrigger<triggerCriterionValue:
							responseMade = True
							rts[0].append(event['time'])
				elif event['axis']==triggerRightAxis:
					triggerData[1].append([event['time'],event['value']])
					if event['value']>=triggerCriterionValue:
						if lastRightTrigger<triggerCriterionValue:
							responseMade = True
							rts[1].append(event['time'])
		return [responseMade,rts,triggerData]


	#define a function that runs a block of trials
	def runBlock():
		start = time.time()
		while (time.time()-start)<1:
			checkInput()
		
		print 'block started'

		#get trials
		trialList = getTrials()	

		#run the trials
		trialNum = 0
		while trialNum<trialsPerBlock:
			# if doEyelink:
			# 	try:
			# 		error = eyelink.doDriftCorrect(stimDisplayRes[0]/2, stimDisplayRes[1]/2, 1, 1)
			# 		if error!=0:
			# 			eyelink.doTrackerSetup()
			# 	except:
			# 		eyelink.doTrackerSetup()

			if doEyelink:
				eyelink.startRecording(1,1,1,1) #this retuns immediately takes 10-30ms to actually kick in on the tracker

			# printList = []

			#bump the trial number
			trialNum = trialNum + 1
		
			#get the trial info
			trialInfo = random.choice(trialList)

			#parse the trial info
			brightSide,fastSide,cueSide,targetSide,targetIdentity = trialInfo
			
			#generate fixation duration
			fixationDuration = int(random.uniform(fixationDurationMin,fixationDurationMax))

			#prep and show the buffers
			drawBoxes(brightSide)
			drawDot(fixationSize)
			setPhotoTrigger()
			refreshWindows()
			drawBoxes(brightSide)
			drawDot(fixationSize)
			setPhotoTrigger()
			refreshWindows() #this one should block until it's actually displayed

			#get the trial start time 
			trialStartTime = getTime()
			lastFrameTime = trialStartTime
			
			#compute event times
			cueOnFrame = 0+fixationDuration
			cueOffFrame = cueOnFrame + cueDuration
			cuebackOnFrame = cueOnFrame + cueCuebackSOA
			cuebackOffFrame = cuebackOnFrame + cuebackDuration
			targetOnFrame = cuebackOnFrame + cuebackTargetSOA
			targetOffFrame = targetOnFrame + responseTimeout

			sendFastOnMessage = False
			sendFastOffMessage = False
			sendSlowOnMessage = False
			sendSlowOffMessage = False
			sendCueOnMessage = False
			sendCueOffMessage = False
			sendCuebackOnMessage = False
			sendCuebackOffMessage = False
			sendTargetOnMessage = False

			fastOnMessageSent = False
			fastOffMessageSent = False
			slowOnMessageSent = False
			slowOffMessageSent = False
			cueOnMessageSent = False
			cueOffMessageSent = False
			cuebackOnMessageSent = False
			cuebackOffMessageSent = False
			targetOnMessageSent = False
			setPhotoTriggerOn = False

			#initialize variables to write
			saccadeStartTimes = []
			saccadeStartTimes2 = []
			saccadeEndTimes = []
			saccadeEndTimes2 = []
			blinkStartTimes = []
			blinkStartTimes2 = []
			blinkEndTimes = []
			blinkEndTimes2 = []
			saccadeLocations = []
			blinkMade = False
			sacadeMade = False

			blink = False
			saccadeMade = False
			# trialAppended = False

			#create some variables
			preTargetResponse = 'FALSE'
			feedbackResponse = 'FALSE'
			response = 'NA'
			rt = 'NA'
			error = 'NA'

			#loop through time
			trialDone = False
			frameNum = -1
			while not trialDone:
				frameNum = frameNum + 1
				frameText = ''
				drawBoxes(brightSide)
				drawDot(fixationSize)
				#check if it's time to deal with the cue
				if frameNum>=cueOnFrame:
					if frameNum<cueOffFrame:
						# frameText = frameText + ' cueOn'
						if not cueOnMessageSent:
							sendCueOnMessage = True
							setPhotoTriggerOn = True
						if cueSide=='left':
							drawRing(-offsetSize,targetSize,targetSize*targetThicknessProportion)
						else:
							drawRing(offsetSize,targetSize,targetSize*targetThicknessProportion)
					else:#frame>=cueOffFrame
						# frameText = frameText + ' cueOff'
						if not cueOffMessageSent:
							sendCueOffMessage = True
						#check if it's time to deal with the cueback
						if frameNum>=cuebackOnFrame:
							if frameNum<cuebackOffFrame:
								# frameText = frameText + ' cueBackOn'
								if not cuebackOnMessageSent:
									sendCuebackOnMessage = True
								drawDot(fixationSize*2)
							else: #frame>=cueBackOffFrame
								# frameText = frameText + ' cueBackOff'
								if not cuebackOffMessageSent:
									sendCuebackOffMessage = True
								#check if it's time to deal with the target
								if frameNum>=targetOnFrame:
									if frameNum<targetOffFrame:
										# frameText = frameText + ' targetOn'
										if not targetOnMessageSent:
											sendTargetOnMessage = True
										if targetSide=='left':
											if targetIdentity=='square':
												drawSquare(-offsetSize,targetSize,targetSize*targetThicknessProportion)
											else:
												drawDiamond(-offsetSize,targetSize,targetSize*targetThicknessProportion)
										else:
											if targetIdentity=='square':
												drawSquare(offsetSize,targetSize,targetSize*targetThicknessProportion)
											else:
												drawDiamond(offsetSize,targetSize,targetSize*targetThicknessProportion)
									else:
										trialDone = True
				#check whether to draw the faster flicker
				if (frameNum%(fastCycleHalfFrames*2))<fastCycleHalfFrames:
					# frameText = frameText + ' fastOn'
					if fastSide=='left':
						drawDot(flickerSize,-offsetSize)
					else:
						drawDot(flickerSize,offsetSize)
					if not fastOnMessageSent:
						sendFastOnMessage = True
				else:
					# frameText = frameText + ' fastOff'
					if not fastOffMessageSent:
						sendFastOffMessage = True
				#check whether to draw the slower flicker
				if (frameNum%(slowCycleHalfFrames*2))<slowCycleHalfFrames:
					# frameText = frameText + ' slowOn'
					if fastSide!='left':
						drawDot(flickerSize,-offsetSize)
					else:
						drawDot(flickerSize,offsetSize)
					if not slowOnMessageSent:
						sendSlowOnMessage = True
				else:
					# frameText = frameText + ' slowOff'
					if not slowOffMessageSent:
						sendSlowOffMessage = True
				if setPhotoTriggerOn:
					setPhotoTrigger(on=True)
					setPhotoTriggerOn = False
				else:
					setPhotoTrigger()
				#done drawing
				refreshWindows() #show this frame (should block until shown (if we haven't missed a frame!))
				frameTime = getTime() #get the time of this frame (refresh should have blocked)
				lastFrameTime = frameTime
				if sendFastOnMessage:
					#queueFromExpToEEG.put([frameTime,'fast on'])
					sendFastOnMessage = False
					fastOnMessageSent = True
					fastOffMessageSent = False
				if sendFastOffMessage:
					#queueFromExpToEEG.put([frameTime,'fast off'])
					sendFastOffMessage = False
					fastOffMessageSent = True
					fastOnMessageSent = False
				if sendSlowOnMessage:
					#queueFromExpToEEG.put([frameTime,'slow on'])
					sendSlowOnMessage = False
					slowOnMessageSent = True
					slowOffMessageSent = False
				if sendSlowOffMessage:
					#queueFromExpToEEG.put([frameTime,'slow off'])
					sendSlowOffMessage = False
					slowOffMessageSent = True
					slowOnMessageSent = False
				if sendCueOnMessage:
					if doEyelink:
						eyelink.sendMessage('CUE ON')
					#queueFromExpToEEG.put([frameTime,'cue on'])
					sendCueOnMessage = False
					cueOnMessageSent = True
				if sendCueOffMessage:
					#queueFromExpToEEG.put([frameTime,'cue off'])
					sendCueOffMessage = False
					cueOffMessageSent = True
				if sendCuebackOnMessage:
					#queueFromExpToEEG.put([frameTime,'cueback on'])
					sendCuebackOnMessage = False
					cuebackOnMessageSent = True
				if sendCuebackOffMessage:
					#queueFromExpToEEG.put([frameTime,'cueback off'])
					sendCuebackOffMessage = False
					cuebackOffMessageSent = True
				if sendTargetOnMessage:
					if doEyelink:
						eyelink.sendMessage('TARGET ON')
					#queueFromExpToEEG.put([frameTime,'target on'])
					sendTargetOnMessage = False
					targetOnMessageSent = True
					targetOnTime = frameTime
				#check for eye tracking data here
				if doEyelink:
			 		eyeData = eyelink.getNextData()
					if (eyeData==3) or (eyeData==5):
						eyeEvent = eyelink.getFloatData()
						if isinstance(eyeEvent,pylink.StartSaccadeEvent):
							saccadeMade = True
							saccadeStartTimes2.append(getTime())				
							saccadeStartTimes.append(eyeEvent.getTime())
							if not saccadeSound.stillPlaying():
								saccadeSound.play()
						elif isinstance(eyeEvent,pylink.StartBlinkEvent):
							blinkMade = True
							blinkStartTimes2.append(getTime())
							blinkStartTimes.append(eyeEvent.getTime())
							if not blinkSound.stillPlaying():
								blinkSound.play()
					elif (eyeData==4) or (eyeData==6):
						eyeEvent = eyelink.getFloatData()
						if isinstance(eyeEvent,pylink.EndSaccadeEvent):
							saccadeEndTimes2.append(getTime())
							saccadeEndTimes.append(eyeEvent.getTime())
							saccadeLocations.append(eyeEvent.getEndGaze())
						elif isinstance(eyeEvent,pylink.EndBlinkEvent):
							blinkEndTimes2.append(getTime())		
							blinkEndTimes.append(eyeEvent.getTime())		
				# print getTime()-start #check the total loop time 
			#trial done
			#print printList
			#check for responses here
			responseMade,rts,triggerData = checkInput()
			#compute feedback
			if targetIdentity=='square':
				if not responseMade:
					feedbackText = 'Miss!'
					feedbackColor = [255,0,0,255]
					print 'miss'
				else:
					if (len(rts[0])==0) or (len(rts[1])==0):
						feedbackText = 'Use both!'
						feedbackColor = [255,0,0,255]
						print 'only one trigger pressed'
					else:
						rt = (rts[0][0]+rts[1][0])/2.0-targetOnTime
						# if rts[0][0]<rts[1][0]:
						# 	rt = rts[1][0]-targetOnTime
						# else:
						# 	rt = rts[0][0]-targetOnTime
						feedbackText = str(int(rt*1000))
						feedbackColor = [0,255,0,255]
						print feedbackText
			else:
				if responseMade:
					if (len(rts[0])==0):
						rt = rts[1][0]-targetOnTime
					elif (len(rts[1])==0):
						rt = rts[0][0]-targetOnTime
					else:
						rt = (rts[0][0]+rts[1][0])/2.0-targetOnTime
					feedbackText = 'Oops!'
					feedbackColor = [255,0,0,255]
					print 'false alarm'
				else:
					feedbackText = 'Good'
					feedbackColor = [0,255,0,255]
					print 'nogo'
			#show feedback
			gl.glClearColor(.5,.5,.5,1)
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)
			drawText( feedbackText , feedbackFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=feedbackColor )
			setPhotoTrigger()	
			refreshWindows()
			trialDoneTime = getTime()
			if doEyelink:
				eyelink.sendMessage('FEEDBACK ON')
			trialDone = False
			while getTime()<(trialDoneTime+feedbackDuration):
				#check for eye tracking data here (but don't do anything about it because Ss are allowed to move/blink during feedback)
				if doEyelink:
			 		eyeData = eyelink.getNextData()
			#check for responses here
			responseMade2,rts2,triggerData = checkInput(triggerData)
			if responseMade2:
				feedbackResponse = 'TRUE'
				print 'feedback response made'
			if doEyelink:
				eyelink.sendMessage('TRIAL OK')
				eyelink.stopRecording()
				# dataFile.write('\t'.join(['\t'.join(map(str,i)) for i in saccadeLocations])+'\n')
				# dataFile.write('\t'.join(map(str,saccadeStartTimes))+'\n')
				# dataFile.write('\t'.join(map(str,saccadeEndTimes))+'\n')
				# dataFile.write('\t'.join(map(str,blinkStartTimes))+'\n')
				# dataFile.write('\t'.join(map(str,blinkEndTimes))+'\n')
				# dataFile.write('\t'.join(map(str,saccadeStartTimes2))+'\n')
				# dataFile.write('\t'.join(map(str,saccadeEndTimes2))+'\n')
				# dataFile.write('\t'.join(map(str,blinkStartTimes2))+'\n')
				# dataFile.write('\t'.join(map(str,blinkEndTimes2))+'\n')
			#write out trial info
			triggerData = [[[i[0]-targetOnTime,i[1]] for i in side] for side in triggerData]#fix times to be relative to target on time
			triggerTrialInfo = '\t'.join(map(str,[subInfo[0],block,trialNum]))
			triggerDataToWriteLeft = '\n'.join([triggerTrialInfo + '\t' + '\t'.join(map(str,i)) for i in triggerData[0]])
			triggerDataToWriteRight = '\n'.join([triggerTrialInfo + '\t' + '\t'.join(map(str,i)) for i in triggerData[1]])
			writerProcess.qTo.put(['write','trigger',triggerDataToWriteLeft])
			writerProcess.qTo.put(['write','trigger',triggerDataToWriteRight])
			dataToWrite = '\t'.join(map(str,[ subInfoForFile , messageViewingTime , block , trialNum , brightSide , fastSide , cueSide , targetSide , targetIdentity , rt , feedbackResponse ]))
			writerProcess.qTo.put(['write','data',dataToWrite])
			if doEyelink:
				eyelink.sendMessage(dataToWrite)
		print 'on break'



	########
	# Initialize the data files
	########

	#get subject info
	subInfo = getSubInfo()
	password = subInfo[-1]
	subInfo = subInfo[0:(len(subInfo)-1)]

	if not os.path.exists('_Data'):
		os.mkdir('_Data')
	if subInfo[0]=='test':
		filebase = 'test'
	else:
		filebase = '_'.join(subInfo[0:6])
	if not os.path.exists('_Data/'+filebase):
		os.mkdir('_Data/'+filebase)

	shutil.copy(sys.argv[0], '_Data/'+filebase+'/'+filebase+'_code.py')

	labjackProcess.qTo.put(['write','_Data/'+filebase+'/'+filebase+'_jack.txt'])
	eyelinkProcess.put(['edfPath','_Data/'+filebase+'/'+filebase+'_eyelink.edf'])

	writerProcess.qTo.put(['newFile','data','_Data/'+filebase+'/'+filebase+'_data.txt'])
	writerProcess.qTo.put(['write','data',password])
	header ='\t'.join(['id' , 'year' , 'month' , 'day' , 'hour' , 'minute' , 'sex' , 'age'  , 'handedness' , 'wait' , 'block' , 'trial' , 'fastSide' , 'cue' , 'targetSide', 'rt' , 'response' , 'error' , 'preTargetResponse' , 'feedbackResponse'])
	writerProcess.qTo.put(['write','data',header])

	writerProcess.qTo.put(['newFile','trigger','_Data/'+filebase+'/'+filebase+'_trigger.txt'])
	header ='\t'.join(['id' , 'block' , 'trial' , 'trigger' , 'time' , 'value' ])
	writerProcess.qTo.put(['write','trigger',header])

	subInfoForFile = '\t'.join(map(str,subInfo))


	########
	# Start the experiment
	########

	messageViewingTime = showMessage('Press any trigger to begin practice.')
	block = 'practice'
	runBlock()
	messageViewingTime = showMessage('Practice is complete.\nPress any trigger to begin the experiment.')

	for i in range(numberOfBlocks):
		block = str(i+1)
		runBlock()
		if i<(numberOfBlocks):
			messageViewingTime = showMessage('Take a break!\nYou\'re about '+str(block)+'/'+str(numberOfBlocks)+' done.\nWhen you are ready, press any trigger to continue the experiment.')

	messageViewingTime = showMessage('You\'re all done!\nPlease alert the person conducting this experiment that you have finished.')

	exitSafely()

