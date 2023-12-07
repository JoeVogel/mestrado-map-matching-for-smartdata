import requests
import numpy as np

class LishaOpenCood():

	def __init__(self) -> None:

		self.request_body = {
				"series" : {
					"version": "1.2",
					"signature": 641,
     				"x": 0,
              	    "y": 0,
                    "z": 0,
                    "r": 1000,
                    "workflow": 0            
				},
				"credentials" : {
					"domain": "opencood",
					"username": "opencood",
					"password": "A7B64D415BD3E9AA"
				}
			}


	def make_request(self, unit, dev):
	
		self.request_body["series"]["unit"] = unit
		self.request_body["series"]["dev"] = dev

		r = requests.get('https://iot.lisha.ufsc.br/api/get.php', json=self.request_body)

		if (r.status_code == 200):

			data = r.json()
			
			if (len(data["series"]) > 0):
				return data["series"]
			else:
				return []
		

	def get_gps_iot_api(self):

		latitude = []
		longitude = []
  
		points = {'latitude':[], 'longitude':[]}
  
		raw_data = self.make_request(3298175268, 0)
  
		if (len(raw_data) > 0):
    
			for i in range(len(raw_data)-1):
				points["latitude"].append(raw_data[i]['x'] * (180/np.pi))
				points["latitude"].append(raw_data[i]['y'] * (180/np.pi))
  
		return points