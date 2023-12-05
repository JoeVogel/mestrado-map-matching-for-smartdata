#!/usr/bin/env python
import numpy as np
from helperMethods import helperMethods

class kalmanFilter(helperMethods):
  '''
  Kalman Filter class fuses the data from GPS and IMU.
  The predict and update functions play the most vital role.
  '''
  def __init__(self, initPos, posStdDev, accStdDev, currTime):
    helperMethods.__init__(self)
    # set these values from the arguments r♥eceived
    # current state
    self.X = np.concatenate((np.float64(initPos), np.zeros((len(initPos),1))))
    # Identity matrix
    self.I = np.identity(len(self.X))
    # Initial guess for covariance
    self.P = np.identity(len(self.X))
    # transformation matrix for input data
    self.H = np.pad(np.identity(len(initPos)),((0,0),(0,len(initPos))))
    # process (accelerometer) error variance
    self.Q = np.identity(len(self.X))*np.concatenate((accStdDev**2,accStdDev**2))
    # measurement (GPS) error variance
    self.R = np.identity(len(initPos))*posStdDev**2
    # current time
    self.currStateTime = currTime
    # self.A = defined in predict
    # self.B = defined in predict
    # self.u = defined in predict
    # self.z = defined in update

  # main functions
  def predict(self, accThisAxis, timeNow):
    '''
    Predict function perform the initial matrix multiplications.
    Objective is to predict current state and compute P matrix.
    '''
    deltaT = timeNow - self.currStateTime
    self.B = np.ones(self.X.shape)* \
        np.concatenate((0.5 * deltaT * deltaT*np.ones((int(len(self.X)/2),1)) \
                        , deltaT*np.ones((int(len(self.X)/2),1))))
    self.A = np.identity(len(self.X))+np.eye(len(self.X),k=int(len(self.X)/2))*deltaT
    self.u = np.concatenate((accThisAxis,accThisAxis))

    self.X = np.add(np.matmul(self.A, self.X), self.B * self.u)
    self.P = np.add(np.matmul(np.matmul(self.A, self.P), np.transpose(self.A)), self.Q)
    self.currStateTime = timeNow

  def update(self, pos, posError):
    '''
    Update function performs the update when the GPS data has been
    received. 
    '''
    self.z = np.array(pos)
    if(not posError.any()):
      self.R = np.identity(len(pos))*posError**2
    y = np.subtract(self.z, self.H @ self.X)
    s = np.add(self.H @ self.P @ self.H.T, self.R)
    try:
      sInverse = np.linalg.inv(s)
    except np.linalg.LinAlgError:
      print("Matrix is not invertible")
      pass
    else:
      K = self.P @ self.H.T @ sInverse;
      self.X = np.add(self.X, np.matmul(K, y))
      self.P = np.matmul(np.subtract(self.I, K@self.H), self.P)

  def getPredictedPos(self):
    '''
    Returns predicted position in that axis.
    '''

    return self.X[0:int(len(self.X)/2), 0]

  def getPredictedVel(self):
    '''
    Returns predicted velocity in that axis.
    '''

    return self.X[int(len(self.X)/2):len(self.X), 0]


