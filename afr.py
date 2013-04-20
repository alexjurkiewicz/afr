import random, sys, pygame, os, time, collections, math, logging

logging.basicConfig(level=logging.DEBUG)

###############
# CONFIGURATION
###############
MAP_WIDTH = 30
MAP_HEIGHT = 23

# Window init
RES_X = 1024
RES_Y = 768

# Display init
pygame.init()
screen = pygame.display.set_mode((RES_X, RES_Y))
TILE_WIDTH = TILE_HEIGHT = 32
CAMERA_TILES_X = RES_X // TILE_WIDTH
CAMERA_TILES_Y = RES_Y // TILE_HEIGHT

def load_icon(path):
    '''Load an icon using path relative to res/'''
    image = pygame.image.load(os.path.join('res', path))
    image = image.convert()
    return pygame.transform.smoothscale(image, (TILE_WIDTH, TILE_HEIGHT))

TileType = collections.namedtuple('TileType', ['passable', 'icon'])
TILE_TYPES = { \
        'dirt': TileType(passable = True, icon = load_icon('black32.png')),
        'floor': TileType(passable = True, icon = load_icon('black32.png')),
        'stone': TileType(passable = False, icon = load_icon('stone-tower-grey.png')),
        'boundary': TileType(passable = False, icon = load_icon('mountaintop.png')),
        }

CreatureType = collections.namedtuple('CreatureType', ['icon', 'icondead', 'team'])
CREATURE_TYPES = { \
        'dwarf': CreatureType(icon = load_icon('horse-head-yellow.png'), icondead = load_icon('skull-crossed-bones.png'), team = 'dwarves'),
        'goblin': CreatureType(icon = load_icon('imp-laugh-green.png'), icondead = load_icon('skull-crossed-bones.png'), team = 'goblins'),
        }

class Entity(object):
    def __init__(self, name, components):
        self.name = name
        for component in components:
            self.attach_component(component)

    def attach_component(self, component):
        name = component.__class__.__name__.lower()
        if hasattr(self, name):
            raise AttributeError("Component by the name %s is already attached." % name)
        else:
            component.owner = self
            setattr(self, name, component)

class Weapon(object):
    def __init__(self, damage):
        self.damage = damage
        
class Creature(object):
    def __init__(self, type, strength, hp):
        self.type = type
        self.strength = strength
        self.hp = hp

        self.typedata = CREATURE_TYPES[self.type]
        self.brainstate = {}
        self.alive = True

    @property
    def team(self):
        if hasattr(self, '_team'):
            return self._team
        else:
            return self.typedata.team

    def find_combat_target(self):
        candidates = [e for e in ENTITIES if e.creature.alive and e.creature.team != self.team]
        try:
            return min(candidates, key=lambda c: MAP.distance_between(self.owner.maplocation.x, self.owner.maplocation.y, c.maplocation.x, c.maplocation.y))
        except ValueError: # min can't handle empty lists
            return None

    def attack(self, defender):
        attacker_str = random.randint(0, self.strength)
        defender_str = random.randint(0, defender.creature.strength)

        if attacker_str == 0 or defender_str > attacker_str:
            dmg = (defender_str - attacker_str)//2
            self.hp -= dmg
            print("%s attacks %s but they block and counterattack for %s damage! (%shp remaining)" % (self.owner.name, defender.name, dmg, self.hp))
        elif defender_str == 0 or attacker_str > defender_str:
            dmg = (attacker_str - defender_str)
            defender.creature.hp -= dmg
            print("%s hits %s for %s damage! (%shp remaining)" % (self.owner.name, defender.name, dmg, defender.creature.hp))
        else:
            print("Mutual block!")

        if self.hp <= 0:
            print("%s died!" % self.owner.name)
            self.alive = False
        if defender.creature.hp <= 0:
            print("%s died!" % defender.name)
            defender.creature.alive = False

