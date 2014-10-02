import billiard
billiard.forking_enable(0)

from . import calibrationLoop


########
# Define a class that spawns a new process to manage the camera, do tracking and display a preview window
########
class calibrationClass:
	def __init__(self):
		self.timestampMethod = None
		self.viewingDistance = None
		self.stimDisplayWidth = None
		self.stimDisplayRes = None
		self.stimDisplayPosition = None
		self.mirrorDisplayPosition = None
		self.mirrorDownSize = None
		self.calibrationDotSizeInDegrees = .25
		self.manualCalibrationOrder = False
		self.qTo = billiard.Queue()
		self.qFrom = billiard.Queue()
		self.started = False
	def start(self):
		if not self.started:
			self.process = billiard.Process( target=calibrationLoop.loop , args=(self.qTo,self.qFrom,self.timestampMethod,self.viewingDistance,self.stimDisplayWidth,self.stimDisplayRes,self.stimDisplayPosition,self.mirrorDisplayPosition,self.mirrorDownSize,self.calibrationDotSizeInDegrees,self.manualCalibrationOrder) )
			self.process.start()
			self.started = True
	def stop(self):
		if self.started:
			self.qTo.put('quit')
			self.process.join(timeout=1)
			if self.process.is_alive():
				self.process.terminate()
		return None

