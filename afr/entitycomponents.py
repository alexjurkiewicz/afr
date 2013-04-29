import collections, random, math, logging

import afr.util
import afr.map

class Weapon(object):
    def __init__(self, damage):
        self.damage = damage

class Fighter(object):
    '''Entity can fight'''
    def __init__(self, type, strength, hp, team):
        self.type = type
        self.strength = strength
        self.hp = hp
        self.team = team

        self.alive = True

    def find_combat_target(self):
        candidates = [e for e in afr.entity.entities if hasattr(e, 'fighter') and e.fighter.alive and e.fighter.team != self.team]
        try:
            return min(candidates, key=lambda c: afr.map.map.distance_between(self.owner.corporeal.x, self.owner.corporeal.y, c.corporeal.x, c.corporeal.y))
        except ValueError: # min can't handle empty lists
            return None

    def attack(self, defender):
        attacker_str = random.randint(0, self.strength)
        defender_str = random.randint(0, defender.fighter.strength)

        if attacker_str == 0 or defender_str > attacker_str:
            dmg = (defender_str - attacker_str)//2
            self.hp -= dmg
            print("%s attacks %s but they block and counterattack for %s damage! (%shp remaining)" % (self.owner.name, defender.name, dmg, self.hp))
        elif defender_str == 0 or attacker_str > defender_str:
            dmg = (attacker_str - defender_str)
            defender.fighter.hp -= dmg
            print("%s hits %s for %s damage! (%shp remaining)" % (self.owner.name, defender.name, dmg, defender.fighter.hp))
        else:
            print("Mutual block!")

        if self.hp <= 0:
            print("%s died!" % self.owner.name)
            self.alive = False
            self.owner.corporeal.set_icon(afr.util.load_icon('skull-crossed-bones.png'))
        if defender.fighter.hp <= 0:
            print("%s died!" % defender.name)
            defender.fighter.alive = False
            defender.corporeal.set_icon(afr.util.load_icon('skull-crossed-bones.png'))

class Corporeal(object):
    '''Entity exists on the map'''
    def __init__(self, x, y, icon, blocks_movement = True):
        self.x = x
        self.y = y
        self.icon = icon
        self.blocks_movement = blocks_movement
        
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
    
    def run(self):
        '''Stupid generic creature brain'''
        state = self.brainstate
        if not self.owner.fighter.alive:
            return
        
        # Find a target
        if 'target' not in state:
            if hasattr(self.owner, 'inventory'):
                state['target'] = self.owner.inventory.find_nearby_pickupable()
            elif hasattr(self.owner, 'fighter'):
                state['target'] = self.owner.fighter.find_combat_target()
            else:
                logging.debug("Can't find a target for %s" % self.owner.name)
        
        if 'target' in state:
            target = state['target']
            logging.debug("Using target: %s (%s, %s)" % (target.name, target.corporeal.x, target.corporeal.y))
            # Move towards it / attack it
            dij_map = afr.map.map.create_dijkstra_map([[target.corporeal.x, target.corporeal.y]])
            #print("Generated dijkstra map: %s" % dij_map)
            (dx, dy) = afr.map.map.pathfind_using_dijkstra_map(dij_map, self.owner.corporeal.x, self.owner.corporeal.y)
            self.owner.corporeal.x += dx
            self.owner.corporeal.y += dy
            #if afr.map.map.distance_between(self.owner.corporeal.x, self.owner.corporeal.y, target.corporeal.x, target.corporeal.y) <= math.sqrt(2):
                #self.owner.fighter.attack(target)
            #else:
                #(dx, dy) = afr.map.map.pathfind_to(self.owner.corporeal.x, self.owner.corporeal.y, target.corporeal.x, target.corporeal.y)
                #self.owner.corporeal.x += dx
                #self.owner.corporeal.y += dy
        else:
            # No target, wander around
            if random.random() > 0.5:
                (dx, dy) = afr.map.map.pathfind_to(self.owner.corporeal.x, self.owner.corporeal.y, random.randint(0, afr.map.map.width), random.randint(0, afr.map.map.height))
                self.owner.corporeal.x += dx
                self.owner.corporeal.y += dy
                
class Inventory(list):
    '''Entity has an inventory'''
    def pick_up(self, entity):
        self.append(entity)
        entity.remove_component('corporeal')
    
    def find_nearby_pickupable(self):
        candidates = [e for e in afr.entity.entities if hasattr(e, 'weapon')]
        try:
            return min(candidates, key=lambda c: afr.map.map.distance_between(self.owner.corporeal.x, self.owner.corporeal.y, c.corporeal.x, c.corporeal.y))
        except ValueError: # min can't handle empty lists
            return None        