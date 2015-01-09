import logging

import afr.entity
from afr.entitycomponent import EntityComponent


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
