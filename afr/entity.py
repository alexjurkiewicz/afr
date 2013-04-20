class Entity(object):
    def __init__(self, name, components):
        self.name = name
        for component in components:
            self.attach_component(component)

    def attach_component(self, component):
        name = component.__class__.__name__.lower()
        if hasattr(self, name):
            raise AttributeError("Component by the name %s is already attached." % name)
        else:
            component.owner = self
            setattr(self, name, component)
    
    def detach_component(self, component):
        '''Detach component by name'''
        if not hasattr(self, component):
            raise AttributeError("No component named %s is attached." % component)
        else:
            delattr(self, component)

global entities
entities = []