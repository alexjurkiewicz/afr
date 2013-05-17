import logging

class Entity(object):
    def __init__(self, name, components):
        self.name = name
        self.components = {}
        for c in components:
            self.attach_component(c)

    def attach_component(self, component):
        name = component.__class__.__name__.lower()
        if name in self.components:
            raise ValueError("Component by the name %s is already attached to entity %s." % (name, self.name))
        else:
            logging.debug("Attaching %s to %s" % (name, self.name))
            component.owner = self
            self.components[name] = component
            for obj in component.export:
                if hasattr(self, obj):
                    raise AttributeError("Component exports %s which is already in use on entity %s." % (obj, self.name))
                logging.debug("Setting attribute %s" % obj)
                setattr(self, obj, getattr(component, obj))
    
    def detach_component(self, name):
        '''Detach component by name'''
        if name not in self.components.keys():
            raise ValueError("Entity %s has no attached component named %s." % (self.name, name))
        else:
            logging.debug("Detaching %s from %s" % (name, self.name))
            component = self.components[name]
            del(self.components[name])
            for obj in component.export:
                delattr(self, obj)
                
    def has_component(self, component):
        return component in self._components

global entities
entities = []
