from circle import Circle
from wall import Wall
import numpy as np
import math


class Contact:
    #constructor
    def __init__(self, a,b, overlap, normal,penetrator, point, **kwargs):
        self.a = a
        self.b = b
        self.overlap = overlap
        self.normal = normal
        self.penetrator = penetrator
        self.offset = penetrator.local(point)
        self.kwargs = kwargs

    def __bool__(self):
        return self.overlap > 0
    
    def contact_point(self):
        return self.penetrator.world(self.offset)

    def resolveNeg(self):
        a = self.a
        b = self.b
        if self.overlap < 0:
            #resolve overlap
            m = 1/(1/a.mass + 1/b.mass)
            a.delta_pos(m/a.mass *self.overlap*self.normal)
            b.delta_pos(-m/b.mass *self.overlap*self.normal)
            
            #resolve velocities
            contact_point = self.contact_point()
            sa = contact_point - a.pos
            sb = contact_point - b.pos
            va = a.vel + a.avel*np.array([-sa[1],sa[0]], float)
            vb = b.vel + b.avel*np.array([-sb[1],sb[0]], float)

            vi = va-vb
            #vi = a.vel-b.vel #initial rel velocity
            vin = np.dot(vi, self.normal) 
            if vin < 0:
                restitution = self.kwargs["restitution"]
                Jn = -(1 + restitution) *m*vin
                J = Jn*self.normal
                a.impulse(J)
                b.impulse(-J)

    def resolvePos(self):
        a = self.a
        b = self.b
 
        if self.overlap > 0:
            #resolve overlap
            m = 1/(1/a.mass + 1/b.mass)
            a.delta_pos(m/a.mass *self.overlap*self.normal)
            b.delta_pos(-m/b.mass *self.overlap*self.normal)
            
            #resolve velocities
            contact_point = self.contact_point()
            sa = contact_point - a.pos
            sb = contact_point - b.pos
            va = a.vel + a.avel*np.array([-sa[1],sa[0]], float)
            vb = b.vel + b.avel*np.array([-sb[1],sb[0]], float)

            vi = va-vb
            #vi = a.vel-b.vel #initial rel velocity
            vin = np.dot(vi, self.normal) 
            if vin > 0:
                restitution = self.kwargs["restitution"]
                Jn = -(1 + restitution) *m*vin
                J = Jn*self.normal
                a.impulse(J)
                b.impulse(-J)

def mag(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

def contact(a,b, **kwargs):
    if isinstance(a,Circle) and isinstance(b, Circle):
        return circle_circle(a,b, **kwargs)
    elif isinstance(a,Circle) and isinstance(b, Wall):
        return circle_wall(a,b, **kwargs)
    elif isinstance(a,Wall) and isinstance(b, Circle):
        return circle_wall(b,a , **kwargs)

def circle_wall(circle, wall, radius, **kwargs):
    overlap = np.dot((wall.pos - circle.pos), wall.normal) + radius
    #print(wall.pos)
    normal = wall.normal
    contact_point = circle.pos - circle.radius*normal
    
    return Contact(circle, wall, overlap, normal, circle, contact_point, **kwargs)

def circle_polygon(circle, poly, **kwargs):
    min_overlap = math.inf
    for i in range(len(poly.points)):
        overlaps = np.einsum("ij,ij->i", ((poly.pos + poly.offsets) - circle.pos), poly.normals) + circle.radius
        min_i = np.argmin(overlaps)
        min_overlap = overlaps[i]

        if overlaps[i] < min_overlap:
            min_i = i
        if min_overlap <= 0:
            break
    
    if 0 < min_overlap < circle.radius: #check corner overlapped, but not inside
        # endpoints of side of minimum overlap
        point1 = poly.points[min_i]
        point2 = poly.points[min_i - 1]
        # distances to those endpoints
        dist1 = mag(point1 - circle.pos)
        dist2 = mag(point2 - circle.pos)
        #find which is closest
        if dist1 < dist2:
            closest = point1
            other = point2
        else:
            closest = point2
            other = point1
        #displacement from closest to circle, vector tangent to side
        s = circle.pos - closest
        vector = closest - other
        #if beyond the endpoint, contact is with corner
        if np.dot(s, vector) > 0:
            mags = mag(s)
            overlap = circle.radius - mags
            normal = s/mags
            contact_point =  circle.pos - circle.radius*normal
            return Contact(circle, poly, overlap, normal, circle, contact_point, **kwargs)
    contact_point = circle.pos - circle.radius*poly.normals[i]
    return Contact(circle, poly, min_overlap, poly.normals[i], circle, contact_point, **kwargs)
    
def circle_circle(a, b, **kwargs):
    r = a.pos - b.pos
    overlap = a.radius + b.radius - mag(r)
    normal = r/mag(r)
    contact_point = r - (a.radius + b.radius)*normal
    return Contact(a,b, overlap, normal, b, contact_point, **kwargs)

def polygon_polygon(polyA, polyB, **kwargs):
    min_overlap = math.inf
    for i in range(len(polyA.points)):
        overlaps = np.einsum("ij,ij->i", ((polyA.pos + polyA.offsets) - polyB.pos), polyA.normals) + polyB.radius
        min_i = np.argmin(overlaps)
        min_overlap = overlaps[i]

        if overlaps[i] < min_overlap:
            min_i = i
        if min_overlap <= 0:
            break

def polygon_wall(poly, wall, **kwargs):
    overlap = np.dot((wall.pos - poly.pos), wall.normal) + poly.width
    normal = wall.normal
    contact_point = poly.pos - poly.width*normal
    return Contact(poly,wall, overlap, normal, poly, contact_point, **kwargs)