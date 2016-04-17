stimDisplayRes = (800,600)
stimDisplayPosition = (0,0)

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
import sdl2 #for input and display

byteify = lambda x, enc: x.encode(enc)


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
		self.Window = sdl2.video.SDL_CreateWindow(byteify('stimDisplay', "utf-8"),self.stimDisplayPosition[0],self.stimDisplayPosition[1],self.stimDisplayRes[0],self.stimDisplayRes[1],sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
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



stimDisplay = stimDisplayClass(stimDisplayRes=stimDisplayRes,stimDisplayPosition=stimDisplayPosition)#,stimDisplayMirrorChild=stimDisplayMirrorChild)

def drawSquare(xOffset,size):
	gl.glColor3f(.5,.5,.5)
	outer = size
	xOffset = stimDisplayRes[0]/2+xOffset
	yOffset = stimDisplayRes[1]/2
	# gl.glBegin(gl.GL_QUAD_STRIP)
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset-outer/2 , yOffset-outer/2 )
	gl.glVertex2f( xOffset-outer/2 , yOffset+outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset+outer/2 )
	gl.glEnd()
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset-outer/2 , yOffset-outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset-outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset+outer/2 )
	gl.glEnd()


def drawDiamond(xOffset,size):
	gl.glColor3f(.25,.25,.25)
	outer = math.sqrt((size**2)*2)
	xOffset = stimDisplayRes[0]/2 + xOffset
	yOffset = stimDisplayRes[1]/2
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset , yOffset-outer/2 )
	gl.glVertex2f( xOffset-outer/2 , yOffset )
	gl.glVertex2f( xOffset , yOffset+outer/2 )
	gl.glEnd()
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset , yOffset-outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset )
	gl.glVertex2f( xOffset , yOffset+outer/2 )
	gl.glEnd()

drawSquare(0,100)
drawDiamond(0,100)
stimDisplay.refresh()
time.sleep(3)