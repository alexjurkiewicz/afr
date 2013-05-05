import collections, random, math, logging

import afr.util
import afr.map

class Weapon(object):
    def __init__(self, damage):
        self.damage = damage
        self.export = ['damage']

class Fighter(object):
    '''Entity can fight'''
    def __init__(self, type, strength, hp, team):
        self.type = type
        self.strength = strength
        self.hp = hp
        self.team = team

        self.alive = True
        
        self.export = ['strength', 'hp', 'team', 'alive', 'find_combat_target', 'attack']

    def find_combat_target(self):
        candidates = [e for e in afr.entity.entities if e.alive and e.team != self.owner.team]
        try:
            return min(candidates, key=lambda c: afr.map.map.distance_between(self.owner.x, self.owner.y, c.x, c.y))
        except ValueError: # min can't handle empty lists
            return None

    def attack(self, defender):
        attacker_str = random.randint(0, self.strength)
        defender_str = random.randint(0, defender.strength)

        if attacker_str == 0 or defender_str > attacker_str:
            dmg = (defender_str - attacker_str)//2
            self.hp -= dmg
            print("%s attacks %s but they block and counterattack for %s damage! (%shp remaining)" % (self.owner.name, defender.name, dmg, self.hp))
        elif defender_str == 0 or attacker_str > defender_str:
            dmg = (attacker_str - defender_str)
            defender.hp -= dmg
            print("%s hits %s for %s damage! (%shp remaining)" % (self.owner.name, defender.name, dmg, defender.hp))
        else:
            print("Mutual block!")

        if self.hp <= 0:
            print("%s died!" % self.owner.name)
            self.alive = False
            self.owner.set_icon(afr.util.load_icon('skull-crossed-bones.png'))
        if defender.fighter.hp <= 0:
            print("%s died!" % defender.name)
            defender.alive = False
            defender.set_icon(afr.util.load_icon('skull-crossed-bones.png'))

class Corporeal(object):
    '''Entity exists on the map'''
    def __init__(self, x, y, icon, blocks_movement = True):
        self.x = x
        self.y = y
        self.icon = icon
        self.blocks_movement = blocks_movement
        
        self.export = ['x', 'y', 'icon', 'blocks_movement', 'set_icon']
        
        self.__original_icon = icon
        
    def set_icon(self, icon=None):
        '''Change this entity's icon. Use none to reset to the original icon'''
        if icon:
            self.icon = icon
        else:
            self.icon == self.__original_icon

class AI(object):
    '''Entity has a brain'''
    def __init__(self):
        self.brainstate = {}
        
        self.export = ['run_ai']
    
    def run_ai(self):
        '''Stupid generic creature brain'''
        state = self.brainstate
        if not self.owner.alive:
            return
        
        # Find a target
        if 'target' not in state:
            if self.owner.has_component('inventory'):
                state['target'] = self.owner.find_nearby_pickupable()
            elif self.owner.has_component('fighter'):
                state['target'] = self.owner.find_combat_target()
            else:
                logging.debug("Can't find a target for %s" % self.owner.name)
        
        if 'target' in state:
            target = state['target']
            logging.debug("Using target: %s (%s, %s)" % (target.name, target.x, target.y))
            path = afr.map.map.pathfind(self.owner.x, self.owner.y, target.x, target.y)
            if path != False:
                logging.debug("Found path, %s steps. First step is %s, %s" % (len(path), dx, dy))
            if path:
                dx = path[0].x - self.owner.x
                dy = path[0].y - self.owner.y
                
            
            self.owner.x += dx
            self.owner.y += dy
        else:
            # No target, wander around
            if random.random() > 0.5:
                (dx, dy) = afr.map.map.pathfind_to(self.owner.x, self.owner.y, random.randint(0, afr.map.map.width), random.randint(0, afr.map.map.height))
                self.owner.corporeal.x += dx
                self.owner.corporeal.y += dy
                
class Inventory(object):
    '''Entity has an inventory'''
    def __init__(self):
        self.inventory = []
        self.export = ['inventory', 'pick_up', 'find_nearby_pickupable']
    
    def pick_up(self, entity):
        self.inventory.append(entity)
        entity.remove_component('corporeal')
    
    def find_nearby_pickupable(self):
        candidates = [e for e in afr.entity.entities if e.has_component('weapon')]
        try:
            return min(candidates, key=lambda c: afr.map.map.distance_between(self.owner.x, self.owner.y, c.x, c.y))
        except ValueError: # min can't handle empty lists
            return None        