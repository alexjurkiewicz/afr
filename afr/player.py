"""Contains player-specific code."""
import logging
import sys

import afr.entitycomponents


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
    if key == 'q':
        action = 'quit-game'
    elif key == 'h':
        action = 'move-left'
    elif key == 'j':
        action = 'move-down'
    elif key == 'k':
        action = 'move-up'
    elif key == 'l':
        action = 'move-right'
    elif key == 'y':
        action = 'move-left-up'
    elif key == 'u':
        action = 'move-right-up'
    elif key == 'b':
        action = 'move-left-down'
    elif key == 'n':
        action = 'move-right-down'
    else:
        logging.warning("Unknown key '%'", key)
        action = None
    return action
