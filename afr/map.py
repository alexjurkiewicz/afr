import collections, random, math, logging, itertools

import afr.util

TileType = collections.namedtuple('TileType', ['passable', 'icon'])
TILE_TYPES = { \
        'dirt': TileType(passable = True, icon = afr.util.load_icon('black32.png')),
        'floor': TileType(passable = True, icon = afr.util.load_icon('black32.png')),
        'stone': TileType(passable = False, icon = afr.util.load_icon('stone-tower-grey.png')),
        'boundary': TileType(passable = False, icon = afr.util.load_icon('mountaintop.png')),
        }

class Map(object):
    def __init__(self, width, height, max_path_length = 9999):
        self.width = width
        self.height = height
        self.max_path_length = min([self.width * self.height, max_path_length])
        self.map = [[MapTile('dirt', x, y) for x in range(width)] for y in range(height)]
        
        self.graph = {}
        for x, y in itertools.product(range(self.width), range(self.height)):
            node = self.getTile(x, y)
            self.graph[node] = []
            
            for i, j in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                if self.tile_traversable(x+i, y+j):
                    self.graph[node].append(self.getTile(x+i, y+j))
            
    def getTile(self, x, y):
        return self.map[y][x]
        
    def generate(self):
        self.map = [[MapTile('dirt', x, y) if random.random() > 0.2 else MapTile('stone', x, y) for x in range(self.width)] for y in range(self.height)]

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

    def tile_traversable(self, x, y):
        '''Is given tile traversable'''
        return 0 <= x < self.width and 0 <= y < self.height and \
               self.getTile(x, y).tile.passable and \
               True
               #not any([ e.corporeal.blocks_movement and e.corporeal.x == x and e.corporeal.y == y for e in afr.entity.entities if hasattr(e, 'corporeal')])
    
    def neighboring_tile_coords(self, x, y, traversable_only = False):
        '''Return array of neighboring coordinates'''
        neighbors = [(x+n[0], y+n[1]) for n in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))]
        if traversable_only:
            return [n for n in neighbors if self.tile_traversable(n[0], n[1])]
        else:
            return neighbors

class MapTile(object):
    def __init__(self, type, x, y):
        self.type = type
        self.tile = TILE_TYPES[self.type]
        self.x = x
        self.y = y
        
        # a star stuff
        self.g = 0
        self.h = 0
        self.parent = None
    
    # a star stuff
    def move_cost(self, other):
        # diagonal = abs(self.x - other.x) == 1 and abs(self.y - other.y) == 1
        # return math.sqrt(2) if diagonal else 1
        return 1

global map
def CreateMap(**kwargs):
    global map
    map = Map(**kwargs)
