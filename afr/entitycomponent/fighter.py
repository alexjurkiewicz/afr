import random

import afr.entitycomponent


class Fighter(afr.entitycomponent.EntityComponent):

    """Fighters can engage in combat with other entities."""

    def __init__(self, strength, team):
        """Create a fighter with strength on team.

        team is an arbitrary identifying string.
        """
        self.strength = strength
        self.team = team

        self.export = ['strength', 'team', 'find_combat_target', 'attack',
                       'die']

    def find_combat_target(self):
        """Return closest enemy or None.

        XXX: assumes all fighters are corporeal(?).
        """
        candidates = [e for e in afr.entity.entities if
                      (e.has_component('corporeal') and
                       e.has_component('fighter') and
                       e.alive and
                       e.team != self.owner.team)
                      ]
        try:
            return min(candidates,
                       key=lambda c:
                       afr.map.map.distance_between(self.owner.x,
                                                    self.owner.y,
                                                    c.x,
                                                    c.y))
        except ValueError:  # min can't handle empty lists
            return None

    def die(self):
        """Kill the fighter."""
        self.owner.alive = False
        self.owner.blocks_movement = False
        self.owner.icon = 'x'

    def attack(self, defender):
        """Attack another entity and resolve results.

        Note: does not check if the attack is valid, you have to do that
        yourself.
        """
        attacker = self.owner
        attacker_str = random.randint(0, attacker.get('strength'))
        defender_str = random.randint(0, defender.get('strength'))

        if attacker_str == 0 or defender_str > attacker_str:
            dmg = (defender_str - attacker_str) // 2
            self.owner.current_hp -= dmg
            print("{attacker} ({attackerhp} hp) attacks "
                  "{defender} ({defenderhp} hp) but they block and "
                  "counterattack for {dmg} damage!"
                  .format(attacker=attacker.name,
                          attackerhp=attacker.current_hp,
                          defender=defender.name,
                          defenderhp=defender.current_hp,
                          dmg=dmg))
        elif defender_str == 0 or attacker_str > defender_str:
            dmg = (attacker_str - defender_str)
            defender.current_hp -= dmg
            print("{attacker} ({attackerhp} hp) hits "
                  "{defender} ({defenderhp} hp) for "
                  "{dmg} damage!"
                  .format(attacker=attacker.name,
                          attackerhp=attacker.current_hp,
                          defender=defender.name,
                          defenderhp=defender.current_hp,
                          dmg=dmg))
        else:
            print("Mutual block!")

        if self.owner.current_hp <= 0:
            print("%s died!" % self.owner.name)
            self.die()
        if defender.current_hp <= 0:
            print("%s died!" % defender.name)
            defender.die()
