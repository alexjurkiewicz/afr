import afr.util
import afr.map
import afr.entitycomponents

class Fighter(afr.entitycomponents.EntityComponent):
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
            self.owner.set_icon(afr.util.load_icon('skull-crossed-bones.png'))
        if defender.current_hp <= 0:
            print("%s died!" % defender.name)
            defender.alive = False
            defender.set_icon(afr.util.load_icon('skull-crossed-bones.png'))
