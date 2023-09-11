from Adafruit_PCA9685 import PCA9685
from utils import *
import time
import numpy as np

STEP = 50


class ControlMotor:
    def __init__(self):
        # Initialise the PCA9685 using desired address and/or bus:
        self.pwm = PCA9685(address=0x40, busnum=1)
        # Set frequency to 60[Hz]
        self.pwm.set_pwm_freq(60)
        # disk size
        self.disk_colors = {1: 110, 2: 100, 3: 90, 4: 80}
        self.default_angles = [90, 180, 190, 45]
        self.current_angles = [90, 180, 190]
        self.target_angles = [90, 110, 170]

    def setPWMwithAngle(self, thetas, num):
        self.pwm.set_pwm(12, 0, AngleToRadian(90 - thetas[1] - 7 + thetas[2] - 21 + 7))
        if num == 0:
            self.pwm.set_pwm(0, 0, AngleToRadian(thetas[0]))
        elif num == 1:
            self.pwm.set_pwm(4, 0, AngleToRadian(thetas[1]))
        elif num == 2:
            self.pwm.set_pwm(8, 0, AngleToRadian(thetas[2]))
        
        
    def setDefault(self):
        diff = []
        for i in range(3):
            diff.append(np.linspace(self.current_angles[i], self.default_angles[i], STEP))

        # for i in range(STEP):
        #     self.current_angles[0] = diff[0][i]
        #     self.setPWMwithAngle(self.current_angles, 0)
        #     time.sleep(0.03)

        for i in range(STEP):
            for j in range(3):
                self.current_angles[j] = diff[j][i]
                self.setPWMwithAngle(self.current_angles, j)
                time.sleep(.02)

        self.pwm.set_pwm(12, 0, AngleToRadian(45))
        self.pwm.set_pwm(15, 0, AngleToRadian(0))

    def moveArmSlow(self):
        diff = []
        for i in range(3):
            diff.append(np.linspace(self.current_angles[i], self.target_angles[i], STEP))

        for i in range(STEP):
            self.current_angles[0] = diff[0][i]
            self.setPWMwithAngle(self.current_angles, 0)
            time.sleep(0.03)

        for i in range(STEP):
            for j in range(1, 3):
                self.current_angles[j] = diff[j][i]
                self.setPWMwithAngle(self.current_angles, j)
                time.sleep(.02)

    def gripperMove(self, _ga):
        if _ga >= 120:
            _ga = 120

        self.pwm.set_pwm(15, 0, AngleToRadian(_ga))

    def moveArmWithCoord(self, _disk, _coord):
        for j in range(3):
            if j == 1:
                self.gripperMove(self.disk_colors.get(_disk))
                time.sleep(0.5)
            theta_0, theta_1, theta_2 = CalculateTheta(_coord[j][0], _coord[j][1], _coord[j][2])
            self.target_angles = [theta_0, theta_1, theta_2]
            self.moveArmSlow()
            time.sleep(1.5)

        theta_0, theta_1, theta_2 = CalculateTheta(_coord[2][0], _coord[2][1], 1)
        self.target_angles = [theta_0, theta_1, theta_2]
        self.moveArmSlow()
        time.sleep(0.5)
        self.gripperMove(0)
        time.sleep(0.5)
        self.setDefault()
        time.sleep(1.5)
