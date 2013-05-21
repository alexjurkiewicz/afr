import afr.map
import afr.entitycomponents

class Inventory(afr.entitycomponents.EntityComponent):
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
