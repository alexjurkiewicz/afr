"""Entity components attach to entities to provide properties & methods.

They can also modify attributes of the parent entity.
This file provides the EntityComponent abstract base class and the
ComponentError exception they should raise when needed.
"""


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
