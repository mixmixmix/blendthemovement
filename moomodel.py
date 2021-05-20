import math
import numpy as np


class Mooveemodel:
    def __init__(self, init_pos, mu_s, sigma_speed, sigma_angular_velocity, theta_speed, theta_angular_velocity, border=None, side=None):
        self.mu = np.array([mu_s,0.])
        self.theta = np.array([theta_speed,theta_angular_velocity])
        self.sigma = np.array([sigma_speed,sigma_angular_velocity])
        self.v = np.array([0.,0.,0.])
        self.dt = np.ones(3)
        self.rng = np.random.default_rng()
        self.pos = np.array(init_pos)
        self.angle = 30. #alpha angle
        self.os = np.array(self.mu)
        self.s = 0.
        self.border = border

        if border:
            if side:
                self.side = side
            if not side:
                print(f'You need to provide argument \'side\' for the border conditions {borderMethod}')

        if border=='normal':
            self.bdist=0.5 #half the power of border rejection

        self.updateSpeed()

    #The "normal" boundary condition is a hack on the output angle of the movement model, it accelerates the turn of angle without feeding in to the model
    def borderRepulsionVector(self):
        dist_low = self.side + self.pos[0]
        dist_high = self.side - self.pos[0]
        dist_left = self.side + self.pos[1]
        dist_right = self.side - self.pos[1]

        mag = 10
        # print(f' The distances are {dist_low} {dist_high}, {dist_left}, {dist_right}')
        force_low = 1 / (1+math.exp(mag*(dist_low-self.bdist)))
        force_high = 1 / (1+math.exp(mag*(dist_high-self.bdist)))
        force_left = 1 / (1+math.exp(mag*(dist_left-self.bdist)))
        force_right = 1 / (1+math.exp(mag*(dist_right-self.bdist)))
        # print(f' The forceances are {force_low} {force_high}, {force_left}, {force_right}')

        #add vectors:
        #return np.array([force_left-force_right, force_low-force_high])
        #blender
        return np.array([force_low-force_high, force_left-force_right])


    def updateSpeed(self):
        os1 = self.os
        mu1 = self.mu
        theta1 = self.theta
        dt1 = self.dt[0:2]
        sigma1 = self.sigma
        rng1 = self.rng

        self.os = (os1
            + theta1 * (mu1 - os1) * dt1
            + sigma1 * rng1.normal(0,np.sqrt(dt1),2)
        )

        self.angle = self.angle + self.os[1] * dt1[1] #angle of X/Y plane
        #self.s = np.log1p(np.exp(self.os[0])) #softplus cause it to get stuck in 0.

        inv=np.array([0.,0.])#this must be float otherwise python gets messed up real quick
        ouv=np.array([0.,0.])

        # print(f'pre angle {self.angle}')
        if self.border=='normal':
            inv[0] = np.cos(self.angle)
            inv[1] = np.sin(self.angle)
            brv = self.borderRepulsionVector()
            # print(f'Repulsion! {brv}')
            ouv [0] = inv[0] + brv[0]
            ouv [1] = inv[1] + brv[1]
            # print(f'vector inv: {inv}')
            # print(f'vector brv: {brv}')
            # print(f'vector ouv: {ouv}')
            self.angle = np.arctan2(ouv[1],ouv[0])

        # print(f'post angle {self.angle}')

        self.s = abs(self.os[0])
        self.v[0] = self.s*np.cos(self.angle)
        self.v[1] = self.s*np.sin(self.angle)
        self.v[2] = 0 #no movement on z-axis for now...

        return self.v

    def updatePosition(self):
        new_pos = self.pos + self.v * self.dt
        if not self.border:
            self.pos = new_pos
            return self.pos
        elif self.border=='periodic':
            self.pos = new_pos % self.side
            is_same_panel = True if np.all(new_pos == self.pos) else False
            return self.pos, is_same_panel
        elif self.border=='normal':
            self.pos = new_pos
            return self.pos


    #2D only
    def getDirection(self):
        return np.degrees(np.arctan2(self.v[1],self.v[0]))
