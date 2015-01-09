from afr.entitycomponent import EntityComponent


class Weapon(EntityComponent):

    """Weapons provide bonus attributes.

    They are stored in an entity's inventory, not directly on the entity
    itself.

    XXX: support more modification schemes than addition (eg multiplication).
    """

    def __init__(self, slot='hand', **bonus_attribs):
        """Supply bonus_attribs like {'strength': 10}."""
        self.slot = slot
        for key in bonus_attribs:
            setattr(self, key, bonus_attribs[key])

        self.export = ['slot']

    def modify_attribute(self, attrib, cur):
        """Get modified attrib."""
        if hasattr(self, attrib):
            return cur + getattr(self, attrib)
        else:
            return cur
