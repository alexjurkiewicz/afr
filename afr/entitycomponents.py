import collections, random, math, logging

import afr.util
import afr.map

class EntityComponent(object):
    '''
    Functionality for Entity objects is implemented in a modular fashion as EntityComponent objects, which can be loaded/unloaded  at runtime into Entity objects.

    EntityComponents can export attributes/methods to the entity's base namespace by specifying the name in list self.exports that is checked during the attach process.
    '''
    def __init__(self):
        raise NotImplementedError("EntityComponent-derived objects  must override __init__")

    def modify_attribute(self, attrib, cur):
        return cur

class Weapon(EntityComponent):
    '''Entity is a weapon.'''
    def __init__(self, **bonus_attribs):
        '''Weapons provide bonus attributes specified as a key/val dict'''
        for key in bonus_attribs:
            setattr(self, key, bonus_attribs[key])

    def modify_attribute(self, attrib, cur):
        if hasattr(self, attrib):
            return cur + getattr(self, attrib)
        else:
            return cur

class Creature(EntityComponent):
    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.alive = True

        self.export = ['max_hp', 'current_hp', 'alive']

class Fighter(EntityComponent):
    '''Entity can fight'''
    def __init__(self, strength, team):
        self.strength = strength
        self.team = team

        self.export = ['strength', 'team', 'find_combat_target', 'attack']

    def find_combat_target(self):
        candidates = [e for e in afr.entity.entities if (e.has_component('corporeal') and e.has_component('fighter') and e.alive and e.team != self.owner.team)]
        try:
            return min(candidates, key=lambda c: afr.map.map.distance_between(self.owner.x, self.owner.y, c.x, c.y))
        except ValueError: # min can't handle empty lists
            return None

    def attack(self, defender):
        attacker_str = random.randint(0, self.owner.get('strength'))
        defender_str = random.randint(0, defender.get('strength'))

        if attacker_str == 0 or defender_str > attacker_str:
            dmg = (defender_str - attacker_str)//2
            self.owner.current_hp -= dmg
            print("{attacker} ({attackerhp} hp) attacks {defender} ({defenderhp} hp) but they block and counterattack for {dmg} damage!".format( \
                attacker=self.owner.name, attackerhp=self.owner.current_hp, defender=defender.name, defenderhp=defender.current_hp, dmg=dmg))
        elif defender_str == 0 or attacker_str > defender_str:
            dmg = (attacker_str - defender_str)
            defender.current_hp -= dmg
            print("{attacker} ({attackerhp} hp) hits {defender} ({defenderhp} hp) for {dmg} damage!".format( \
                attacker=self.owner.name, attackerhp=self.owner.current_hp, defender=defender.name, defenderhp=defender.current_hp, dmg=dmg))
        else:
            print("Mutual block!")

        if self.owner.current_hp <= 0:
            print("%s died!" % self.owner.name)
            self.alive = False
            self.blocks_movement = False
            self.owner.set_icon(afr.util.load_icon('skull-crossed-bones.bmp'))
        if defender.current_hp <= 0:
            print("%s died!" % defender.name)
            defender.alive = False
            defender.blocks_movement = False
            defender.set_icon(afr.util.load_icon('skull-crossed-bones.bmp'))

class Corporeal(EntityComponent):
    '''Entity exists on the map'''
    def __init__(self, x, y, icon, blocks_movement = True, zorder = 0):
        self.x = x
        self.y = y
        self.icon = icon
        self.blocks_movement = blocks_movement
        self.zorder = zorder
        
        self.export = ['x', 'y', 'get_icon', 'blocks_movement', 'set_icon', 'zorder']
        
        self.__original_icon = icon

    def get_icon(self):
        return self.icon
        
    def set_icon(self, icon=None):
        '''Change this entity's icon. Use none to reset to the original icon'''
        if icon:
            self.icon = icon
        else:
            self.icon == self.__original_icon

class AI(EntityComponent):
    '''Entity has a brain'''
    def __init__(self):
        self.brainstate = {}
        
        self.export = ['run_ai']

    def run_ai(self):
        '''Stupid generic creature brain'''
        state = self.brainstate
        me = self.owner
        if not self.owner.alive:
            return
        
        # If we have a target, ensure it's valid
        if 'target' in state and not state['target'].has_component('corporeal'):
            # The target has vanished (eg item that was picked up)
            del(state['target'])
        if 'target' in state and state['target_action'] == 'attack' and not state['target'].alive:
            # Stop attacking after a target dies
            del(state['target'])
        
        # Find a target
        if 'target' not in state:
            logging.debug("Finding target for %s" % me.name)
            if me.has_component('inventory'):
                target = me.find_nearby_pickupable()
                if target:
                    state['target'] = target
                    state['target_distance'] = 0
                    state['target_action'] = 'pick_up'
        if 'target' not in state:
            if me.has_component('fighter'):
                target = me.find_combat_target()
                if target:
                    state['target'] = target
                    state['target_distance'] = 1
                    state['target_action'] = 'attack'
        if 'target' not in state:
            logging.debug("Can't find a target for %s" % me.name)
        
        if 'target' in state:
            target = state['target']
            logging.debug("Using target: %s (%s, %s)" % (target.name, target.x, target.y))
            
            path = afr.map.map.pathfind(self.owner.x, self.owner.y, target.x, target.y)
            if path == None:
                logging.debug("Can't find path!")
            elif len(path) == state['target_distance']:
                # We're close enough to our destination.
                action = state['target_action']
                getattr(me, action)(target) # call the function specified in target_action on ourselves, with the target as the only argument
            else:
                if len(path) > 0:
                    dx = path[0].x - self.owner.x
                    dy = path[0].y - self.owner.y
                    logging.debug("Found path, %s steps. First step is %s, %s" % (len(path), dx, dy))
                    self.owner.x += dx
                    self.owner.y += dy
                else:
                    logging.debug("Pathfinding says we're there already!!")
        else:
            # No target, wander around
            if random.random() > 0.3:
                possible_directions = [i for i in ([-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]) if afr.map.map.tile_traversable(me.x + i[0], me.y + i[1])]
                print("possible directions: ", possible_directions)
                movement = random.choice(possible_directions)
                me.x += movement[0]
                me.y += movement[1]
                
class Inventory(EntityComponent):
    '''Entity has an inventory'''
    def __init__(self):
        self.inventory = []
        self.export = ['inventory', 'pick_up', 'find_nearby_pickupable']

    def modify_attribute(self, attrib, cur):
        val = cur
        for item in self.inventory:
            val = item.get(attrib, val)
        return val

    def pick_up(self, entity):
        self.inventory.append(entity)
        entity.detach_component('corporeal')
        logging.debug("%s picks up %s" % (self.owner.name, entity.name))
    
    def find_nearby_pickupable(self):
        candidates = [e for e in afr.entity.entities if (e.has_component('corporeal') and e.has_component('weapon'))]
        if candidates:
            best = min(candidates, key=lambda c: afr.map.map.distance_between(self.owner.x, self.owner.y, c.x, c.y))
        else:
            best = None
        return best
