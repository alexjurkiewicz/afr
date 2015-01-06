import logging
import random

import afr.map
import afr.util


class ComponentError(Exception):

    """Exception type for internal component signalling."""

    def __init__(self, reason):
        """Raise an exception with a reason."""
        self.reason = reason

    def __str__(self):
        """Simple display."""
        return self.reason


class EntityComponent(object):

    """Entity Component abstract base class.

    Functionality for Entity objects is implemented in a modular fashion as
    EntityComponent objects, which can be loaded/unloaded at runtime into
    Entity objects.

    EntityComponents can export attributes/methods to the entity's base
    namespace by specifying the name in list self.exports that is checked
    during the attach process.
    """

    def __init__(self):
        """The default constructor does nothing."""
        pass

    def modify_attribute(self, attrib, cur):
        """A default no-op for attribute modification."""
        return cur


class Weapon(EntityComponent):

    """Weapons provide bonus attributes.

    They are stored in an entity's inventory, not directly on the entity
    itself.

    XXX: support more modification schemes than addition (eg multiplication).
    """

    def __init__(self, **bonus_attribs):
        """Supply affected attribs as str(attrib_name)=int(modifier)."""
        for key in bonus_attribs:
            setattr(self, key, bonus_attribs[key])

    def modify_attribute(self, attrib, cur):
        """Get modified attrib."""
        if hasattr(self, attrib):
            return cur + getattr(self, attrib)
        else:
            return cur


class Creature(EntityComponent):

    """Creatures have hitpoints and can be alive or dead."""

    def __init__(self, max_hp):
        """Create a creature with max_hp hp."""
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.alive = True

        self.export = ['max_hp', 'current_hp', 'alive']


class Fighter(EntityComponent):

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


class Corporeal(EntityComponent):

    """Corporeal entities exist on the map."""

    def __init__(self, x, y, icon='g', blocks_movement=True, zorder=0):
        """Create a corporeal component.

        x & y (int) are the entity's location.
        icon (stris the character to represent the entity with.
        blocks_movement (bool) determines if other entities can occupy the same
            square.
        zorder (int) represents display order (higher = closer to the front).
        """
        self.x = x
        self.y = y
        self.blocks_movement = blocks_movement
        self.zorder = zorder
        self.icon = icon

        self.export = ['x', 'y', 'icon', 'blocks_movement', 'zorder', 'move']

    def move(self, dx, dy):
        """Move entity dx,dy tiles.

        Raises an exception if the travel is impossible.
        """
        print dx, dy
        if -1 > dx > 1 or -1 > dy > 1:
            raise ComponentError("Attempted to move more than 1 tile.")
        x = self.owner.x + dx
        y = self.owner.y + dy
        if afr.map.map.tile_is_traversable(x, y):
            self.owner.x += dx
            self.owner.y += dy
        else:
            raise ComponentError("There's no room at your destination!")


class AI(EntityComponent):

    """Entity has a brain."""

    def __init__(self):
        """Create an AI entity."""
        self.brainstate = {}

        self.export = ['run_ai']

    def _is_valid_target(self):
        state = self.brainstate
        if 'target' in state and \
                not state['target'].has_component('corporeal'):
            # The target has vanished (eg item that was picked up)
            del(state['target'])
        if 'target' in state and state['target_action'] == 'attack' and \
                not state['target'].alive:
            # Stop attacking after a target dies
            del(state['target'])
        if 'target' in state and state['target']:
            return True
        else:
            return False

    def _acquire_target(self):
        state = self.brainstate
        me = self.owner
        if self._is_valid_target():
            return
        if 'target' not in state:
            logging.debug("Finding target for %s" % me.name)
            if me.has_component('inventory'):
                pickupable = me.find_nearby_pickupable()
                if pickupable:
                    state['target'] = pickupable
                    state['target_distance'] = 0
                    state['target_action'] = 'pick_up'
        if 'target' not in state:
            if me.has_component('fighter'):
                enemy = me.find_combat_target()
                if enemy:
                    state['target'] = enemy
                    state['target_distance'] = 1
                    state['target_action'] = 'attack'
        if 'target' not in state:
            logging.debug("Can't find a target for %s" % me.name)

    def _move_towards_target(self):
        me = self.owner
        state = self.brainstate
        target = state['target']
        logging.debug("Using target: %s (%s, %s)",
                      target.name, target.x, target.y)

        path = afr.map.map.pathfind(me.x,
                                    me.y,
                                    target.x,
                                    target.y)
        if path is None:
            logging.debug("Can't find path!")
        elif len(path) == state['target_distance']:
            # We're close enough to our destination.
            action = state['target_action']
            # call the function specified in target_action on ourselves,
            # with the target as the only argument
            getattr(me, action)(target)
        else:
            if len(path) > 0:
                dx = path[0].x - me.x
                dy = path[0].y - me.y
                logging.debug("Found path, %s steps. Next step is %s, %s",
                              len(path), dx, dy)
                me.move(dx, dy)
            else:
                logging.debug("Pathfinding says we're there already!!")

    def run_ai(self):
        """Stupid generic creature brain."""
        state = self.brainstate
        me = self.owner
        if not self.owner.alive:
            return
        self._acquire_target()
        if 'target' in state:
            self._move_towards_target()
        else:
            # No target, wander around
            if random.random() > 0.3:
                possible_directions = [i for i in
                                       ([-1, -1], [-1, 0], [-1, 1], [0, -1],
                                        [0, 1], [1, -1], [1, 0], [1, 1])
                                       if afr.map.map.tile_is_traversable(
                                           me.x + i[0],
                                           me.y + i[1]
                                       )
                                       ]
                logging.debug("possible directions: %s", possible_directions)
                movement = random.choice(possible_directions)
                me.x += movement[0]
                me.y += movement[1]


class Inventory(EntityComponent):

    """Entity has an inventory.

    Inventories can contain other entities and pass through attribute
    modification.
    """

    def __init__(self):
        """Create an inventory."""
        self.inventory = []
        self.export = ['inventory', 'pick_up', 'find_nearby_pickupable']

    def modify_attribute(self, attrib, cur):
        """See if any inventory items modify the attrib."""
        val = cur
        for item in self.inventory:
            val = item.get(attrib, val)
        return val

    def pick_up(self, entity):
        """Add the named entity to our inventory.

        XXX: assumes the item is corporeal (not true in the future case of
        trading, etc).
        """
        self.inventory.append(entity)
        entity.detach_component('corporeal')
        logging.debug("%s picks up %s" % (self.owner.name, entity.name))

    def find_nearby_pickupable(self):
        """Return closest pickupable or None."""
        candidates = [e for e in afr.entity.entities if
                      (e.has_component('corporeal') and
                       e.has_component('weapon'))]
        if candidates:
            best = min(candidates,
                       key=lambda c:
                       afr.map.map.distance_between(self.owner.x,
                                                    self.owner.y,
                                                    c.x, c.y))
        else:
            best = None
        return best


class Player(EntityComponent):

    """Entity is controlled by the player."""
    pass
