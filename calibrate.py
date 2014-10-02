if __name__ == '__main__':
	import time
	import pyCalibrate
	import pyStamper
	stamper = pyStamper.stamperClass()
	stamper.start(windowSize=[200,200],windowPosition=[1366,0])
	calibrator = pyCalibrate.calibrationClass()
	calibrator.timestampMethod = 0
	calibrator.viewingDistance = 53.0
	calibrator.stimDisplayWidth = 59.5
	calibrator.stimDisplayRes = [1920,1080]
	calibrator.stimDisplayPosition = [2560,0]
	calibrator.mirrorDisplayPosition = [0,0]
	calibrator.mirrorDownSize = 2
	calibrator.manualCalibrationOrder = False
	calibrator.calibrationDotSizeInDegrees = 1
	calibrator.qTo = stamper.qFrom
	calibrator.start()
	while calibrator.process.is_alive():
		pass
