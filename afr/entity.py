class Entity(object):
    def __init__(self, name, map, components):
        self.name = name
        self._map = map
        for component in components:
            self.attach_component(component)

    def attach_component(self, component):
        name = component.__class__.__name__.lower()
        if hasattr(self, name):
            raise AttributeError("Component by the name %s is already attached." % name)
        else:
            component.owner = self
            setattr(self, name, component)

global entities
entities = []