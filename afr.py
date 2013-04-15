import random, sys, pygame, os, time, collections, math, logging

logging.basicConfig(level=logging.DEBUG)

# Window init
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

pygame.init()
font = pygame.font.SysFont('couriernew', 16)
TILE_WIDTH, TILE_HEIGHT = font.size('m')

MAP_WIDTH = WINDOW_WIDTH // TILE_WIDTH
MAP_HEIGHT = WINDOW_HEIGHT // TILE_HEIGHT

TILE_TYPE = { 'dirt': { 'passable' : True,
                        'icon': font.render(' ', False, (0,0,0)), },
              'floor': { 'passable': True,
                         'icon': font.render('_', False, (0,0,0)), },
               'stone': { 'passable' : False, 'icon': font.render('#', False, (0,0,0))},
               }

font.set_bold(True)
CREATURE_TYPE = { 'dwarf': { 'icon': font.render('@', False, (185,122,87), (255,255,255)),
                             'icondead': font.render('@', False, (185,122,87), (136,0,21)),
                             'team': 'dwarves', },
                   'goblin': { 'icon': font.render('g', False, (0,128,0), (255,255,255)),
                               'icondead': font.render('g', False, (0,128,0), (136,0,21)),
                               'team': 'goblins', },
                   }

class Creature(object):
    def __init__(self, name, type, x, y, strength, hp):
        self.name = name
        self.type = type
        self.x = x
        self.y = y
        self.strength = strength
        self.hp = hp

        self.typestats = CREATURE_TYPE[self.type]
        self.brainstate = {}
        self.alive = True

        logging.debug("Spawned new creature. Name: %s, team: %s" % (self.name, self.team))

    def __getattr__(self, key):
        '''If an attribute isn't found, look for it in the generic creature type dict'''
        if key in CREATURE_TYPE[self.type]:
            return CREATURE_TYPE[self.type][key]
        else:
            raise AttributeError

    def find_combat_target(self):
        candidates = [c for c in CREATURES if c.alive and c.team != self.team]
        try:
            return min(candidates, key=lambda c: MAP.distance_between(self.x, self.y, c.x, c.y))
        except ValueError: # min can't handle empty lists
            return None

    def attack(self, defender):
        attacker_str = random.randint(0, self.strength)
        defender_str = random.randint(0, defender.strength)

        if attacker_str == 0 or defender_str > attacker_str:
            dmg = (defender_str - attacker_str)
            self.hp -= dmg
            print("%s blocks and counterattacks %s for %s damage!" % (defender.name, self.name, dmg))
        elif defender_str == 0 or attacker_str > defender_str:
            dmg = (attacker_str - defender_str)
            print("%s hits %s for %s damage!" % (self.name, defender.name, dmg))
            defender.hp -= dmg
        else:
            print("Mutual block!")

        if self.hp <= 0:
            print("%s died!" % self.name)
            self.alive = False
        if defender.hp <= 0:
            print("%s died!" % defender.name)
            defender.alive = False

class Map(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[MapTile('dirt') for _ in range(width)] for _ in range(height)]
        
    def generate(self):
        self.map = [[MapTile('dirt') if random.random() > 0.20 else MapTile('stone') for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

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
        return MAP.map[y][x].typestats['passable'] and \
               not any([ c.x == x and c.y == y for c in CREATURES]) and \
               x >= 0 and y >= 0

class MapTile(object):
    def __init__(self, type):
        self.type = type

        self.typestats = TILE_TYPE[self.type]

def draw_map(m, screen):
    buffer = {}
    for y in range(len(m.map)):
        for x in range(len(m.map[y])):
            screen.blit(m.map[y][x].typestats['icon'], (TILE_WIDTH*x, TILE_HEIGHT*y))

    for c in CREATURES:
        screen.blit(c.icon if c.alive else c.icondead, (c.x*TILE_WIDTH, c.y*TILE_HEIGHT))

def run_creature_brain(c):
    '''Stupid generic creature brain'''
    if not c.alive: return # dont run ai for dead things
    logging.debug("Running brain for %s" % c.name)
    state = c.brainstate
    
    # Find a target
    target = c.find_combat_target()
    if target:
        logging.debug("Found target: %s" % target.name)
        state['combat_target'] = target

        # Move towards it / attack it
        if MAP.distance_between(c.x,c.y,target.x,target.y) <= math.sqrt(2):
            c.attack(target)
        else:
            (dx, dy) = MAP.pathfind_to(c.x, c.y, state['combat_target'].x, state['combat_target'].y)
            c.x += dx
            c.y += dy
    else:
        logging.debug("Found no combat target.")

def tick():
    for c in CREATURES:
        run_creature_brain(c)

if __name__ == '__main__':
    try:
        # Mapgen
        MAP = Map(MAP_WIDTH, MAP_HEIGHT)
        MAP.generate()
        # Creature init
        CREATURES = []

        CREATURES.append(Creature('Urist1', 'dwarf', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))
        CREATURES.append(Creature('Urist2', 'dwarf', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))
        CREATURES.append(Creature('Urist3', 'dwarf', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))
        CREATURES.append(Creature('Urist4', 'dwarf', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))
        CREATURES.append(Creature('Gobbo1', 'goblin', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))
        CREATURES.append(Creature('Gobbo2', 'goblin', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))
        CREATURES.append(Creature('Gobbo3', 'goblin', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))
        CREATURES.append(Creature('Gobbo4', 'goblin', x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), strength=10, hp=40))

        # PyGame init
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.fill((0,0,0))
        pygame.key.set_repeat(400, 50)

        # Event loop
        n_tick = 0
        run = True
        do_tick = False
        draw_map(MAP, screen)
        pygame.display.update()
        while run == True:
            if do_tick:
                n_tick += 1
                print("Tick: %s" % n_tick)
                do_tick = False
                tick()
                draw_map(MAP, screen)
                pygame.display.update()

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
