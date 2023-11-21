import requests
import numpy as np

class ImuMock():

	def __init__(self) -> None:

		self.request_body = {
				"series" : {
					"version": "1.2",
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
			
			if (len(data["series"]) > 0):
				return data["series"][0]["value"]
			else:
				return []
		

	def get_gps_iot_api(self, t0, t1):

		latitude = []
		longitude = []
  
		raw_latitude = self.make_request(3300018468, t0, t1, 3)
		raw_longitude = self.make_request(3300018468, t0, t1, 4)
  
		if (raw_latitude != [] and raw_latitude != None):
			latitude = raw_latitude * (180/3.14)
			longitude = raw_longitude * (180/3.14)
  
		return latitude, longitude