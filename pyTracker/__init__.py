class trackerClass:
	def start(self,camIndex,camRes,monitorResize,fidSizeInmm):
		import billiard
		billiard.forking_enable(0)
		self.qTo = billiard.Queue()
		self.qFrom = billiard.Queue()
		self.process = billiard.Process( target=trackerLoop , args=(camIndex,camRes,monitorResize,fidSizeInmm,self.qTo,self.qFrom,) )
		self.process.start()
		return None
	def quit(self):
		self.qTo.put(['quit'])
		self.process.terminate()
		del self.qTo
		del self.qFrom
		return None


def trackerLoop(camIndex,camRes,monitorResize,fidSizeInmm,qTo,qFrom):
	import time
	import os
	import numpy
	import scipy.ndimage.filters
	import scipy.interpolate
	import cv2
	import sdl2
	import sdl2.ext
	import sys
	import aifc
	import threading
	import math
	import cPickle
	try:
		import appnope
		appnope.nope()
	except:
		pass
	sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
	class ReadAIFF:
		def __init__(self, fileName):
			self.a = aifc.open(fileName)
			self.frameUpto = 0
			self.bytesPerFrame = self.a.getnchannels() * self.a.getsampwidth()
			self.numFrames = self.a.getnframes()
			self.done = threading.Event()
		def playNextChunk(self, unused, buf, bufSize):
			framesInBuffer = bufSize/self.bytesPerFrame
			framesToRead = min(framesInBuffer, self.numFrames-self.frameUpto)
			if self.frameUpto == self.numFrames:
				self.done.set()
			for i, b in enumerate(self.a.readframes(framesToRead)):
				buf[i] = ord(b)
			for i in range(self.bytesPerFrame*framesToRead, self.bytesPerFrame*framesInBuffer):
				buf[i] = 0
			self.frameUpto += framesToRead
	class dotObj:
		def __init__(self,x1,y1,x2,y2,img,imageTime,name,fid=None):
			self.imageTime = imageTime
			self.name = name
			self.lost = True
			self.blink = False
			# try:
			if x1<x2:
				xLo = x1
				xHi = x2
			else:
				xLo = x2
				xHi = x1
			if y1<y2:
				yLo = y1
				yHi = y2
			else:
				yLo = y2
				yHi = y1
			img = img[yLo:yHi,xLo:xHi]
			self.ellipse = getDarkEllipse(img)
			if self.ellipse!=None:
				self.ellipse = ((self.ellipse[0][0]+xLo,self.ellipse[0][1]+yLo),self.ellipse[1],self.ellipse[2])
				self.lost = False
				self.x = self.ellipse[0][0]
				self.y = self.ellipse[0][1]
				self.major = self.ellipse[1][0]
				self.minor = self.ellipse[1][1]
				self.angle = self.ellipse[2]
				self.xPixel = int(self.x)
				self.yPixel = int(self.y)
				self.radii = []
				self.radius = (self.ellipse[1][0]+self.ellipse[1][1])/4
				self.radiusPixel = int(self.radius)
				if fid!=None:
					self.x2 = (self.x-fid.x)/fid.radius
					self.y2 = (self.y-fid.y)/fid.radius
					self.radius2 = self.radius/fid.radius
					self.x2Last = self.x2
					self.y2Last = self.y2
					self.tLast = self.imageTime
					self.velocity = None
				self.SDs = []
				self.medianSD = None
				self.critSD = None
				self.medianRadius = None
				self.critRadius = None
			# except:
			# 	pass
		def update(self,img,imageTime,fid=None,other=None):
			self.imageTime = imageTime
			if self.lost:
				searchSize = 5
			else:
				searchSize = 3
			self.blink = False
			self.lost = True
			if self.name=='fid':
				# try:
				xLo = self.xPixel - searchSize*self.radiusPixel
				xHi = self.xPixel + searchSize*self.radiusPixel
				yLo = self.yPixel - searchSize*self.radiusPixel
				yHi = self.yPixel + searchSize*self.radiusPixel
				img = img[yLo:yHi,xLo:xHi]
				self.ellipse = getDarkEllipse(img)
				if self.ellipse!=None:
					self.ellipse = ((self.ellipse[0][0]+xLo,self.ellipse[0][1]+yLo),self.ellipse[1],self.ellipse[2])
					self.lost = False
					self.x = self.ellipse[0][0]
					self.y = self.ellipse[0][1]
					self.major = self.ellipse[1][0]
					self.minor = self.ellipse[1][1]
					self.angle = self.ellipse[2]
					self.xPixel = int(self.x)
					self.yPixel = int(self.y)
					self.radius = (self.ellipse[1][0]+self.ellipse[1][1])/4
					self.radiusPixel = int(self.radius)
				# except:
				# 	pass
			else:
				# try:
				xLo = self.xPixel - 5*fid.radiusPixel
				xHi = self.xPixel + 5*fid.radiusPixel
				yLo = self.yPixel - 5*fid.radiusPixel
				yHi = self.yPixel + 5*fid.radiusPixel
				imgForSD = img[yLo:yHi,xLo:xHi]
				obsSD = numpy.std(imgForSD)
				self.SDs.append(obsSD)
				self.medianSD = numpy.median(self.SDs)
				self.critSD = 10*((numpy.median((self.SDs-self.medianSD)**2))**.5)
				if len(self.SDs)>=30:
					if (obsSD<(self.medianSD - self.critSD)):
						self.blink = True
				# try:
				xLo = self.xPixel - searchSize*fid.radiusPixel
				xHi = self.xPixel + searchSize*fid.radiusPixel
				yLo = self.yPixel - searchSize*fid.radiusPixel
				yHi = self.yPixel + searchSize*fid.radiusPixel
				imgForEllipse = img[yLo:yHi,xLo:xHi]
				self.ellipse = getDarkEllipse(imgForEllipse)
				if self.ellipse!=None:
					self.ellipse = ((self.ellipse[0][0]+xLo,self.ellipse[0][1]+yLo),self.ellipse[1],self.ellipse[2])
					lost = False
					radius2 = ((self.ellipse[1][0]+self.ellipse[1][1])/4.0)/fid.radius
					self.radii.append(radius2)
					if other==None:
						radiiArray = self.radii
					else:
						radiiArray = numpy.concatenate((self.radii,other.radii))
					self.medianRadius = numpy.median(radiiArray)
					self.critRadius = 10*((numpy.median((radiiArray-self.medianRadius)**2))**.5)
					if len(self.radii)>30:
						if (radius2<(1/6)) or (radius2>2) or (radius2<(self.medianRadius - self.critRadius)) or (radius2>(self.medianRadius + self.critRadius)): #(radius2<(fid.radius/6.0)) or (radius2>fid.radius*2) or 
							lost = True
							#fid diameter3is 6mm, so range from .1 to 12mm
						# if (((self.ellipse[0][1]+yLo)-fid.y)/fid.radius) > 12:
						# 	lost = True
					if not lost:
						self.lost = False
						self.x = self.ellipse[0][0]
						self.x2 = (self.x-fid.x)/fid.radius
						self.y = self.ellipse[0][1]
						self.y2 = (self.y-fid.y)/fid.radius
						self.major = self.ellipse[1][0]
						self.minor = self.ellipse[1][1]
						self.angle = self.ellipse[2]
						self.xPixel = int(self.x)
						self.yPixel = int(self.y)
						self.radius2 = radius2
						self.radius = (self.ellipse[1][0]+self.ellipse[1][1])/4
						self.radiusPixel = int(self.radius)
						dx = (self.x2-self.x2Last)
						dy = (self.y2-self.y2Last)
						self.dt = self.imageTime-self.tLast
						self.velocity = (((dx**2)+(dy**2))**.5)#/self.dt
						self.x2Last = self.x2
						self.y2Last = self.y2
						self.tLast = self.imageTime
				# print [getTime(),self.name,self.SDs[-1],self.medianSD,self.critSD,self.blink,self.radii[-1],self.medianRadius,self.critRadius,fid.radius,self.lost]
					# except:
					# 	pass
				# except:
				# 	pass
	def getDarkEllipse(img,neighborhoodSize=3):
		try:
			smoothedImg = cv2.GaussianBlur(img,(3,3),0)
			# print 'smoothing OK'
			dataMin = scipy.ndimage.filters.minimum_filter(smoothedImg, 3)
			if dataMin!=None:
				# print 'scipy filter OK'
				minLocs = numpy.where(dataMin<(numpy.min(dataMin)+numpy.std(dataMin)))
				# print 'minLocs OK'
				if len(minLocs[0])>=5:
					ellipse = cv2.fitEllipse(numpy.reshape(numpy.column_stack((minLocs[1],minLocs[0])),(len(minLocs[0]),1,2)))
					# print 'ellipse OK'
					return ellipse
				else:
					return None
			else:
				return None
		except:
			return None
	def getTime():
		return sdl2.SDL_GetPerformanceCounter()*1.0/sdl2.SDL_GetPerformanceFrequency()
	def getError(obs,exp,fit):
		error = numpy.zeros(shape=obs.shape[0])
		for i in range(obs.shape[0]):
			error[i] = scipy.interpolate.bisplev(obs[:,0][i],obs[:,1][i],fit)-exp[i]
		return error
	saveImages = False
	doSounds = False
	blinkSoundPlaying = False
	saccadeSoundPlaying = False
	hzList = []
	showImage = 1
	showPlot = 0
	doProcessing = True
	dotDict = {}
	clickingFor = None
	definingFidFinderBox = False
	fidFinderBoxX = None
	fidFinderBoxY = None
	fidFinderBoxSize = None
	queueData = False
	calibrating = False
	applyCalibration = False
	sdl2.SDL_Init(sdl2.SDL_INIT_TIMER)
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	window = sdl2.ext.Window("test", size= (camRes[0]/monitorResize,camRes[1]/monitorResize),position=(0,0),flags=sdl2.SDL_WINDOW_SHOWN)#|sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)#sdl2.SDL_WINDOW_BORDERLESS)window.show()
	window.refresh()
	sdl2.SDL_PumpEvents()
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	windowArray = sdl2.ext.pixels3d(windowSurf.contents)
	sdl2.sdlttf.TTF_Init()
	font = sdl2.sdlttf.TTF_OpenFont('pyTracker/DejaVuSans.ttf', camRes[1]/monitorResize/10)
	vc = cv2.VideoCapture(camIndex)
	vc.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,camRes[0]) #set the width resolution
	vc.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,camRes[1]) #set the height resolution
	lastImageTime = getTime()
	while True:
