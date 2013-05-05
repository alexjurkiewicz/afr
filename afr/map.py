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
    '''Represents the game world'''
    def __init__(self, width, height, max_path_length = 9999):
        self.width = width
        self.height = height
        self.max_path_length = min([self.width * self.height, max_path_length])
        self.map = [[MapTile('dirt', x, y) for x in range(width)] for y in range(height)]
        self.updateTileNeighbors()
        
    def updateTileNeighbors(self):
        for x, y in itertools.product(range(self.width), range(self.height)):
            node = self.getTile(x, y)
            #n = 0
            for i, j in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                if self.tile_traversable(x+i, y+j):
                    #n += 1
                    node.neighbors.append(self.getTile(x+i, y+j))
            #print("Added %s neighbors for %s, %s" % (n, node.x, node.y))
            
    def getTile(self, x, y):
        return self.map[y][x]
        
    def generate(self):
        '''Generate a random game map'''
        self.map = [[MapTile('dirt', x, y) if random.random() > 0.2 else MapTile('stone', x, y) for x in range(self.width)] for y in range(self.height)]
        self.updateTileNeighbors()
    
    def pathfind(self, x1, y1, x2, y2):
        '''return array of tiles which are a path between x1,y1 and x2,y2
        returns False if there is no path (care: a path of [] could be returned if you're already at the destination!)'''
        start = self.getTile(x1, y1)
        end = self.getTile(x2, y2)
        
        openset = set()
        closedset = set()
        current = start
        openset.add(current)
        parent = {}
        cycles = 0
        while openset:
            cycles += 1
            current = min(openset, key=lambda t:t.g + t.h)
            if current == end:
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                path.append(current)
                logging.debug("Found path for %s,%s to %s,%s in %s cycles (%s steps)" % (x1, y1, x2, y2, cycles, len(path)-1))
                return path[-2::-1] # [::-1] to include current tile
            openset.remove(current)
            closedset.add(current)
            #logging.debug("Working on node %s, %s (%s neighbors)" % (current.x, current.y, len(self.getTile(current.x, current.y).neighbors)))
            for node in self.getTile(current.x, current.y).neighbors:
                if node in closedset:
                    continue
                if node in openset:
                    new_g = current.g + current.move_cost(node)
                    if node.g > new_g:
                        node.g = new_g
                        parent[node] = current
                else:
                    node.g = current.g + current.move_cost(node)
                    node.h = self.distance_between(node.x, node.y, end.x, end.y)
                    parent[node] = current
                    openset.add(node)
        # If we're here, we didn't find a path. Maybe return a partial path in future.
        logging.warning("Cound't find path!")
        return None

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
        self.neighbors = []
    
    # a star stuff
    def move_cost(self, other):
        # diagonal = abs(self.x - other.x) == 1 and abs(self.y - other.y) == 1
        # return math.sqrt(2) if diagonal else 1
        return 1

global map
def CreateMap(**kwargs):
    global map
    map = Map(**kwargs)
