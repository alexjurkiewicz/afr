import collections, random, math

import afr.util

TileType = collections.namedtuple('TileType', ['passable', 'icon'])
TILE_TYPES = { \
        'dirt': TileType(passable = True, icon = afr.util.load_icon('black32.png')),
        'floor': TileType(passable = True, icon = afr.util.load_icon('black32.png')),
        'stone': TileType(passable = False, icon = afr.util.load_icon('stone-tower-grey.png')),
        'boundary': TileType(passable = False, icon = afr.util.load_icon('mountaintop.png')),
        }

class Map(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[MapTile('dirt') for _ in range(width)] for _ in range(height)]
        
    def generate(self):
        self.map = [[MapTile('dirt') if random.random() > 0.20 else MapTile('stone') for _ in range(self.width)] for _ in range(self.height)]
        for x in self.map[0]:
            x.type = 'boundary'
        for x in self.map[-1]:
            x.type = 'boundary'
        for y in self.map:
            y[0].type = 'boundary'
            y[-1].type = 'boundary'

    def pathfind_to(self, x1, y1, x2, y2):
        '''stupid pathfinding until i implement a*'''
        dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
        dy = 1 if y2 > y1 else -1 if y2 < y1 else 0
        # At destination
        if dy == dx == 0:
            return (0,0)
        # Attempt to move directly towards the target
        elif self.tile_traversable(x1+dx, y1+dy):
            return (dx, dy)
        # If the direct path is blocked, try horizontal and vertical only movement in a random order
        elif self.tile_traversable(x1, y1+dy) and self.tile_traversable(x1+dx, y1):
            return random.choice([(0, dy), (dx, 0)])
        # Or just vertically if horizontal approach is blocked...
        elif self.tile_traversable(x1, y1+dy):
            return (0, dy)
        # Or just horizontally if vertical approach is blocked...
        elif self.tile_traversable(x1+dx, y1):
            return (dx, 0)
        # No clear path available -- move in a random direction
        else:
            attempt = 0
            while attempt < 3 and not self.tile_traversable(x1+dx, y1+dy):
                dx = random.randint(-1,1)
                dy = random.randint(-1,1)
                attempt += 1
            if attempt >= 2:
                return (0, 0)
            else:
                return (dx, dy)

    def distance_between(self, x1,y1,x2,y2):
        '''Estimate distance between points'''
        #return abs(x1-x2) + abs(y1-y2) #manhattan difference (eg without diagonals)
        return math.sqrt(abs((x1-x2)**2) + abs((y1-y2)**2)) # real distance

    def tile_traversable(self, x,y):
        '''Is given tile traversable'''
        return 0 <= x < self.width and 0 <= y < self.height and \
               self.map[y][x].tile.passable and \
               not any([ c.maplocation.x == x and c.maplocation.y == y for c in afr.entity.entities])

class MapTile(object):
    def __init__(self, type):
        self.type = type
        self.tile = TILE_TYPES[self.type]
