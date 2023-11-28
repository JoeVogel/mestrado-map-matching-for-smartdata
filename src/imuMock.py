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
				return data["series"]
			else:
				return []
		

	def get_gps_iot_api(self, t0, t1):

		latitude = []
		longitude = []
  
		points = {'latitude':[], 'longitude':[]}
  
		raw_latitude = self.make_request(3300018468, t0, t1, 3)
  
		if (len(raw_latitude) > 0):
    
			for i in range(len(raw_latitude)-1):
				points["latitude"].append(raw_latitude[i]['value'] * (180/np.pi))
  
			raw_longitude = self.make_request(3300018468, t0, t1, 4)
   
			for j in range(len(raw_longitude)-1):
				points["longitude"].append(raw_longitude[j]['value'] * (180/np.pi))
  
		return points