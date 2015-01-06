"""All base entity components."""

import afr.entitycomponent
import afr.map
import afr.util


class Weapon(afr.entitycomponent.EntityComponent):

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
