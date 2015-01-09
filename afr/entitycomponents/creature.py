from afr.entitycomponent import EntityComponent


class Creature(EntityComponent):

    """Basic component for all creatures.

    Creatures have hitpoints and can be alive or dead.
    They also have a size/shape, which influences eg equip slots."""

    def __init__(self, max_hp, shape='humanoid', size='medium'):
        """Create a creature with max_hp hp."""
        self.max_hp = max_hp
        self.shape = shape
        self.size = size

        self.current_hp = max_hp
        self.alive = True

        self.export = ['max_hp', 'current_hp', 'alive']
