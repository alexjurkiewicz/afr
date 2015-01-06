"""Contains player-specific code."""
import logging
import sys

import afr.entitycomponents

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


def _action_move(action, entity):
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
    return (entity.move, args)


def handle_player_action(action, entity):
    """Resolve player action."""
    if action == 'quit-game':
        sys.exit(0)
    elif action.startswith('move-'):
        func, args = _action_move(action, entity)
    else:
        logging.warning("Unknown player action %s!", action)

    try:
        func(**args)
    except afr.entitycomponents.ComponentError as e:
        logging.warning("Action failed: %s", e)


def key_to_action(key):
    """Convert input keycode to action."""
    return KEY_MAP.get(key)
