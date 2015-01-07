import logging
import random

import afr.map
from afr.entitycomponent import EntityComponent


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
