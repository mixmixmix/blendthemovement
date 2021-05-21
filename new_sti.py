import math
import time
import numpy as np
from collections import deque
import numpy as np #remember to add to sys.path proper python libs
import bpy
from mathutils import Vector
import moomodel #sys.path.append('/home/mix/repos/blendthemovement
#test


"""
Updates position of all Zwierzaks.
They generally like to cluster, if they are suitably far away
"""
def updateSticklePosition(zwk,mm):

    zwk.prev_pos = zwk.pos

    cur_v = mm.updateSpeed()
    cur_pos = mm.updatePosition()

    zwk.angle[0] = mm.getDirection()

    # print(f'We experience {cur_v} and {cur_pos}')

    # zwk.pos = [int(cur_pos[0]),int(cur_pos[1]),int(cur_pos[2])] #for blender comment this line!!! HACK
    zwk.pos = cur_pos
    return zwk


class Stickle:
    def __init__(self, zwkid, init_pos):
        self.id = zwkid
        self.init_pos=init_pos
        self.pos=init_pos
        self.prev_pos=init_pos
        self.angle = [0.,0.] #angle[0] alpha, angle[1] beta
        self.islong = 30 #half of width and height as opencv ellipses measurements defined
        self.iswide = 10

# useful shortcut
scene = bpy.context.scene





number_of_frame = 0
scene.frame_set(number_of_frame)

#ani = bpy.data.objects['hemingway_benth'] 
##ani = bpy.data.objects['hemingway_mbd'] 
#side = [-2.5,2.5,1,5.2]
#start_x=7.
#start_z=2.
#ani.location=(start_x,0.,start_z)
#init_pos = [start_z,start_x,0]

ani = bpy.data.objects['block'] 
side = [-2.5,2.5,-5.2,-1] #those are middle of the tank3
start_x=-7.
start_z=-2.
ani.location=(start_x,0.,start_z)
init_pos = [start_z,start_x,0]


ani.rotation_mode = 'XYZ'

ani.rotation_euler = (np.pi/2, 0., np.pi/2) 
ani.keyframe_insert(data_path="location", index=-1)  
ani.keyframe_insert(data_path="rotation_euler", index=-1)
number_of_frame += 1


stickle = Stickle('s',init_pos)


mu_s  = 0
#sigma_speed = 4
#sigma_angular_velocity = 0.1
#theta_speed = 0.1
#theta_angular_velocity = 0.1
sigma_speed = 0.3
theta_speed = 0.5
sigma_angular_velocity = 0.2
theta_angular_velocity = 0.1
fwave = 0.2
mdir = 1

mm = moomodel.Mooveemodel(init_pos, mu_s, sigma_speed,sigma_angular_velocity,theta_speed, theta_angular_velocity, border='normal',side=side)
print('STARTTTTTTTT')
print('STARTTTTTTTT')
print('STARTTTTTTTT')
print('STARTTTTTTTT')
sampling = 5
for it in range(1,7500,sampling):
    scene.frame_set(number_of_frame)
    stickle = updateSticklePosition(stickle,mm)
    # alf = handleColisions(alf,borders,alfs)
    #print(stickle.pos)
    ani.location = (stickle.pos[1],0,stickle.pos[0])#x,y,z = 
    aa = stickle.angle[0]
    #blender_angle = 2 * alf.angle / np.pi
    blender_angle = np.radians(aa) 
    #print(mm.v)
    #ani.rotation_euler = (blender_angle, 0, np.pi/2) 
    if mm.v[0] > 0:
        blender_angle = 3 * np.pi/8
    if mm.v[0] < 0:
        blender_angle = 5*np.pi/8

    if mm.v[1] > 0.3:
        mdir =1
    if mm.v[1] < -0.3:
        mdir = -1
        
    #blender_angle = np.pi/2    
    ani.rotation_euler = (blender_angle, 0, mdir * np.pi/(2 + fwave)) 
    ani.keyframe_insert(data_path="location", frame=it)
    ani.keyframe_insert(data_path="rotation_euler", frame = it)
    #print([alf.x_pos,alf.y_pos])
    #print(f'frame {number_of_frame}, we got alf angle of {aa} and for blender it is  {blender_angle}')
    number_of_frame += sampling
    fwave = fwave * -1
