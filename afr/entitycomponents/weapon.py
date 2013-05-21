import afr.entitycomponents

class Weapon(afr.entitycomponents.EntityComponent):
    '''Entity is a weapon.'''
    def __init__(self, **bonus_attribs):
        '''Weapons provide bonus attributes specified as a key/val dict'''
        for key in bonus_attribs:
            setattr(self, key, bonus_attribs[key])

    def modify_attribute(self, attrib, cur):
        if hasattr(self, attrib):
            return cur + getattr(self, attrib)
        else:
            return cur