class MapLocation(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Map(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[MapTile('dirt') for _ in range(width)] for _ in range(height)]
        
    def generate(self):
        self.map = [[MapTile('dirt') if random.random() > 0.20 else MapTile('stone') for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
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
               not any([ c.maplocation.x == x and c.maplocation.y == y for c in ENTITIES])

class MapTile(object):
    def __init__(self, type):
        self.type = type
        self.tile = TILE_TYPES[self.type]

def draw_map(m, screen, startx=0, starty=0, clamp_to_map=True):
    '''Draw the map starting from x,y'''
    screen.fill((0,0,0))

    # Clamp draw rectangle to map border
    if clamp_to_map:
        if startx + CAMERA_TILES_X > m.width:
            startx = m.width - CAMERA_TILES_X
        if starty + CAMERA_TILES_Y > m.height:
            starty = m.height - CAMERA_TILES_Y

        startx = 0 if startx < 0 else startx
        starty = 0 if starty < 0 else starty

    # Don't try to draw tiles beyond the edge of the map
    endx = max([min([startx + CAMERA_TILES_X, m.width]), 0])
    endy = max([min([starty + CAMERA_TILES_Y, m.height]), 0])
    
    logging.debug("Drawing map from %s, %s to %s, %s" % (startx, starty, endx, endy))

    for j in range(starty, endy):
        for i in range(startx, endx):
            #print("%s,%s" % (i,j))
            if i >= 0 and j >= 0:
                screen.blit(m.map[j][i].tile.icon, (TILE_WIDTH*(i-startx), TILE_HEIGHT*(j-starty)))

    for c in ENTITIES:
        if startx <= c.maplocation.x <= endx and starty <= c.maplocation.y <= endy:
            screen.blit(c.creature.typedata.icon if c.creature.alive else c.creature.typedata.icondead, ((c.maplocation.x-startx)*TILE_WIDTH, (c.maplocation.y-starty)*TILE_HEIGHT))

def run_creature_brain(c):
    '''Stupid generic creature brain'''
    if not c.creature.alive: return # dont run ai for dead things
    state = c.creature.brainstate
    
    # Find a target
    target = c.creature.find_combat_target()
    if target:
        state['combat_target'] = target

        # Move towards it / attack it
        if MAP.distance_between(c.maplocation.x,c.maplocation.y,target.maplocation.x,target.maplocation.y) <= math.sqrt(2):
            c.creature.attack(target)
        else:
            (dx, dy) = MAP.pathfind_to(c.maplocation.x, c.maplocation.y, state['combat_target'].maplocation.x, state['combat_target'].maplocation.y)
            c.maplocation.x += dx
            c.maplocation.y += dy
    else:
        # No target, wander around
        if random.random() > 0.5:
            (dx, dy) = MAP.pathfind_to(c.maplocation.x, c.maplocation.y, random.randint(0, MAP.width), random.randint(0, MAP.height))
            c.maplocation.x += dx
            c.maplocation.y += dy

def tick():
    for c in ENTITIES:
        run_creature_brain(c)

if __name__ == '__main__':
    try:
        # Mapgen
        MAP = Map(MAP_WIDTH, MAP_HEIGHT)
        MAP.generate()
        # Creature init
        ENTITIES = []

        ENTITIES.append( \
            Entity('Urist', components = [
                Creature('dwarf', strength=20, hp=40),
                MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                ]
            )
        )
        ENTITIES.append( \
            Entity('Gobbo', components = [
                Creature('goblin', strength=20, hp=40),
                MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                ]
            )
        )

        # PyGame init
        screen = pygame.display.set_mode((RES_X, RES_Y))
        screen.fill((0,0,0))
        pygame.key.set_repeat(400, 50)

        # Event loop
        n_tick = 0
        run = True
        do_tick = False
        update_screen = True
        while run == True:
            if do_tick:
                n_tick += 1
                logging.debug("Tick: %s" % n_tick)
                do_tick = False
                tick()
                update_screen = True
            if update_screen == True:
                draw_map(MAP, screen, startx=0, starty=0)
                pygame.display.update()
                update_screen = False

            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    do_tick = True
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    run = False
    except:
        raise
    finally:
        pygame.quit()
    sys.exit()