# 		try:
# 			os.nice(-20)
# 		except:
# 			pass
		thisVelocity = None
		thisRadius = None
		t1 = getTime()
		junk,image = vc.read()
		t2 = getTime()
		imageTime = t1+(t2-t1)/2
		timeSinceLastImage = imageTime-lastImageTime
		lastImageTime = imageTime
		grayImage = image[:,:,2]#numpy.copy(image[:,:,2])
		for dotName in dotDict:
			if dotName=='fid':
				dotDict[dotName].update(img=grayImage,imageTime=imageTime)
			elif len(dotDict)==3:
				if dotName=='left':
					dotDict[dotName].update(img=grayImage,imageTime=imageTime,fid=dotDict['fid'],other=dotDict['right'])
				elif dotName=='right':
					dotDict[dotName].update(img=grayImage,imageTime=imageTime,fid=dotDict['fid'],other=dotDict['left'])
			else:
				dotDict[dotName].update(img=grayImage,imageTime=imageTime,fid=dotDict['fid'])
		if len(dotDict)==3:
			if (not dotDict['left'].lost) and (not dotDict['right'].lost):
				thisRadius = ((dotDict['left'].radius2+dotDict['right'].radius2)/2.0)*fidSizeInmm
				thisVelocity = math.degrees(math.atan(((dotDict['left'].velocity+dotDict['right'].velocity)/2.0)*fidSizeInmm/12.0))/dotDict['left'].dt
			elif (not dotDict['left'].lost):
				thisRadius = dotDict['left'].radius2*fidSizeInmm
				thisVelocity = math.degrees(math.atan(dotDict['left'].velocity*fidSizeInmm/12.0))/dotDict['left'].dt
			elif (not dotDict['right'].lost):
				thisRadius = dotDict['right'].radius2*fidSizeInmm
				thisVelocity = math.degrees(math.atan(dotDict['right'].velocity*fidSizeInmm/12.0))/dotDict['right'].dt
		if doSounds:
			if len(dotDict)==3:
				if dotDict['left'].blink or dotDict['right'].blink:
					if not blinkSoundPlaying:
						blinkSoundPlaying = True
						blinkSound = ReadAIFF('pyTracker/stop.aif')
						blinkSoundSpec = sdl2.SDL_AudioSpec(blinkSound.a.getframerate(),sdl2.AUDIO_S16MSB,blinkSound.a.getnchannels(),2**13,sdl2.SDL_AudioCallback(blinkSound.playNextChunk))
						blinkSoundDevID = sdl2.SDL_OpenAudioDevice(None, 0, blinkSoundSpec, None, 0)
						sdl2.SDL_PauseAudioDevice(blinkSoundDevID, 0)
				if thisVelocity>600:
					if not saccadeSoundPlaying:
						saccadeSoundPlaying = True
						saccadeSound = ReadAIFF('pyTracker/beep.aif')
						saccadeSoundSpec = sdl2.SDL_AudioSpec(saccadeSound.a.getframerate(),sdl2.AUDIO_S16MSB,saccadeSound.a.getnchannels(),2**13,sdl2.SDL_AudioCallback(saccadeSound.playNextChunk))
						saccadeSoundDevID = sdl2.SDL_OpenAudioDevice(None, 0, saccadeSoundSpec, None, 0)
						sdl2.SDL_PauseAudioDevice(saccadeSoundDevID, 0)
			if blinkSoundPlaying:
				if blinkSound.done.isSet():
					blinkSoundPlaying = False
					sdl2.SDL_CloseAudioDevice(blinkSoundDevID)
					del blinkSound
					del blinkSoundDevID
					del blinkSoundSpec
			if saccadeSoundPlaying:
				if saccadeSound.done.isSet():
					saccadeSoundPlaying = False
					sdl2.SDL_CloseAudioDevice(saccadeSoundDevID)
					del saccadeSound
					del saccadeSoundDevID
					del saccadeSoundSpec				
		if showPlot:
			if len(dotDict)==3:
				radiusList.append(thisRadius)
				velocityList.append(thisVelocity)
				timeList.append(imageTime)
		if calibrating:
			if (not dotDict['left'].lost) and (not dotDict['right'].lost):
				obsX = (dotDict['left'].x2+dotDict['right'].x2)/2.0
				obsY = (dotDict['left'].y2+dotDict['right'].y2)/2.0
				calibrationData.append([calibrationExpected,[obsX,obsY]])
		if not qTo.empty():
			message = qTo.get()
			if message[0]=='quit':
				sys.exit()
			elif message[0]=='doSounds':
				doSounds = message[1]
			elif message[0]=='queueData':
				queueData = message[1]
			elif message[0]=='calibrationPause':
				calibrating = False
			elif message[0]=='newCalibrationCoords':
				calibrationExpected = message[1]
				calibrating = True
			elif message[0]=='calibrationStart':
				# calibrating = True
				calibrationData = []
				# calibrationExpected = message[1]
			elif message[0]=='calibrationDone':
				calibrating = False
				calibrationData = numpy.array(calibrationData)
				exp = calibrationData[:,0]
				obs = calibrationData[:,1]
				# xFit = scipy.interpolate.bisplrep(obs[:,0],obs[:,1],exp[:,0])
				# yFit = scipy.interpolate.bisplrep(obs[:,0],obs[:,1],exp[:,1])
				xFit = numpy.polyfit(obs[:,0],exp[:,0],2)
				yFit = numpy.polyfit(obs[:,1],exp[:,1],2)
				xError = numpy.polyval(xFit,obs[:,0])-exp[:,0]
				yError = numpy.polyval(yFit,obs[:,1])-exp[:,1]
				# xError = getError(obs,exp[:,0],xFit)
				# yError = getError(obs,exp[:,1],yFit)
				xSTD = numpy.std(xError)
				ySTD = numpy.std(yError)
				totError = numpy.mean(((xError**2)+(yError**2))**.5)
				qFrom.put(['calibrationError',[totError,xSTD,ySTD]])
			elif message[0]=='validationStart':
				# calibrating = True
				calibrationData = []
			elif message[0]=='validationDone':
				calibrating = False
				calibrationData = numpy.array(calibrationData)
				exp = calibrationData[:,0]
				obs = calibrationData[:,1]
				# xError = getError(obs,exp[:,0],xFit)
				# yError = getError(obs,exp[:,1],yFit)
				xError = numpy.polyval(xFit,obs[:,0])-exp[:,0]
				yError = numpy.polyval(yFit,obs[:,1])-exp[:,1]
				xSTD = numpy.std(xError)
				ySTD = numpy.std(yError)
				totError = numpy.mean(((xError**2)+(yError**2))**.5)
				qFrom.put(['validationError',[totError,xSTD,ySTD]])
		if queueData and (len(dotDict)==3):
			qFrom.put([imageTime,thisVelocity,thisRadius,dotDict['left'].blink|dotDict['right'].blink])
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				response = sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()
				if response=='escape':
					sys.exit()
				if response=='space':
					showImage = 1-showImage
				if response=='q':
					qFrom.put('points acquired')
				if response=='s':
					doSounds = True
				if response=='p':
					showPlot = 1-showPlot
					radiusList = []
					radiusMax = 0
					radiusMin = 0#9999999
					velocityList = []
					velocityMax = 0
					velocityMin = 0#9999999
					timeList = []
				if response=='f':
					clickingFor = 'fid'
					if clickingFor in dotDict:
						del dotDict
						dotDict = {}
					definingFidFinderBox = False
				if response=='l':
					clickingFor = 'left'
					if clickingFor in dotDict:
						del dotDict[clickingFor]
					definingFidFinderBox = False
				if response=='r':
					clickingFor = 'right'
					if clickingFor in dotDict:
						del dotDict[clickingFor]
					definingFidFinderBox = False
			if event.type==sdl2.SDL_MOUSEMOTION:
				if definingFidFinderBox:
					fidFinderBoxSize = abs(fidFinderBoxX - (window.size[0]-event.button.x) )
			if event.type==sdl2.SDL_MOUSEBUTTONDOWN:
				if clickingFor=='fid':
					if not definingFidFinderBox:
						definingFidFinderBox = True
						fidFinderBoxX = window.size[0]-event.button.x
						fidFinderBoxY = event.button.y
					else:
						definingFidFinderBox = False
						fidFinderBoxSize = abs(fidFinderBoxX - (window.size[0]-event.button.x) )
						x1 = ( ( fidFinderBoxX - fidFinderBoxSize ) ) * monitorResize
						y1 = ( fidFinderBoxY - fidFinderBoxSize ) * monitorResize
						x2 = ( ( fidFinderBoxX + fidFinderBoxSize ) ) * monitorResize
						y2 = ( fidFinderBoxY + fidFinderBoxSize ) * monitorResize
						newDot = dotObj(x1=x1,y1=y1,x2=x2,y2=y2,img=grayImage,imageTime=imageTime,name=clickingFor)
						if not newDot.lost:
							dotDict[clickingFor] = newDot
						clickingFor = None	
				if clickingFor in ['left','right']:
					clickX = (window.size[0]-event.button.x)*monitorResize
					clickY = event.button.y*monitorResize
					x1 = clickX-dotDict['fid'].radius*5
					y1 = clickY-dotDict['fid'].radius*5
					x2 = clickX+dotDict['fid'].radius*5
					y2 = clickY+dotDict['fid'].radius*5
					newDot = dotObj(x1=x1,y1=y1,x2=x2,y2=y2,img=grayImage,imageTime=imageTime,name=clickingFor,fid=dotDict['fid'])
					if not newDot.lost:
						dotDict[clickingFor] = newDot
					clickingFor = None	
		if showImage==1:
			for dotName in dotDict:
				dot = dotDict[dotName]
				if dot.blink:
					pass
					# if dot.ellipse!=None:
						# cv2.ellipse(image, dot.ellipse, (0,0,255), 2)
				else:
					if not dot.lost:
						if dot.ellipse!=None:
							cv2.ellipse(image, dot.ellipse, (0,255,0), 2)
			image = cv2.resize(image,dsize=(camRes[0]/monitorResize,camRes[1]/monitorResize),interpolation=cv2.INTER_NEAREST)
			if definingFidFinderBox:
				if fidFinderBoxSize!=None:
					cv2.circle(image,(fidFinderBoxX,fidFinderBoxY),fidFinderBoxSize,color=(255,0,0,255),thickness=2)
			image = numpy.rot90(image) #rotate dims
			windowArray[:,:,0:3] = image
		else:
			blankArray = numpy.zeros((camRes[0]/monitorResize,camRes[1]/monitorResize,4),numpy.uint8)
			numpy.copyto(windowArray,blankArray)
		hzList.append(timeSinceLastImage*1000)
		if len(hzList)>30:
			hzList.pop(0)
		if showPlot:
			if len(timeList)>1:
				if (thisVelocity!=None) and (thisRadius!=None):
					image = windowArray[:,:,0:3]
					image = numpy.rot90(image,3).copy()

					timeSlope = (camRes[0]/monitorResize/10)-1
					timeIntercept = ((camRes[0]/monitorResize)-1)-timeSlope*timeList[-1]
					timePxArray = numpy.floor(timeSlope*numpy.array(timeList)+timeIntercept)
					timeSelection = timePxArray>=0
					timePxArray = timePxArray[timeSelection]
					timePxArray = ((camRes[0]/monitorResize)-1) - timePxArray
					timeList = timeList[(len(timeList)-len(timePxArray)):len(timeList)]

					radiusPxArray = numpy.array(radiusList)
					radiusPxArray = radiusPxArray[timeSelection]
					radiusList = radiusList[(len(radiusList)-len(radiusPxArray)):len(radiusList)]
					
					velocityPxArray = numpy.array(velocityList)
					velocityPxArray = velocityPxArray[timeSelection]
					velocityList = velocityList[(len(velocityList)-len(velocityPxArray)):len(velocityList)]

					dataSelection = numpy.array([ (velocityPxArray[i]!=None) and (radiusPxArray[i]!=None) for i in range(len(velocityPxArray))])
					timePxArray = timePxArray[dataSelection]
					velocityPxArray = velocityPxArray[dataSelection]
					radiusPxArrayOrig = radiusPxArray
					radiusPxArray = radiusPxArray[dataSelection]					
					
