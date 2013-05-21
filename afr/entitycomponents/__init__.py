class EntityComponent(object):
    '''
    Functionality for Entity objects is implemented in a modular fashion as EntityComponent objects, which can be loaded/unloaded  at runtime into Entity objects.
    EntityComponents can export attributes/methods to the entity's base namespace by specifying the name in list self.exports that is checked during the attach process.
    '''
    def __init__(self):
        raise NotImplementedError("EntityComponent-derived objects  must override __init__")

    def modify_attribute(self, attrib, cur):
        return cur
