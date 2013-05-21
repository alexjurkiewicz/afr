import afr.entitycomponents

class Creature(afr.entitycomponents.EntityComponent):
    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.alive = True

        self.export = ['max_hp', 'current_hp', 'alive']
