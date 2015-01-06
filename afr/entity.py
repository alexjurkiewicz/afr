"""The entity class represents all entities in the game.

From units to items.
"""

import logging


class Entity(object):

    """
    Represents an ingame object (creature, item, aura, etc).

    Entitys are given functionality through EntityComponents which can be attached/detached at instantiation & runtime.
    """

    def __init__(self, name, components):
        """Create a new entity.

        name is a human-readable tag.
        components is an iterable of components to attach.
        """
        self.name = name
        self.components = {}
        for c in components:
            self.attach_component(c)

    def attach_component(self, component):
        """Attach provided EntityComponent."""
        name = component.__class__.__name__.lower()
        if name in self.components:
            raise ValueError("Component by the name %s is already attached to entity %s." % (name, self.name))
        else:
            logging.debug("Attaching %s to %s" % (name, self.name))
            component.owner = self
            self.components[name] = component
            if hasattr(component, 'export'):
                for obj in component.export:
                    if hasattr(self, obj):
                        raise AttributeError("Component exports %s which is already in use on entity %s." % (obj, self.name))
                    logging.debug("Setting attribute %s" % obj)
                    setattr(self, obj, getattr(component, obj))

    def detach_component(self, name):
        """Detach EntityComponent by name."""
        if name not in self.components.keys():
            raise ValueError("Entity %s has no attached component named %s." % (self.name, name))
        else:
            logging.debug("Detaching %s from %s" % (name, self.name))
            component = self.components[name]
            del(self.components[name])
            if hasattr(component, 'export'):
                for obj in component.export:
                    delattr(self, obj)

    def has_component(self, component):
        """Check if a certain component is attached."""
        return component in self.components

    def get(self, attrib, base=None):
        """Return an attribute, which may be modified by attached components.

        Specify base to use a different base value than this entities' (eg when
        modifying a parent entity (eg sword with +str modifying the holder's
        strength))
        """
        val = base if base else getattr(self, attrib)
        logging.debug("Getting attribute %s for %s (initial: %s)",
                      attrib, self.name, val)
        for c in self.components:
            component = self.components[c]
            oldval = val
            val = component.modify_attribute(attrib, val)
            if val != oldval:
                logging.debug("Component %s modified attribute (new: %s)",
                              c, val)
        return val

global entities
entities = []
