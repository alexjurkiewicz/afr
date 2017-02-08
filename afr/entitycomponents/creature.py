import logging

from afr.entitycomponent import EntityComponent

SLOTS = {'humanoid': ['hand-left', 'torso']}


class Creature(EntityComponent):

    """Basic component for all creatures.

    Creatures have hitpoints and can be alive or dead.
    They also have a size/shape, which influences eg equip slots."""

    def __init__(self, max_hp, shape='humanoid', size='medium'):
        """Create a creature with max_hp hp."""
        self.max_hp = max_hp
        self.shape = shape
        self.size = size

        self.current_hp = max_hp
        self.alive = True
        self.slots = dict.fromkeys(SLOTS.get(shape, []))

        self.export = ['max_hp', 'current_hp', 'alive', 'slots', 'equip']

    def modify_attribute(self, attrib, cur):
        """See if any equipped items modify the attrib."""
        val = cur
        for item in list(self.slots.values()):
            if not item:
                continue
            val = item.get(attrib, val)
        return val

    def equip(self, item, slot=None):
        """Equip an item. Slot is determined automatically if unspecified.

        Returns boolean success.
        """
        if slot:
            if self.slot(slot):
                return False
            else:
                target_slot = slot
        else:
            # Use the first slot that starts with the equippable's slot
            # specification and is empty
            possible_slots = [
                s for s in self.slots if hasattr(item, 'slot') and s.startswith(
                    item.slot) and not self.slots[s]]
            if not possible_slots:
                return False
            else:
                target_slot = possible_slots[0]

        assert not item.has_component('corporeal')
        self.slots[target_slot] = item
        logging.debug(
            "%s equips %s in slot %s" %
            (self.owner.name, item.name, target_slot))
        return True
