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
            raise RuntimeError('More than one unit on this tile, not supported!')
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
    if len(items) != 1:
        raise RuntimeError('More than one item on this tile, not supported!')
    entity.pick_up(items[0])
    return


def _do_show(action, entity):
    if action == 'show-inventory':
        message = 'Inventory:\n'
        message += ', '.join(str(i) for i in entity.inventory)
        raise ActionError(message)


def handle_player_action(action, entity):
    """Resolve player action."""
    # XXX: this action -> func mapping should probably be defined in the KEY_MAP dict
    if action == 'quit-game':
        sys.exit(0)
    elif action.startswith('move-'):
        func = _do_move
    elif action == 'pick-up':
        func = _do_pickup
    elif action.startswith('show-'):
        func = _do_show
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
