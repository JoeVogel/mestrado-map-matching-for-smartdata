import requests
import numpy as np
from motionVector import MotionVector

class ImuMock():

	def __init__(self, type="local") -> None:

		if (type == "local"):

			self.motion_vector_list = []

			self.data = np.load('./datasets/2023-09-29 20-12-25.874768.npy')

			self.time_list 				= self.data[:,0]
			self.yaw_pitch_roll_list	= self.data[:,3:6]
			self.lat_long_alt_list 		= self.data[:,6:9]
			self.velocity_list 			= self.data[:,9:12]

			for i in range(len(self.lat_long_alt_list)):
				velocity = np.sqrt(self.velocity_list[i,:] @ self.velocity_list[i,:].T)
				yaw = np.deg2rad(self.yaw_pitch_roll_list[i,0])
				a_abs = 0
				yaw_rate = 0
				pos = {
					"latitude" : self.lat_long_alt_list[i,0],
					"longitude" : self.lat_long_alt_list[i,1],
					"altitude" : self.lat_long_alt_list[i,2]
				}

				new_motion_vector = MotionVector()

				new_motion_vector.timestamp = self.time_list[i]
				new_motion_vector.pos = pos
				new_motion_vector.speed = velocity
				new_motion_vector.heading = yaw				

				if i > 0:
					dt = self.time_list[i]-self.time_list[i-1]
					a_ned = (self.velocity_list [i,:]-self.velocity_list [i-1,:])/dt
					a_abs = np.sqrt(a_ned @ a_ned.T)
					yaw_rate = (yaw - np.deg2rad(self.yaw_pitch_roll_list[i-1,0]))/dt
				
				new_motion_vector.acceleration = a_abs
				new_motion_vector.yaw_rate = yaw_rate
				
				self.motion_vector_list.append(new_motion_vector)

		elif (type == "api"):

			self.motion_vector = MotionVector()

			self.request_body = {
					"series" : {
						"version": "1.2",
						# "unit": 3298175268, 
						# "t0": 1533906414544846,
						# "t1": 1533906414544847,
						# "dev": 1,
						"signature": 1
					},
					"credentials" : {
						"domain": "a2d2",
							"username": "a2d2",
							"password": "hG2847#4ABlvx962"
					}
				}


	def make_request(self, unit, t0, t1, dev):
	
		self.request_body["series"]["unit"] = unit
		self.request_body["series"]["t0"] = t0
		self.request_body["series"]["t1"] = t1
		self.request_body["series"]["dev"] = dev

		r = requests.get('https://iot.ufsc.br/api/get.php', json=self.request_body)

		if (r.status_code == 200):

			data = r.json()
			# adicionado [0] pois algumas vezes o dado vem duplicado
			return data["series"][0]
		
	'''
		Funtion to generate the motion vector
		
		Configurations for GET data from IoT UFSC:
		# Acceleration unit=3298175268, dev=0
		# IMU Rotation 3300018468
		# IMU Angular Velocity 3300014372
		# GPS "unit" : 3300018468, long=dev=3, lat=dev=4
		 
	'''
	def get_motion_vector_iot_api(self) -> MotionVector:

		position = {"latitude": "0", "longitude": "0", "altitude": "0"}
		speed = 0
		heading = 0
		yaw_rate = 0
		acceleration = 0
		orientation = 0
		timestamp = 0

		# Comentado por erro na API
		# data = self.make_request(3300018468, 1533906414544846, 1533906414544847, 4)
		# position["latitude"] = data["latitude"] 
		position["latitude"] = ""

		# Comentado por erro na API
		# data = self.make_request(3300018468, 1533906414544846, 1533906414544847, 3)
		# position["longitude"] = data["longitude"]
		position["longitude"] = ""

		data = self.make_request(3298175268, 1533906414544846, 1533906414544847, 0)
		speed = data["value"]

		data = self.make_request(3298175268, 1533906414544846, 1533906414544847, 0)
		acceleration = data["value"]

		# TODO: implementar o restante das solicitações quando a API estiver pronta

		return self.motion_vector
	