# 					if numpy.min(radiusPxArray)<radiusMin:
# 						radiusMin = numpy.min(radiusPxArray)
# 					radiusPxArray = radiusPxArray-radiusMin
					if numpy.max(radiusPxArray)>radiusMax:
						radiusMax = numpy.max(radiusPxArray)
					radiusPxArray = numpy.floor(numpy.array(radiusPxArray/radiusMax*((camRes[1]/monitorResize)-1),numpy.float64))
					radiusPxArray = ((camRes[1]/monitorResize)-1) - radiusPxArray
					# radiusPts = numpy.array(numpy.column_stack((timePxArray,radiusPxArray)),numpy.int32)
					radiusPts = numpy.array([[x_, y_] for x_, y_ in zip(timePxArray,radiusPxArray)],numpy.int32)
					# cv2.polylines(img=image,pts=radiusPts,isClosed=False,color=(255,0,0),thickness=2)
					for i in xrange(len(radiusPts)-1):
						cv2.line(image,tuple(radiusPts[i]),tuple(radiusPts[i+1]), (255,0,0),2)
			
# 					if numpy.min(velocityPxArray)<velocityMin:
# 						velocityMin = numpy.min(velocityPxArray)
# 					velocityPxArray = velocityPxArray-velocityMin
					if numpy.max(velocityPxArray)>velocityMax:
						velocityMax = numpy.max(velocityPxArray)
					velocityPxArray = numpy.floor(numpy.array(velocityPxArray/velocityMax*((camRes[1]/monitorResize)-1),numpy.float64))
					velocityPxArray = ((camRes[1]/monitorResize)-1) - velocityPxArray
					# velocityPts = numpy.array(numpy.column_stack((timePxArray,velocityPxArray)))
					velocityPts = numpy.array([[x_, y_] for x_, y_ in zip(timePxArray,velocityPxArray)],numpy.int32)
					# cv2.polylines(img=image,pts=velocityPts,isClosed=False,color=(0,0,255),thickness=2)
					for i in xrange(len(velocityPts)-1):
						cv2.line(image,tuple(velocityPts[i]),tuple(velocityPts[i+1]), (0,0,255),2)

					image = numpy.rot90(image)
					windowArray[:,:,0:3] = image
					radiusSurf = sdl2.sdlttf.TTF_RenderText_Blended_Wrapped(font,str(int(radiusMax*100)),sdl2.pixels.SDL_Color(r=0, g=0, b=255, a=255),window.size[0]).contents
					velocitySurf = sdl2.sdlttf.TTF_RenderText_Blended_Wrapped(font,str(int(velocityMax)),sdl2.pixels.SDL_Color(r=255, g=0, b=0, a=255),window.size[0]).contents
					sdl2.SDL_BlitSurface(radiusSurf, None, windowSurf, sdl2.SDL_Rect(windowSurf.contents.w-radiusSurf.w,0,radiusSurf.w,radiusSurf.h))
					sdl2.SDL_BlitSurface(velocitySurf, None, windowSurf, sdl2.SDL_Rect(windowSurf.contents.w-velocitySurf.w,radiusSurf.h,velocitySurf.w,velocitySurf.h))
