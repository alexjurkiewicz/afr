"""Contains player-specific code."""
import logging
import sys

import afr.entity
import afr.map
from afr.entitycomponent import ComponentError

KEY_MAP = {
    'q': 'quit-game',
    'h': 'move-left',
    'j': 'move-down',
    'k': 'move-up',
    'l': 'move-right',
    'y': 'move-left-up',
    'u': 'move-right-up',
    'b': 'move-left-down',
    'n': 'move-right-down',
    'g': 'pick-up',
    'i': 'show-inventory',
    '.': 'wait',
    'e': 'equip',
}


class ActionError(Exception):

    """Simple Exception type for actions to raise if they can't do anything."""

    def __init__(self, message):
        """Message is displayed to the player."""
        self.message = message

    def __str__(self):
        """be quiet, pylint."""
        return "ActionError: {}".format(self.message)


def _do_move(action, entity):
    """Handle move actions.

    These may be an attack request or (TODO) a force move request.
    """
    args = {'dx': 0, 'dy': 0}
    if '-left' in action:
        args['dx'] = -1
    elif '-right' in action:
        args['dx'] = 1
    if '-up' in action:
        args['dy'] = -1
    elif '-down' in action:
        args['dy'] = 1
    target = (entity.x + args['dx'], entity.y + args['dy'])
    blocking_entities = afr.entity.at_position(*target, blocks_movement=True)
    if blocking_entities:
        blocker = blocking_entities[0]
        if len(blocking_entities) != 1:
            raise RuntimeError(
                'More than one unit on this tile, not supported!')
        if entity.team != blocker.team:
            entity.attack(blocker)
            return
    # note: tile_is_traversable also checks for entities in the way
    if not afr.map.map.tile_is_traversable(*target):
        raise ActionError('Something is in the way!')
    entity.move(**args)


def _do_pickup(action, entity):
    """Handle pickup actions."""
    items = afr.entity.at_position(entity.x, entity.y, blocks_movement=False)
    if not items:
        raise ActionError('Nothing to pick up.')
    elif len(items) == 1:
        item_num = 0
    else:
        prompt = "Pick up which item?\n"
        for i in range(len(items)):
            prompt += '%s: %s\n' % (i, items[i])
        prompt += '\n'
        item_num = input(prompt)
        try:
            item_num = int(item_num)
        except:
            raise ActionError("Unrecognised input '%r'." % item_num)
        # XXX: this shuffle is probably a sign of bad design
    entity.pick_up(items[item_num])
    print("Picked up %s" % items[item_num])


def _do_show(action, entity):
    if action == 'show-inventory':
        message = 'Inventory:\n'
        for index, item in enumerate(entity.inventory):
            print("%s: %s" % (index, item))
        raise ActionError("Instant Turn")


def _do_wait(action, entity):
    pass


def _do_equip(action, entity):
    if len(entity.inventory) < 1:
        raise ActionError("Your inventory is empty!")
    prompt = "Equip which item?\n"
    for i in range(len(entity.inventory)):
        prompt += '%s: %s\n' % (i, entity.inventory[i])
    prompt += '\n'
    item_num = input(prompt)
    try:
        item_num = int(item_num)
    except:
        raise ActionError("Unrecognised input '%r'." % item_num)
    # XXX: this shuffle is probably a sign of bad design
    item = entity.inventory[item_num]
    success = entity.equip(item)
    if success:
        del(entity.inventory[item_num])
    else:
        raise ActionError("Couldn't equip %s." % item.name)


def handle_player_action(action, entity):
    """Resolve player action."""
    # XXX: this action -> func mapping should probably be defined in the
    # KEY_MAP dict
    if action == 'quit-game':
        sys.exit(0)
    elif action.startswith('move-'):
        func = _do_move
    elif action == 'pick-up':
        func = _do_pickup
    elif action.startswith('show-'):
        func = _do_show
    elif action == 'wait':
        func = _do_wait
    elif action == 'equip':
        func = _do_equip
    else:
        logging.warning("Unknown player action %s!", action)
        return False

    logging.debug(
        "Player action calls {func} with args action={action} "
        "entity={entity}".format(
            func=func,
            action=action,
            entity=entity))

    try:
        func(action, entity)
    except ComponentError as e:
        logging.warning("Action '%s' failed: %s", action, e)
        return False
    else:
        return True


def key_to_action(key):
    """Convert input keycode to action."""
    return KEY_MAP.get(key)
