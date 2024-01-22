import numpy as np
import math
#highlight and control /
class Particle:
    #constructor
    def __init__(self, pos=[0,0], vel=[0,0], mass=math.inf, angle=0, avel=0, momi=math.inf):
        self.pos = np.array(pos, float)
        self.vel = np.array(vel, float)
        self.mass = mass
        self.force = np.zeros(2,float) #np.array([0,0], float)
        self.angle = angle
        self.avel = avel
        self.momi = momi
        self.torque = 0


        self.update_rotation()
    
    def update(self, dt):
        #update the velocity assuming constant force
        self.vel += self.force/self.mass*dt
        #update the position assuming constant velocity
        self.pos -= self.vel*dt

        self.avel += self.torque/self.momi*dt
        self.angle += self.avel*dt
        #print(self.angle)
        self.update_rotation()

    def update_rotation(self):
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        self.rotational_matrix = np.array([[c,-s], [s,c]])
        #print(self.rotational_matrix)
    
    def rotate(self, v):
        return np.dot(self.rotational_matrix, v)
    
    def invrotate(self, v):
        return np.dot(self.rotational_matrix.transpose(), v)
    
    #add a force to the accumulator
    def add_force(self, force, pos=None):
        self.force += force
        if pos is None:
            pos = self.pos
        self.torque += np.cross(pos - self.pos, force)
    
    def clear_force(self):
        self.force = np.zeros(2, float)
        self.torque = 0
    
    def set_pos(self, pos):
        self.pos = np.array(pos, float)

    def set_angle(self, angle):
        self.angle = angle
        self.update_rotation()
    
    def delta_angle(self, delta):
        self.angle += delta
        self.update_rotation()
    
    def delta_pos(self, delta):
        self.pos += delta

    def impulse(self, impulse, pos=None):
        self.vel += impulse/self.mass
        if pos is None:
            pos = self.pos
        self.avel += np.cross(pos - self.pos, impulse)/self.momi
    
    def world(self,loc):
        return self.pos + self.rotate(loc)
    
    def local(self, world):
        #world = self.pos + self.rotate(self.local)
        return self.invrotate(world - self.pos)