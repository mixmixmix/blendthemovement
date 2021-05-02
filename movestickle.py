import math
import time
import numpy as np
from collections import deque
import numpy as np #remember to add to sys.path proper python libs
import bpy
from mathutils import Vector
#test


"""
This class shows any natural and unnatural boundaries for the environment
"""
class Borders:
    x_min=0
    y_min=0
    x_max=100
    y_max=100
    def __init__(self, xmi,ymi,xma,yma): #isn't that a dumb constructor syntax, heh?
        self.x_min=xmi
        self.y_min=ymi
        self.x_max=xma
        self.y_max=yma

class Mooveemodel:
    def __init__(self, x_init, y_init, mu_s, sigma_speed, sigma_angular_velocity, theta_speed, theta_angular_velocity):
        self.mu = np.array([mu_s,0.])
        self.theta = np.array([theta_speed,theta_angular_velocity])
        self.sigma = np.array([sigma_speed,sigma_angular_velocity])
        self.v = np.array(self.mu)
        self.dt = np.ones(2)
        self.rng = np.random.default_rng()
        self.pos = np.array([x_init,y_init])
        self.angle = 0.
        self.os = np.array(self.mu)
        self.s = 0
        self.updateSpeed()

    def updateSpeed(self):
        os1 = self.os
        mu1 = self.mu
        theta1 = self.theta
        dt1 = self.dt
        sigma1 = self.sigma
        rng1 = self.rng

        self.os = (os1
            + theta1 * (mu1 - os1) * dt1
            + sigma1 * rng1.normal(0,np.sqrt(dt1),2)
        )

        self.angle = self.angle + self.os[1] * dt1[1]
        #self.s = np.log1p(np.exp(self.os[0])) #softplus cause it to get stuck in 0.
        self.s = abs(self.os[0])
        self.v[0] = self.s*np.cos(self.angle)
        self.v[1] = self.s*np.sin(self.angle)

        return self.v

    def updatePosition(self, side):
        new_pos = self.pos + self.v * self.dt
        self.pos = new_pos# % side
        is_same_panel = True if np.all(new_pos == self.pos) else False
        return self.pos, is_same_panel

    def getDirection(self):  
        return np.degrees(np.arctan2(self.v[1],self.v[0]))

def normToOne(vallist):
    valsum = sum(vallist)
    return [x/valsum for x in vallist]

"""
Updates position of all Zwierzaks.
They generally like to cluster, if they are suitably far away
"""
def updateZwkPosition(zwk,zwks,x_home,y_home,side,mm):

    zwk.x_prev = zwk.x_pos
    zwk.y_prev = zwk.y_pos

    cur_v = mm.updateSpeed()
    cur_pos, is_same_panel = mm.updatePosition(side)


    zwk.angle = mm.getDirection()

    #zwk.x_pos = int(cur_pos[0])
    #zwk.y_pos = int(cur_pos[1])

    zwk.x_pos = cur_pos[0]
    zwk.y_pos = cur_pos[1]
    
    return zwk, is_same_panel

"""
Handle colisions:
 - boundry conditions? Let's make it reflective, but simulate so that animals keep off the long grass.
 - collisions with other animals: This is going to be async, so if animal wants to move to other position, it will not make this movement. I need occupancy grid for that.
"""
def handleColisions(zwk, borders, zwks_list):
    rside = borders.x_max
    lside = borders.x_min # ASSUME IT IS SQUARE
    zwk.x_pos = max(min(zwk.x_pos,rside-1),lside)
    zwk.y_pos = max(min(zwk.y_pos,rside-1),lside)

    return zwk


class Zwierzak:
    def __init__(self, zwkid, x_init,y_init, hue=0, sat=1):
        self.id = zwkid
        self.x_init=x_init
        self.y_init=y_init
        self.x_pos=x_init
        self.y_pos=y_init
        self.x_prev=x_init
        self.y_prev=y_init
        self.hsv=(hue,sat,0) # initialise as a dim value
        self.angle = 0
        self.islong = 30 #half of width and height as opencv ellipses measurements defined
        self.iswide = 10
        self.speed = 2
        self.state = 0 #0 passive, speed = 1, 1 normal, speed around 3

        #unusual numbers to encourage program loudly crashing
        self.topleft = -111
        self.bottomright = -111
        self.topleft_prev = -111
        self.bottomright_prev = -111

        self.panelswitcher = deque([False, False, False])

    def observationPointSwitch(self, is_same_panel):
        self.panelswitcher.popleft()
        self.panelswitcher.append(is_same_panel)
        return np.all(self.panelswitcher)

# useful shortcut
scene = bpy.context.scene

side = 10
borders = Borders(0,0,side,side)

number_of_frame = 0
scene.frame_set(number_of_frame)
ani = bpy.data.objects['hemingway']
ani.rotation_mode = 'XYZ'
ani.location=(0,0,0)
ani.rotation_euler = (np.pi/2, 0, 0) 
ani.keyframe_insert(data_path="location", index=-1)
ani.keyframe_insert(data_path="rotation_euler", index=-1)
number_of_frame += 1

x_init, y_init = [side//2,side//2]
home = [x_init, y_init]
alf0 = Zwierzak('alf0',x_init,y_init, hue=0,sat=1)
alfs = [alf0]



mu_s  = 0
#sigma_speed = 4
#sigma_angular_velocity = 0.1
#theta_speed = 0.1
#theta_angular_velocity = 0.1
sigma_speed = 0.3
theta_speed = 0.001
sigma_angular_velocity = 1
theta_angular_velocity = 0.01


name = 'stickle'
dirname = 'stickle'
mm = Mooveemodel(x_init,y_init, mu_s, sigma_speed,sigma_angular_velocity,theta_speed, theta_angular_velocity)
mm2 = Mooveemodel(x_init,y_init, mu_s, sigma_speed,sigma_angular_velocity,theta_speed, theta_angular_velocity)


for it in range(1,2500,10):
    #break
    for alf in alfs:
        scene.frame_set(number_of_frame)
        alf, _ = updateZwkPosition(alf,alfs,home[0],home[1],side,mm)
        alf2, _ = updateZwkPosition(alf,alfs,home[0],home[1],side,mm)
        # alf = handleColisions(alf,borders,alfs)
        ani.location = (alf.y_pos,-alf.x_pos,0)
        aa = alf.angle
        #blender_angle = 2 * alf.angle / np.pi
        blender_angle = np.radians(aa) 
        ani.rotation_euler = (np.pi/2, 0, blender_angle) 
        ani.keyframe_insert(data_path="location", frame=it)
        ani.keyframe_insert(data_path="rotation_euler", frame = it)
        #print([alf.x_pos,alf.y_pos])
        print(f'frame {number_of_frame}, we got alf angle of {aa} and for blender it is  {blender_angle}')
        number_of_frame += 10
