import numpy as np
import random as rand


#finding path
def findpath(E, start):
    icntr = 0
    #converts E one for x11 and y11, another for x12, y12
    E = np.array(E)
    VE1 = (E[:,:,0])
    VE2 = (E[:,:,1])

    ipath = -1
    Vpath = [[VE2[ipath,0]], [VE2[ipath,1]]]

    start2 = [start[0], start[1]]

    #matches the x11 and y11 with a x12 and y12
    while 0 != ipath and 0 != ipath and icntr < 1000:
        iplen = range(len(VE2))
        for j in iplen:
            if VE1[ipath][0] == VE2[j][0] and VE1[ipath][1] == VE2[j][1]:
                ipath = j
        Vpath[0].append(int(VE2[ipath,0]))
        Vpath[1].append(int(VE2[ipath,1]))
        icntr += 1
    Vpath[0].append(start2[0])
    Vpath[1].append(start2[0])

    return Vpath


### functions ###
def collision_free(p1, p2, obstacles):
    """
    Check if the line segment between p1 and p2 intersects any rectangular obstacle.
    p1, p2 = (x, y)
    obstacles = list of [[x_min, x_max], [y_min, y_max]]
    """
    for shape in obstacles:
        xmin, xmax = shape[0]
        ymin, ymax = shape[1]

        # If both points are inside obstacle ? Flse
        if (xmin <= p1[0] <= xmax and ymin <= p1[1] <= ymax) or \
           (xmin <= p2[0] <= xmax and ymin <= p2[1] <= ymax):
            return False

        # Divide edge into small steps and check each point
        steps = 20
        for i in range(steps+1):
            t = i / steps
            x = p1[0] + t*(p2[0]-p1[0])
            y = p1[1] + t*(p2[1]-p1[1])
            if xmin <= x <= xmax and ymin <= y <= ymax:
                return False
    return True

