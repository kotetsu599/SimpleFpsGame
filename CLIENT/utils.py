import math
import random


def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def lerp(start, end, t):
    return start + (end - start) * t

def colliding(x, y, z, blocks):
    half = 0.5
    for block in blocks:
        bx, by, bz = block
        if (bx - half <= x <= bx + half) and (bz - half <= z <= bz + half):
            if (by-0.5 <= y <= by + 2.5):
                return True
    if y <=2.5:
        return True

    return False

def bullet_colliding(x, y, z, blocks):
    half = 0.5
    for block in blocks:
        bx, by, bz = block
        if (bx - half <= x <= bx + half) and (bz - half <= z <= bz + half):
            if (by-0.5 <= y <= by + 0.5):
                return True
    return False


def spawn(building_blocks):
    while True:
        x = random.randint(-25, 25)
        y = 2.6
        z = random.randint(-25, 25)
        if not colliding(x, y, z, building_blocks):
            return [x, y, z]
