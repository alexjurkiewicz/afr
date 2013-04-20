import collections, random

import afr.util

class Weapon(object):
    def __init__(self, damage):
        self.damage = damage

CreatureType = collections.namedtuple('CreatureType', ['icon', 'icondead', 'team'])
CREATURE_TYPES = { \
        'dwarf': CreatureType(icon = afr.util.load_icon('horse-head-yellow.png'), icondead = afr.util.load_icon('skull-crossed-bones.png'), team = 'dwarves'),
        'goblin': CreatureType(icon = afr.util.load_icon('imp-laugh-green.png'), icondead = afr.util.load_icon('skull-crossed-bones.png'), team = 'goblins'),
        }

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
        candidates = [e for e in afr.entity.entities if e.creature.alive and e.creature.team != self.team]
        try:
            return min(candidates, key=lambda c: self.owner._map.distance_between(self.owner.maplocation.x, self.owner.maplocation.y, c.maplocation.x, c.maplocation.y))
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