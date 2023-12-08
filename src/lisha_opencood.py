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

        
    	def get_IMU_iot_api(self):
        
	        IMU_Accel_x = []
	        IMU_Accel_y = []
	        IMU_Accel_z = []
	        IMU_Rotation_x = []
	        IMU_Rotation_y = []
	        IMU_Rotation_z = []
	        IMU_Gyro_x = []
	        IMU_Gyro_y = []
	        IMU_Gyro_z = []
	        IMU_Compass = []
	        
	        raw_data_ax = self.make_request(0xC4962924,0)
	        raw_data_ay = self.make_request(0xC4962924,1)
	        raw_data_az = self.make_request(0xC4962924,2)
	        raw_data_rx = self.make_request(0xC4B24924,0)
	        raw_data_ry = self.make_request(0xC4B24924,1)
	        raw_data_rz = self.make_request(0xC4B24924,2)
	        raw_data_wx = self.make_request(0xC4B23924,0)
	        raw_data_wy = self.make_request(0xC4B23924,1)
	        raw_data_wz = self.make_request(0xC4B23924,2)
	        raw_data_C = self.make_request(0xC4B24924,3)
	        
	        if (len(raw_data) > 0):
	            for i in range(len(raw_data)-1):
	                IMU_Accel_x = raw_data_ax[i]['value']
	                IMU_Accel_y = raw_data_ay[i]['value']
	                IMU_Accel_z = raw_data_az[i]['value']
	                IMU_Rotation_x = raw_data_rx[i]['value']
	                IMU_Rotation_y = raw_data_rx[i]['value']
	                IMU_Rotation_z = raw_data_rx[i]['value']
	                IMU_Gyro_x = raw_data_wx[i]['value']
	                IMU_Gyro_y = raw_data_wx[i]['value']
	                IMU_Gyro_z = raw_data_wx[i]['value']
	                IMU_Compass = raw_data_C [i]['value']
	        
	        return IMU_Accel_x, IMU_Accel_y, IMU_Accel_z, IMU_Rotation_x , IMU_Rotation_y,IMU_Rotation_z ,IMU_Gyro_x,IMU_Gyro_y,IMU_Gyro_z,IMU_Compass
	        
	                
