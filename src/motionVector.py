
class MotionVector:

	def __init__(self) -> None:
		self.pos = {"latitude": "0", "longitude": "0", "altitude": "0"}
		self.speed = 0
		self.acceleration = 0
		self.yaw_rate = 0
		self.heading = 0
		self.timestamp = 0 

	def set_motion_vector(self, pos, speed, acceleration, yaw_rate, heading, timestamp) -> None:
		self.pos = pos
		self.speed = speed
		self.acceleration = acceleration
		self.yaw_rate = yaw_rate
		self.heading = heading
		self.timestamp = timestamp