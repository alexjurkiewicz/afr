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
        try:
            return self.map[y][x]
        except IndexError:
            raise IndexError("Coordinates outside map")

    def setTile(self, x, y, tile):
        '''You may also want to regenerate pathfinding neighbors'''
        try:
            self.map[y][x] = tile
        except IndexError:
            raise IndexError("Coordinates outside map")
        
    def generate(self):
        '''Generate a random game map'''
        self.map = [[MapTile('dirt', x, y) if random.random() > 0.2 else MapTile('stone', x, y) for x in range(self.width)] for y in range(self.height)]
        self.updateTileNeighbors()

    def generate_interior(self, rooms=2):
        # Generate an all-wall map
        self.map = [[MapTile('stone', x, y) for x in range(self.width)] for y in range(self.height)]

        # Add boundary
        for x in range(self.width):
            for y in range(self.height):
                if x in (0, self.width-1) or y in (0, self.height-1):
                    self.setTile(x, y, MapTile('boundary', x, y))

        # Carve out rooms
        room_coords = []
        for room in range(rooms):
            width = random.randint(2,6)
            height = random.randint(2,6)
            # Don't let rooms overrun the map boundary
            startx = random.randint(0, self.width - 1 - width)
            starty = random.randint(0, self.height - 1 - height)
            endx = startx + width
            endy = starty + height
            room_coords.append((startx, starty, endx, endy))
            logging.debug("Building room at %s,%s - %s,%s" % (startx, starty, endx, endy))
            for x in range(startx, endx):
                for y in range(starty, endy):
                    self.setTile(x, y, MapTile('dirt', x, y))

        # Carve a tunnel between each combination of rooms
        for roompair in itertools.combinations(room_coords, 2):
            start_room = roompair[0]
            dest_room = roompair[1]
            if start_room != dest_room:
                cursorx = random.randint(start_room[0], start_room[2])
                cursory = random.randint(start_room[1], start_room[3])
                destx = random.randint(dest_room[0], dest_room[2])
                desty = random.randint(dest_room[1], dest_room[3])
                self.carve_tunnel(cursorx, cursory, destx, desty)

        # Update pathing
        self.updateTileNeighbors()

    def carve_tunnel(self, x1, y1, x2, y2):
        logging.debug("Carving tunnel between %s,%s and %s,%s" % (x1, y1, x2, y2))
        #map.py:70 (generate_interior) Building room at 1,3 - 6,6
        #map.py:70 (generate_interior) Building room at 9,7 - 13,9
        cursorx = x1
        cursory = y1
        while cursorx != x2:
            logging.debug("Clearing space at %s,%s" % (cursorx, cursory))
            self.setTile(cursorx, cursory, MapTile('dirt', cursorx, cursory))
            cursorx += 1 if x2 > cursorx else -1
        while cursory != y2:
            logging.debug("Clearing space at %s,%s" % (cursorx, cursory))
            self.setTile(cursorx, cursory, MapTile('dirt', cursorx, cursory))
            cursory += 1 if y2 > cursory else -1

    def get_empty_coordinates(self):
        x = random.randint(0, self.width-1)
        y = random.randint(0, self.height-1)
        while not self.tile_traversable(x, y):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
        return (x, y)
    
    def pathfind(self, x1, y1, x2, y2):
        '''return array of tiles which are a path between x1,y1 and x2,y2
        returns False if there is no path (care: a path of [] could be returned if you're already at the destination!)'''
        # thanks to http://scriptogr.am/jdp/post/pathfinding-with-python-graphs-and-a-star
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
                if not self.tile_traversable(node.x, node.y):
                    if node.x != x2 or node.y != y2:
                        closedset.add(node)
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
               not any([ e.blocks_movement and e.x == x and e.y == y for e in afr.entity.entities if e.has_component('corporeal')])
    
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

    def setType(self, type):
        self.type = type
        self.tile = TILE_TYPES[self.type]
    
    # a star stuff
    def move_cost(self, other):
        diagonal = abs(self.x - other.x) == 1 and abs(self.y - other.y) == 1
        return math.sqrt(2) if diagonal else 1

global map
def CreateMap(**kwargs):
    global map
    map = Map(**kwargs)
