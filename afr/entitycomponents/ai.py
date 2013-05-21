import afr.map
import afr.entitycomponents

class AI(afr.entitycomponents.EntityComponent):
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
            if random.random() > 0.5:
                (dx, dy) = (random.randint(-1, 1), random.randint(-1, 1))
                if afr.map.map.tile_traversable(me.x + dx, me.y + dy):
                    me.x += dx
                    me.y += dy
