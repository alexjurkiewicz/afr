import afr.map
from afr.entitycomponent import EntityComponent


class Corporeal(EntityComponent):

    """Corporeal entities exist on the map."""

    def __init__(self, x, y, icon='g', blocks_movement=True, zorder=0):
        """Create a corporeal component.

        x & y (int) are the entity's location.
        icon (stris the character to represent the entity with.
        blocks_movement (bool) determines if other entities can occupy the same
            square.
        zorder (int) represents display order (higher = closer to the front).
        """
        self.x = x
        self.y = y
        self.blocks_movement = blocks_movement
        self.zorder = zorder
        self.icon = icon

        self.export = ['x', 'y', 'icon', 'blocks_movement', 'zorder', 'move']

    def move(self, dx, dy):
        """Move entity dx,dy tiles.

        Raises an exception if the travel is impossible.
        """
        if -1 > dx > 1 or -1 > dy > 1:
            raise afr.entitycomponent.ComponentError(
                "Attempted to move more than 1 tile.")
        x = self.owner.x + dx
        y = self.owner.y + dy
        if afr.map.map.tile_is_traversable(x, y):
            self.owner.x += dx
            self.owner.y += dy
        else:
            raise afr.entitycomponent.ComponentError(
                "There's no room at your destination!")
