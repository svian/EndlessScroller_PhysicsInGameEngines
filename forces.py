import numpy as np
from particle import Particle

class SingleForce:
    def __init__(self,  objects = []):
        self.objects = objects

    def apply(self):
        for obj in self.objects:
            force = self.force(obj)
            obj.add_force(force)
    
    def force(self, obj):
        return np.array([0,0], float)

class Gravity(SingleForce):
    def __init__(self, acc = [0,0], **kwargs):
        self.acc = np.array(acc, float)
        super().__init__(**kwargs)
    
    def force(self, obj):
        return obj.mass * self.acc