import afr.entitycomponents

class Corporeal(afr.entitycomponents.EntityComponent):
    '''Entity exists on the map'''
    def __init__(self, x, y, icon, blocks_movement = True, zorder = 0):
        self.x = x
        self.y = y
        self.icon = icon
        self.blocks_movement = blocks_movement
        self.zorder = zorder

        self.export = ['x', 'y', 'get_icon', 'blocks_movement', 'set_icon', 'zorder']

        self.__original_icon = icon

    def get_icon(self):
        return self.icon

    def set_icon(self, icon=None):
        '''Change this entity's icon. Use none to reset to the original icon'''
        if icon:
            self.icon = icon
        else:
            self.icon == self.__original_icon
