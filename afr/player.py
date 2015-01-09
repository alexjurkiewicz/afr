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
    """Figure out what to do with a move action and return (func, args)."""
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
    if not afr.map.map.tile_is_traversable(*target):
        raise ActionError('Something is in the way!')
    entity.move(**args)


def handle_player_action(action, entity):
    """Resolve player action."""
    if action == 'quit-game':
        sys.exit(0)
    elif action.startswith('move-'):
        func = _do_move
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
