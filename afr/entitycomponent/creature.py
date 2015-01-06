import afr.entitycomponent

class Creature(afr.entitycomponent.EntityComponent):

    """Creatures have hitpoints and can be alive or dead."""

    def __init__(self, max_hp):
        """Create a creature with max_hp hp."""
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.alive = True

        self.export = ['max_hp', 'current_hp', 'alive']
