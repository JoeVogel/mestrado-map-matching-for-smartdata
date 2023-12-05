#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from kalmanFilter_positionOnly_Final import kalmanFilter
from helperMethods import helperMethods

import pandas as pd
from ahrs import DCM
from ahrs.filters import Mahony
import numpy



# Import sensor data
#data = numpy.genfromtxt("sensor_data.csv", delimiter=",", skip_header=1)
#dados_1 = pd.read_csv("2023-11-2920.03.38.csv",delimiter=";",decimal=',')[50:]
dados_1 = pd.read_csv("2023-11-2919.59.50.csv",delimiter=";",decimal=',')[50:]
#dados_1 = pd.read_excel("2023-11-2912.42.38.xlsx",decimal=',',header=1)

sample_rate = int(100) # 100 Hz


timestamp = dados_1.time.values[50:]
gyroscope = dados_1[['wx','wy','wz']].values[50:]
accelerometer = dados_1[['gFx','gFy','gFz']].values[50:]
magnetometer = dados_1[['Bx','By','Bz']].values[50:]
GPS = dados_1[['Latitude','Longitude']].values[50:]
YPR = dados_1[['Azimuth','Pitch','Roll']].values[50:]

#tratando os dados de GPS
prev_GPS = 0
k = 0
for i in range(len(GPS[:,0])):
    if GPS[i,0] == prev_GPS and k < 120:
        GPS[i,0] = 0
        GPS[i,1] = 0
        k += 1
    else:
        prev_GPS = GPS[i,0]
        k = 0

# Instantiate algorithms

orientation = Mahony()


Q = np.tile([1., 0., 0., 0.], (len(gyroscope), 1)) # Allocate for quaternions
  
#Adiciona as configurações da fusão GPS e IMU
GPS_STD = np.array([2,2]).reshape((2,1))
#acc_STD = ACTUAL_GRAVITY*np.array([0.05355371135598354,0.033436506994600976,0.2088683796078286]).reshape((3,1))
acc_STD = 9.806*np.array([0.05355371135598354,0.033436506994600976]).reshape((2,1))

# create object of helper class
helperObj = helperMethods()

# create objects of kalman filter
initial_pos = [GPS[0,0],GPS[0,1]]

obj = kalmanFilter(helperObj.point2Mtrs(initial_pos), \
                   GPS_STD, acc_STD,timestamp[0])


# Process sensor data
delta_time = numpy.diff(timestamp, prepend=timestamp[0])

euler = numpy.empty((len(timestamp), 3))

orgLat = []
orgLon = []
# lists for collecting final points to plot
pointsToPlotLat = []
pointsToPlotLon = []

#ahrs.update(gyroscope[0], accelerometer[0], magnetometer[0], delta_time[0])

for i in range(1,len(timestamp)):
    
    Q[i] = orientation.updateMARG(Q[i-1], gyr=gyroscope[i], acc=accelerometer[i], mag=magnetometer[i], )

    R = DCM()
      
    Rotation = R.from_quaternion(Q[i])
    R = DCM(Rotation)
    euler[i] = R.to_angles()
    
    lin_accel = ((Rotation@accelerometer[i].T - numpy.array([0,0,1]).T)*9.806).T
    
    if i > 0:
        acc = lin_accel[:2]

        obj.predict(acc.reshape((2,1)), timestamp[i])
        
        if(GPS[i,0] != 0.0):
            
          curr_pos = [GPS[i,0],GPS[i,1]]
          defPosErr = np.zeros(len(curr_pos))
          
          point = obj.point2Mtrs(curr_pos)
          obj.update(point, defPosErr)
          
          orgLat.append(GPS[i,0])
          orgLon.append(GPS[i,1])
                    
        PredictedPoint = obj.getPredictedPos()
        predictedLatMtrs, predictedLonMtrs = PredictedPoint[:2]
        predictedLat, predictedLon = helperObj.mtrsToGeopoint(predictedLatMtrs,predictedLonMtrs)
          
        predictedVN, predictedVE = obj.getPredictedVel()[:2]
          
        resultantV = np.sqrt(np.power(predictedVE, 2) + np.power(predictedVN, 2))*3.6
        deltaT = timestamp[i] -timestamp[0]
        
        accel = np.sqrt(acc @ acc.T);
        if i > 0:
            YawRate = (euler[i,2]- euler[i-1,2])/(timestamp[i]-timestamp[i-1]);
        else:
            YawRate = 0
        
        print("\nTime: {} seconds in\nLat: {}\nLon: {}\nVel(km/h): {}\nAccel: {}\nYaw(º): {},\nYawRate: {}\n".format(
                 deltaT, predictedLat, predictedLon, resultantV, accel, euler[i,2], YawRate))
        #print(f'Yaw: {euler[i,2]} º') 
        # append predicted points to list
        pointsToPlotLat.append(predictedLat)
        pointsToPlotLon.append(predictedLon)

    
plt.subplot(2,1,1)
plt.title('Original')
plt.plot(orgLon,orgLat)

plt.subplot(2,1,2)
plt.title('Fused')
plt.plot(pointsToPlotLon, pointsToPlotLat)

plt.show()

plt.figure()
plt.plot(timestamp,euler[:,2])
plt.figure()
plt.plot(timestamp,YPR[:,0])
