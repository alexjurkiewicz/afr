import logging

class Entity(object):
    def __init__(self, name, components):
        self.name = name
        self._components = {}
        for component in components:
            self.attach_component(component)

    def attach_component(self, component):
        name = component.__class__.__name__.lower()
        if name in self._components:
            raise ValueError("Component by the name %s is already attached." % name)
        else:
            logging.debug("Attaching %s to %s" % (name, self.name))
            component.owner = self
            self._components[name] = component
            for obj in component.export:
                if hasattr(self, obj):
                    raise AttributeError("Component exports %s which is already in use on this entity!" % obj)
                logging.debug("Setting attribute %s" % obj)
                setattr(self, obj, getattr(component, obj))
    
    def detach_component(self, component):
        '''Detach component by name'''
        if not component not in self._components:
            raise ValueError("No component named %s is attached." % component)
        else:
            component = self._components[name]
            del(self._components[name])
            for obj in component.export:
                delattr(self, obj)
                
    def has_component(self, component):
        return component in self._components

global entities
entities = []