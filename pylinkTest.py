stimDisplayRes = [1920,1080]

import pylink
eyelink = pylink.EyeLink('100.1.1.1')
eyelink.sendCommand('select_parser_configuration 0')# 0--> standard (cognitive); 1--> sensitive (psychophysical)
eyelink.sendCommand('sample_rate 2000')
eyelink.setLinkEventFilter("SACCADE,BLINK")
eyelink.openDataFile('ssior.edf')
eyelink.sendCommand("screen_pixel_coords =  0 0 %d %d" %(stimDisplayRes[0],stimDisplayRes[1]))
eyelink.sendMessage("DISPLAY_COORDS  0 0 %d %d" %(stimDisplayRes[0],stimDisplayRes[1]))
eyelink.sendCommand("saccade_velocity_threshold = 35")
eyelink.sendCommand("saccade_acceleration_threshold = 9500")
eyelink.doTrackerSetup()

while True:
	eyeData = eyelink.getNextData()
	if (eyeData==pylink.STARTSACC) or (eyeData==pylink.STARTBLINK):
		eyeEvent = eyelink.getFloatData()
		if isinstance(eyeEvent,pylink.StartSaccadeEvent):
			print 'Saccade started'
		elif isinstance(eyeEvent,pylink.StartBlinkEvent):
			print 'Blink started'
