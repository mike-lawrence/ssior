if __name__ == '__main__':
	########
	#Important parameters
	########

	viewingDistance = 57.0 #units can be anything so long as they match those used in stimDisplayWidth below
	stimDisplayWidth = 54.5 #units can be anything so long as they match those used in viewingDistance above
	stimDisplayRes = (1920,1080) #pixel resolution of the stimDisplay
	stimDisplayPosition = (0-1440-1920,0)
	stimDisplayMirrorPosition = (0,0)

	stamperWindowPosition = (0,0)#(1920/2+1,0)

	writerWindowPosition = (200,0)#(1920/2+1,200)

	photoStimSize = [20,20]
	photoStimPosition = [stimDisplayPosition[0]/2-photoStimSize[0]/2,stimDisplayPosition[1]-photoStimSize[1]/2]

	doEyelink = True
	eyelinkWindowPosition = (400,0)#(1920/2+1,400)
	calibrationDisplaySizeInDegrees = [5,5]
	calibrationDotSizeInDegrees = 1

	doLabjack = False
	labjackWindowPosition = (1920/2+1,600)

	triggerLeftAxis = 2
	triggerRightAxis = 5
	triggerCriterionValue = -(2**16/4) #16 bit precision on the triggers, split above/below 0

	fastSideList = ['left','right']
	cueSideList = ['left','right']
	targetSideList = ['left','right']
	targetIdentityList = ['square','diamond']

	#times are specified in frames @ 60Hz

	slowCycleHalfFrames = 2 #half the cycle length
	fastCycleHalfFrames = 2 #half the cycle length

	fixationDurationList = range(60,120,2) #1s-2s, timed to not coincide with either flicker
	cueDuration = 6 #100ms
	cueCuebackSoa = 30 #500ms
	cuebackDuration = 6 #100ms
	cuebackTargetSoa = 30 #for a total cue-target-Soa of 1s
	responseTimeout = 60 #1000ms

	feedbackDuration = 1.000 #specified in seconds

	numberOfBlocks = 10 
	repsPerBlock = 2

	instructionSizeInDegrees = 1 
	feedbackSizeInDegrees = 1

	fixationSizeInDegrees = .1#.25
	offsetSizeInDegrees = 13
	targetSizeInDegrees = 3
	targetThicknessProportion = .8
	flickerSizeInDegrees = 1

	textWidth = .9 #specify the proportion of the stimDisplay to use when drawing instructions


	########
	# Import libraries
	########
	import sdl2 #for input and display
	import numpy #for image and display manipulation
	import scipy.misc #for resizing numpy images via scipy.misc.imresize
	from PIL import Image #for image manipulation
	from PIL import ImageFont
	from PIL import ImageOps
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
	import fileForker

	byteify = lambda x, enc: x.encode(enc)

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
	participantRandomSeed = int(time.time()) #grab the time of the timer initialization to use as a seed
	random.seed(participantRandomSeed) #use the time to set the random seed


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

	calibrationDisplaySize = [int(calibrationDisplaySizeInDegrees[0]*PPD),int(calibrationDisplaySizeInDegrees[0]*PPD)]

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
	# initialize the eyelink
	########
	if doEyelink:
		eyelinkChild = fileForker.childClass(childFile='eyelinkChild.py')
		eyelinkChild.initDict['windowPosition'] = eyelinkWindowPosition
		eyelinkChild.initDict['stimDisplayRes'] = stimDisplayRes
		eyelinkChild.initDict['calibrationDisplaySize'] = [1920,1080]#calibrationDisplaySize
		eyelinkChild.initDict['calibrationDotSize'] = int(calibrationDotSize)
		eyelinkChild.start()


	########
	# Initialize the writer
	########
	writerChild = fileForker.childClass(childFile='writerChild.py')
	writerChild.initDict['windowPosition'] = writerWindowPosition
	time.sleep(1) #give the other windows some time to initialize
	writerChild.start()


	########
	# Initialize the stimDisplayMirrorChild
	########
	# stimDisplayMirrorChild = fileForker.childClass(childFile='stimDisplayMirrorChild.py')
	# stimDisplayMirrorChild.initDict['windowPosition'] = stimDisplayMirrorPosition
	# time.sleep(1) #give the other windows some time to initialize
	# stimDisplayMirrorChild.start()

	########
	# Initialize the stimDisplay
	########
	class stimDisplayClass:
		def __init__(self,stimDisplayRes,stimDisplayPosition):#,stimDisplayMirrorChild):
			self.stimDisplayRes = stimDisplayRes
			# self.stimDisplayMirrorChild = stimDisplayMirrorChild
			sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
			self.stimDisplayRes = stimDisplayRes
			self.stimDisplayPosition = stimDisplayPosition
			self.Window = sdl2.video.SDL_CreateWindow(byteify('stimDisplay', "utf-8"),self.stimDisplayPosition[0],self.stimDisplayPosition[1],self.stimDisplayRes[0],self.stimDisplayRes[1],sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
			self.glContext = sdl2.SDL_GL_CreateContext(self.Window)
			gl.glMatrixMode(gl.GL_PROJECTION)
			gl.glLoadIdentity()
			gl.glOrtho(0, stimDisplayRes[0],stimDisplayRes[1], 0, 0, 1)
			gl.glMatrixMode(gl.GL_MODELVIEW)
			gl.glDisable(gl.GL_DEPTH_TEST)
			gl.glReadBuffer(gl.GL_FRONT)
			gl.glClearColor(0,0,0,1)
			start = time.time()
			while time.time()<(start+2):
				sdl2.SDL_PumpEvents()
			self.refresh()
			self.refresh()
		def refresh(self,clearColor=[0,0,0,1]):
			sdl2.SDL_GL_SwapWindow(self.Window)
			# self.stimDisplayMirrorChild.qTo.put(['frame',self.stimDisplayRes,gl.glReadPixels(0, 0, self.stimDisplayRes[0], self.stimDisplayRes[1], gl.GL_BGR, gl.GL_UNSIGNED_BYTE)])
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)


	time.sleep(1)
	stimDisplay = stimDisplayClass(stimDisplayRes=stimDisplayRes,stimDisplayPosition=stimDisplayPosition)#,stimDisplayMirrorChild=stimDisplayMirrorChild)


	########
	# start the event timestamper
	########
	stamperChild = fileForker.childClass(childFile='stamperChild.py')
	stamperChild.initDict['windowPosition'] = stamperWindowPosition
	time.sleep(1) #give the other windows some time to initialize
	stamperChild.start()


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


	def drawFeedback(feedbackText,feedbackColor):
		feedbackArray = text2numpy(feedbackText,feedbackFont,fg=feedbackColor,bg=[0,0,0,0])
		blitNumpy(feedbackArray,stimDisplayRes[0]/2,stimDisplayRes[1]/2,xCentered=True,yCentered=True)


	def drawDot(size,xOffset=0,grey=False):
		if grey:
			gl.glColor3f(.25,.25,.25)
		else:
			gl.glColor3f(1,1,1)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*size , stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*size)
		gl.glEnd()


	def drawRing(xOffset,outer,inner):
		gl.glColor3f(1,1,1)
		gl.glBegin(gl.GL_QUAD_STRIP)
		for i in range(360):
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*outer)
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*inner)
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*outer)
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*inner)
		gl.glEnd()


	def drawSquare(xOffset,outer,inner):
		gl.glColor3f(1,1,1)
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
		gl.glColor3f(1,1,1)
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

	def drawCalTarget(x=stimDisplayRes[0]/2,y=stimDisplayRes[1]/2):
		gl.glColor3f(1,1,1)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( x + math.sin(i*math.pi/180.0)*(calibrationDotSize/2.0) , y + math.cos(i*math.pi/180.0)*(calibrationDotSize/2.0))
		gl.glEnd()
		gl.glColor3f(0,0,0)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( x + math.sin(i*math.pi/180.0)*(calibrationDotSize/8.0) , y + math.cos(i*math.pi/180.0)*(calibrationDotSize/8.0))
		gl.glEnd()


	def doCalibration():
		drawDot(fixationSize)
		stimDisplay.refresh()
		eyelinkChild.qTo.put('doCalibration')
		calibrationDone = False
		while not calibrationDone:
			if not stamperChild.qFrom.empty():
				event = stamperChild.qFrom.get()
				if event['type'] == 'key' :
					key = event['value']
					if key=='q':
						exitSafely()
					else: #pass keys to eyelink
						eyelinkChild.qTo.put(['keycode',event['keysym']])
			if not eyelinkChild.qFrom.empty():
				message = eyelinkChild.qFrom.get()
				if message=='calibrationComplete':
					calibrationDone = True
				elif (message=='setupCalDisplay') or (message=='exitCalDisplay'):
					drawDot(fixationSize)
					stimDisplay.refresh()
				elif message=='eraseCalTarget':
					pass
				elif message=='clearCalDisplay':
					stimDisplay.refresh()
				elif message[0]=='drawCalTarget':
					x = message[1]
					y = message[2]
					drawCalTarget(x,y)
					stimDisplay.refresh()
				elif message[0]=='image':
					blitNumpy(message[1],stimDisplayRes[0]/2,stimDisplayRes[1]/2,xCentered=True,yCentered=True)
					stimDisplay.refresh()

	def drawPhotoStim():
		# pass
		gl.glColor3f(1,1,1)
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex2f( photoStimPosition[0] - photoStimSize[0]/2 , photoStimPosition[1] - photoStimSize[1]/2 )
		gl.glVertex2f( photoStimPosition[0] - photoStimSize[0]/2 , photoStimPosition[1] + photoStimSize[1]/2 )
		gl.glVertex2f( photoStimPosition[0] + photoStimSize[0]/2 , photoStimPosition[1] + photoStimSize[1]/2 )
		gl.glVertex2f( photoStimPosition[0] + photoStimSize[0]/2 , photoStimPosition[1] - photoStimSize[1]/2 )
		gl.glVertex2f( photoStimPosition[0] - photoStimSize[0]/2 , photoStimPosition[1] - photoStimSize[1]/2 )
		gl.glEnd()


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
		writerChild.stop()
		if doEyelink:
			eyelinkChild.stop()
		if doLabjack:
			labjackChild.stop(killAfter=60)
		stamperChild.stop(killAfter=60)
		while stamperChild.isAlive():
			time.sleep(.1)
		sys.exit()


	#define a function that waits for a response
	def waitForResponse():
		done = False
		while not done:
			if not stamperChild.qFrom.empty():
				event = stamperChild.qFrom.get()
				if event['type']=='key':
					response = event['value']
					if response=='q':
						exitSafely()
					else:
						done = True
				elif event['type'] == 'axis':
					response = event['axis']
					if event['value']>triggerCriterionValue:
						done = True
		return response


	#define a function that prints a message on the stimDisplay while looking for user input to continue. The function returns the total time it waited
	def showMessage(myText):
		messageViewingTimeStart = getTime()
		stimDisplay.refresh()
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		simpleWait(0.500)
		stimDisplay.refresh()
		waitForResponse()
		stimDisplay.refresh()
		simpleWait(0.500)
		messageViewingTime = getTime() - messageViewingTimeStart
		return messageViewingTime


	#define a function that requests user input
	def getInput(getWhat):
		getWhat = getWhat
		textInput = ''
		stimDisplay.refresh()
		simpleWait(0.500)
		myText = getWhat+textInput
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		stimDisplay.refresh()
		done = False
		while not done:
			if not stamperChild.qFrom.empty():
				event = stamperChild.qFrom.get()
				if event['type'] == 'key' :
					response = event['value']
					if response=='q':
						exitSafely()
					elif response == 'backspace':
						if textInput!='':
							textInput = textInput[0:(len(textInput)-1)]
							myText = getWhat+textInput
							drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
							stimDisplay.refresh()
					elif response == 'return':
						done = True
					else:
						textInput = textInput + response
						myText = getWhat+textInput
						drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
						stimDisplay.refresh()
		stimDisplay.refresh()
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
		else:
			sex = 'test'
			age = 'test'
			handedness = 'test'
		subInfo = [ sid , year , month , day , hour , minute , sex , age , handedness ]
		return subInfo


	#define a function that generates a randomized list of trial-by-trial stimulus information representing a factorial combination of the independent variables.
	def getTrials():
		trials=[]
		for fastSide in fastSideList:
			for cueSide in cueSideList:
				for targetSide in targetSideList:
					for targetIdentity in targetIdentityList:
						for i in range(repsPerBlock):
							trials.append([fastSide,cueSide,targetSide,targetIdentity])
		random.shuffle(trials)
		return trials


	#define a function that runs a block of trials
	def runBlock():

		start = time.time()
		while (time.time()-start)<1:
			while not stamperChild.qFrom.empty():
				event = stamperChild.qFrom.get()
		
		# print 'main: block started'

		#get trials
		trialList = getTrials()	

		#run the trials
		trialNum = 0
		for trialInfo in trialList:
			#bump the trial number
			trialNum = trialNum + 1
			
			#parse the trial info
			fastSide,cueSide,targetSide,targetIdentity = trialInfo
			
			#generate fixation duration
			fixationDuration = random.choice(fixationDurationList)

			trialDescriptor = '\t'.join(map(str,[subInfo[0],block,trialNum]))

			if doLabjack:
				labjackChild.qTo.put(['sendTriggers',True])

			########
			# Do drift correction (if using eyelink)
			########
			trialInitiationTime = 'NA'
			recordingStartTime = 'NA'
			drawDot(fixationSize,grey=True)
			stimDisplay.refresh()
			driftCorrectStartTime = getTime()
			if doEyelink:
				outerDone = False
				while not outerDone:
					drawDot(fixationSize,grey=True)
					stimDisplay.refresh()
					outerDone = True #set to False below if need to re-do drift correct after re-calibration
					eyelinkChild.qTo.put(['doDriftCorrect',[int(stimDisplayRes[0]/2),int(stimDisplayRes[1]/2)]])
					quitWhenDoneDrift = False
					leftTriggerRoseAboveCriterion = False
					leftTriggerFellBelowCriterion = False
					rightTriggerRoseAboveCriterion = False
					rightTriggerFellBelowCriterion = False
					buttonSentAlready = False
					innerDone = False
					while not innerDone:
						if not eyelinkChild.qFrom.empty():
							message = eyelinkChild.qFrom.get()
							if message=='driftCorrectComplete':
								innerDone = True
							elif message=='doCalibration':
								# print 'main: re-calibrating'
								doCalibration()
								innerDone = True
								outerDone = False
						while not stamperChild.qFrom.empty():
							event = stamperChild.qFrom.get()
							# print event
							if event['type'] == 'key' :
								if event['value']=='q':
									quitWhenDoneDrift = True
								eyelinkChild.qTo.put(['keycode',event['keysym']])
							elif event['type'] == 'axis':
								if event['axis']==triggerLeftAxis:
									if not leftTriggerRoseAboveCriterion:
										if event['value']>triggerCriterionValue:
											leftTriggerRoseAboveCriterion = True
									elif not leftTriggerFellBelowCriterion:
										if event['value']<triggerCriterionValue:
											leftTriggerFellBelowCriterion = True
								elif event['axis']==triggerRightAxis:
									if not rightTriggerRoseAboveCriterion:
										if event['value']>triggerCriterionValue:
											rightTriggerRoseAboveCriterion = True
									elif not rightTriggerFellBelowCriterion:
										if event['value']<triggerCriterionValue:
											rightTriggerFellBelowCriterion = True
						if leftTriggerFellBelowCriterion and rightTriggerFellBelowCriterion and (not buttonSentAlready):
							eyelinkChild.qTo.put('button')
							buttonSentAlready = True
				# print 'main: drift correction complete'
				if quitWhenDoneDrift:
					exitSafely()
				# print 'main: starting recording'
				#all correction done
				eyelinkChild.qTo.put('startRecording')
				# print 'main: toggling blink detection on'
				eyelinkChild.qTo.put(['reportBlinks',True])
				# print 'main: toggling saccade detection on'
				eyelinkChild.qTo.put(['reportSaccades',True])
				# print 'main: adding trial start message to edf'
				eyelinkChild.qTo.put(['sendMessage','trialStart\t'+trialDescriptor])
				trialInitiationTime = getTime() - driftCorrectStartTime
				recordingStartRequestTime = getTime()
				doneWaitingForRecordingToStart = False
				# print 'main: waiting for recording to start'
				while not doneWaitingForRecordingToStart:
					while not stamperChild.qFrom.empty():
						event = stamperChild.qFrom.get()
						# print event
						if event['type'] == 'key' :
							if event['value']=='q':
								exitSafely()
					if not eyelinkChild.qFrom.empty():
						message = eyelinkChild.qFrom.get()
						if message=='recordingStarted':
							doneWaitingForRecordingToStart = True
				recordingStartTime = getTime() - recordingStartRequestTime
				# print 'main: recording start delay: '+str(recordingStartTime)


			#tell the labjack to expect a trial start stim
			if doLabjack:
				labjackChild.qTo.put('trialStart')

			#prep and show the buffers
			drawDot(fixationSize,grey=True)
			drawPhotoStim()
			stimDisplay.refresh()
			drawDot(fixationSize,grey=True)
			drawPhotoStim()
			stimDisplay.refresh() #this one should block until it's actually displayed

			#get the trial start time 
			trialStartTime = getTime() - 1/60.0 #time of penultimage refresh
			lastFrameTime = trialStartTime
			
			#compute event times
			cueOnFrame = 0 + fixationDuration
			cueOffFrame = cueOnFrame + cueDuration
			cuebackOnFrame = cueOnFrame + cueCuebackSoa
			cuebackOffFrame = cuebackOnFrame + cuebackDuration
			targetOnFrame = cuebackOnFrame + cuebackTargetSoa
			targetOffFrame = targetOnFrame + responseTimeout
			targetOnTime = trialStartTime + targetOnFrame/60.0 #overwritten later *if* the target appears
			
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
			doPhotoTrigger = False

			#initialize variables to write
			blinkMade = False
			saccadeMade = False
			responseMade = False
			triggerData = {'left':[],'right':[]}
			leftTriggerRoseAboveCriterion = False
			leftTriggerFellBelowCriterion = False
			rightTriggerRoseAboveCriterion = False
			rightTriggerFellBelowCriterion = False

			#create some variables
			preTargetResponse = False
			rt = 'NA'
			error = 'NA'

			#loop through time
			trialDone = False
			frameNum = -1
			while not trialDone:
				frameNum = frameNum + 1
				frameText = ''
				drawDot(fixationSize,grey=True)
				########
				# Manage main stimulus timecourse
				########
				if frameNum>=cueOnFrame:
					if frameNum<cueOffFrame:
						# frameText = frameText + ' cueOn'
						if not cueOnMessageSent:
							sendCueOnMessage = True
							doPhotoTrigger = True
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
										trialDone = True #trial timeout
				########
				#check whether to draw the faster flicker
				########
				if (frameNum%(fastCycleHalfFrames*2))==1:
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
				########
				#check whether to draw the slower flicker
				########
				if (frameNum%(slowCycleHalfFrames*2))==1:
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
				########
				# Manage the photo trigger
				########
				if doPhotoTrigger:
					drawPhotoStim()
					doPhotoTrigger = False #so it only stays on for one frame
				########
				#Refresh the screen
				########
				stimDisplay.refresh() #show this frame (should block until shown (if we haven't missed a frame!))
				frameTime = getTime() #get the time of this frame (refresh should have blocked)
				# if (frameNum%100)==1:
				# 	print (frameTime-lastFrameTime) #show the error in between frames (ideally 0)
				lastFrameTime = frameTime
				########
				# Send messages as necessary
				########
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
						eyelinkChild.qTo.put(['sendMessage','cueOn\t'+trialDescriptor])
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
						eyelinkChild.qTo.put(['sendMessage','targetOn\t'+trialDescriptor])
					#queueFromExpToEEG.put([frameTime,'target on'])
					sendTargetOnMessage = False
					targetOnMessageSent = True
					targetOnTime = frameTime
				########
				# Manage eye movements
				########
				if doEyelink:
					if not eyelinkChild.qFrom.empty():
						message = eyelinkChild.qFrom.get()
						if message=='blink':
							# print 'main: blink'
							blinkMade = 'TRUE'
							trialDone = True
							feedbackText = 'Blinked!'
							feedbackColor = [255,0,0,255]
						elif message[0]=='gazeTargetLost': #saccade
							# print 'main: saccade'
							saccadeMade = 'TRUE'
							trialDone = True
							feedbackText = 'Eyes moved!'
							feedbackColor = [255,0,0,255]
				########
				#manage responses
				########
				while not stamperChild.qFrom.empty():
					event = stamperChild.qFrom.get()
					if event['type'] == 'key' :
						if event['value']=='q':
							exitSafely()
					elif event['type'] == 'axis':
						if event['axis']==triggerLeftAxis:
							triggerData['left'].append([event['time'],event['value']])
							if not leftTriggerRoseAboveCriterion:
								if event['value']>triggerCriterionValue:
									leftTriggerRoseAboveCriterion = True
									timeLeftTriggerRoseAboveCriterion = event['time']*1000
									if frameNum<targetOnFrame:
										preTargetResponse = True
										trialDone = True #kill the trial if there's a response before target
							elif not leftTriggerFellBelowCriterion:
								if event['value']<triggerCriterionValue:
									leftTriggerFellBelowCriterion = True
									timeLeftTriggerFellBelowCriterion = event['time']*1000
						elif event['axis']==triggerRightAxis:
							triggerData['right'].append([event['time'],event['value']])
							if not rightTriggerRoseAboveCriterion:
								if event['value']>triggerCriterionValue:
									rightTriggerRoseAboveCriterion = True
									timeRightTriggerRoseAboveCriterion = event['time']*1000
									if frameNum<targetOnFrame:
										preTargetResponse = True
										trialDone = True #kill the trial if there's a response before target
							elif not rightTriggerFellBelowCriterion:
								if event['value']<triggerCriterionValue:
									rightTriggerFellBelowCriterion = True
									timeRightTriggerFellBelowCriterion = event['time']*1000
				if leftTriggerFellBelowCriterion & rightTriggerFellBelowCriterion:
					responseMade = True
					trialDone = True #end trial on response
			########
			#trial done
			########
			#talk to eyelink
			if doEyelink:
				eyelinkChild.qTo.put(['sendMessage','trialDone\t'+trialDescriptor])
				eyelinkChild.qTo.put(['reportBlinks',False])
				eyelinkChild.qTo.put(['reportSaccades',False])
				eyelinkChild.qTo.put(['doSounds',False])
			#talk to labjack
			if doLabjack:
				labjackChild.qTo.put('trialDone')
			#compute feedback	
			if preTargetResponse: #response made before target presentation
				feedbackText = 'Too soon!'
				feedbackColor = [255,0,0,255]
				# print 'main: too soon'
			elif responseMade: #response made after target presentation
				if targetIdentity=='diamond': #not supposed to respond to diamonds
					feedbackText = 'Oops!'
					feedbackColor = [255,0,0,255]
					# print 'main: false alarm'
				else:
					rt = (timeLeftTriggerFellBelowCriterion+timeRightTriggerFellBelowCriterion)/2 - (targetOnTime*1000)
					feedbackText = str(int(rt/10)) #tenths of seconds
					feedbackColor = [127,127,127,255]
					# print 'main: '+feedbackText
			elif targetIdentity=='square':
				feedbackText = 'Miss!'
				feedbackColor = [255,0,0,255]
				# print 'main: miss'
			else:
				feedbackText = 'Good'
				feedbackColor = [127,127,127,255]
			print 'main: block '+str(block)+', trial '+str(trial)+' '+feedback
			#show feedback
			drawFeedback(feedbackText,feedbackColor)
			drawPhotoStim()	
			stimDisplay.refresh()
			trialDoneTime = getTime()
			#wait for feedback duration to complete
			recalibrationRequested = False
			while getTime()< (trialDoneTime + feedbackDuration):
				while not stamperChild.qFrom.empty():
					event = stamperChild.qFrom.get()
					if event['type'] == 'key' :
						if event['value']=='q':
							exitSafely()
						elif (event['value']=='p') & (doEyelink):
							recalibrationRequested = True
					elif event['type'] == 'axis':
						if event['axis']==triggerLeftAxis:
							triggerData['left'].append([event['time'],event['value']])
						elif event['axis']==triggerRightAxis:
							triggerData['right'].append([event['time'],event['value']])
			#write out trial info
			triggerData['left'] = [[i[0]-targetOnTime,i[1]] for i in triggerData['left']] #fix times to be relative to target on time
			triggerData['right'] = [[i[0]-targetOnTime,i[1]] for i in triggerData['right']] #fix times to be relative to target on time
			triggerDataToWriteLeft = '\n'.join([trialDescriptor + '\tleft\t' + '\t'.join(map(str,i)) for i in triggerData['left']])
			triggerDataToWriteRight = '\n'.join([trialDescriptor + '\tright\t' + '\t'.join(map(str,i)) for i in triggerData['right']])
			writerChild.qTo.put(['write','trigger',triggerDataToWriteLeft])
			writerChild.qTo.put(['write','trigger',triggerDataToWriteRight])
			dataToWrite = '\t'.join(map(str,[ subInfoForFile , messageViewingTime , block , trialNum , fastSide , cueSide , targetSide , targetIdentity , fixationDuration , responseMade , rt , preTargetResponse , saccadeMade , blinkMade ]))
			writerChild.qTo.put(['write','data',dataToWrite])
			if recalibrationRequested:
				doCalibration()
		print 'main: on break'



	########
	# Initialize the data files
	########

	if doEyelink:
		doCalibration()

	#get subject info
	subInfo = getSubInfo()

	if not os.path.exists('_Data'):
		os.mkdir('_Data')
	if subInfo[0]=='test':
		filebase = 'test'
	else:
		filebase = '_'.join(subInfo[0:6])
	if not os.path.exists('_Data/'+filebase):
		os.mkdir('_Data/'+filebase)

	shutil.copy(sys.argv[0], '_Data/'+filebase+'/'+filebase+'_code.py')

	if doEyelink:
		eyelinkChild.qTo.put(['edfPath','_Data/'+filebase+'/'+filebase+'_eyelink.edf'])

	writerChild.qTo.put(['newFile','data','_Data/'+filebase+'/'+filebase+'_data.txt'])
	writerChild.qTo.put(['write','data',str(participantRandomSeed)])
	header ='\t'.join(['id' , 'year' , 'month' , 'day' , 'hour' , 'minute' , 'sex' , 'age'  , 'handedness' , 'messageViewingTime' , 'block' , 'trialNum' , 'fastSide' , 'cueSide' , 'targetSide' , 'targetIdentity' , 'fixationDuration' , 'responseMade' , 'rt' , 'preTargetResponse' , 'saccadeMade' , 'blinkMade'])
	writerChild.qTo.put(['write','data',header])

	writerChild.qTo.put(['newFile','trigger','_Data/'+filebase+'/'+filebase+'_trigger.txt'])
	header ='\t'.join(['id' , 'block' , 'trial' , 'trigger' , 'time' , 'value' ])
	writerChild.qTo.put(['write','trigger',header])

	subInfoForFile = '\t'.join(map(str,subInfo))


	########
	# Start the experiment
	########

	messageViewingTime = showMessage('Press any trigger to begin practice.')
	block = 'practice'
	runBlock()
	messageViewingTime = showMessage('Practice is complete.\nPress any trigger to begin the experiment.')

	for i in range(numberOfBlocks):
		block = i+1
		runBlock()
		if block<(numberOfBlocks):
			messageViewingTime = showMessage('Take a break!\nYou\'re about '+str(block)+'/'+str(numberOfBlocks)+' done.\nWhen you are ready, press any trigger to continue the experiment.')

	messageViewingTime = showMessage('You\'re all done!\nThe experimenter will be with you momentarily.')

	exitSafely()