# 					velocitySurf = sdl2.sdlttf.TTF_RenderText_Blended_Wrapped(font,str(int(thisVelocity)),sdl2.pixels.SDL_Color(r=255, g=0, b=0, a=255),window.size[0]).contents
# 					radiusSurf = sdl2.sdlttf.TTF_RenderText_Blended_Wrapped(font,str(int(thisRadius*100)),sdl2.pixels.SDL_Color(r=0, g=0, b=255, a=255),window.size[0]).contents
# 					sdl2.SDL_BlitSurface(velocitySurf, None, windowSurf, sdl2.SDL_Rect(windowSurf.contents.w-velocitySurf.w,windowSurf.contents.h-velocitySurf.h-radiusSurf.h,velocitySurf.w,velocitySurf.h))
# 					sdl2.SDL_BlitSurface(radiusSurf, None, windowSurf, sdl2.SDL_Rect(windowSurf.contents.w-radiusSurf.w,windowSurf.contents.h-velocitySurf.h,radiusSurf.w,radiusSurf.h))
					sdl2.SDL_UpdateWindowSurface(window.window)

		timeSurf = sdl2.sdlttf.TTF_RenderText_Blended_Wrapped(font,str(int(numpy.mean(hzList)))+ '\r'+str(int(numpy.std(hzList))),sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255),window.size[0]).contents
		sdl2.SDL_BlitSurface(timeSurf, None, windowSurf, sdl2.SDL_Rect(0,0,timeSurf.w,timeSurf.h))
		sdl2.SDL_UpdateWindowSurface(window.window)
		window.refresh()
		sdl2.SDL_PumpEvents()
