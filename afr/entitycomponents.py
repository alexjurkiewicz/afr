import collections, random

import afr.util

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

        self.brainstate = {}
        self.alive = True

    def find_combat_target(self):
        candidates = [e for e in afr.entity.entities if e.fighter.alive and e.fighter.team != self.team]
        try:
            return min(candidates, key=lambda c: self.owner._map.distance_between(self.owner.corporeal.x, self.owner.corporeal.y, c.corporeal.x, c.corporeal.y))
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
    def __init__(self, x, y, icon):
        self.x = x
        self.y = y
        self.icon = icon
        self.__original_icon = icon
    def set_icon(self, icon=None):
        '''Change this entity's icon. Use none to reset to the original icon'''
        if icon:
            self.icon = icon
        else:
            self.icon == self.__original_icon