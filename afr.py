#!/usr/bin/env python

"""AFR main program."""

import logging
import sys

import afr.entity
import afr.entitycomponents
import afr.map
import afr.screen
import afr.util

logging.basicConfig(level=logging.DEBUG,
                    format="%(filename)s (%(funcName)s) %(message)s")

MAP_WIDTH = 40
MAP_HEIGHT = 40
ALLOWED_KEYS = set('qhjklyubn')


def _tick(action):
    """Run game turn."""
    for e in afr.entity.entities:
        if e.has_component('player'):
            _player_action(action, e)
        if e.has_component('ai') and not e.has_component('player'):
            logging.debug("Running AI for %s" % e.name)
            e.run_ai()


def _player_action(action, entity):
    """Resolve player action."""
    if action == 'move-left':
        func = entity.move
        args = {'dx': -1, 'dy': 0}
    elif action == 'move-right':
        func = entity.move
        args = {'dx': 1, 'dy': 0}
    elif action == 'move-down':
        func = entity.move
        args = {'dx': 0, 'dy': 1}
    elif action == 'move-up':
        func = entity.move
        args = {'dx': 0, 'dy': -1}
    elif action == 'move-left-up':
        func = entity.move
        args = {'dx': -1, 'dy': -1}
    elif action == 'move-left-down':
        func = entity.move
        args = {'dx': -1, 'dy': 1}
    elif action == 'move-right-up':
        func = entity.move
        args = {'dx': 1, 'dy': -1}
    elif action == 'move-right-down':
        func = entity.move
        args = {'dx': 1, 'dy': 1}
    else:
        logging.warning("Unknown player action %s!", action)
    try:
        func(**args)
    except afr.entitycomponents.ComponentError as e:
        logging.warning("Action failed: %s", e)


def main():
    try:
        # Mapgen
        afr.map.CreateMap(width=MAP_WIDTH, height=MAP_HEIGHT)
        afr.map.map.generate_interior(rooms=5)

        # Test creature init
        coords = [afr.map.map.get_empty_coordinates() for i in range(5)]
        afr.entity.entities.append(
            afr.entity.Entity('Urist', components=[
                afr.entitycomponents.Creature(max_hp=100),
                afr.entitycomponents.Fighter(strength=5, team='dwarves'),
                afr.entitycomponents.Corporeal(x=coords[0][0], y=coords[0][1],
                                               icon='@', zorder=1),
                afr.entitycomponents.AI(),
                afr.entitycomponents.Inventory(),
                afr.entitycomponents.Player(),
            ]
            )
        )
        afr.entity.entities.append(
            afr.entity.Entity('Goblin King', components=[
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=10, team='goblins'),
                afr.entitycomponents.Corporeal(x=coords[1][0], y=coords[1][1]),
                afr.entitycomponents.AI(),
            ]
            )
        )
        afr.entity.entities.append(
            afr.entity.Entity(
                'Sword',
                components=[
                    afr.entitycomponents.Corporeal(
                        x=coords[2][0],
                        y=coords[2][1],
                        icon='(',
                        blocks_movement=False,
                        zorder=-1),
                    afr.entitycomponents.Weapon(
                        strength=10),
                ]))
        afr.entity.entities.append(
            afr.entity.Entity('Goblin King', components=[
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=10, team='goblins'),
                afr.entitycomponents.Corporeal(x=coords[3][0], y=coords[3][1]),
                afr.entitycomponents.AI(),
            ]
            )
        )
        afr.entity.entities.append(
            afr.entity.Entity('Goblin King', components=[
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=10, team='goblins'),
                afr.entitycomponents.Corporeal(x=coords[4][0], y=coords[4][1]),
                afr.entitycomponents.AI(),
            ]
            )
        )

        # Event loop
        n_tick = 0
        run = True
        while run:
            n_tick += 1
            logging.debug("Tick: %s" % n_tick)
            afr.screen.draw_map(afr.map.map, focus=afr.entity.entities[0])
            key = None
            while key not in ALLOWED_KEYS:
                if key:
                    print "Unknown command '%s'" % key
                try:
                    key = raw_input('>_ ')
                except KeyboardInterrupt:
                    run = False
                    break
            if key == 'q':
                run = False
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
            if run:
                _tick(action=action)
        else:
            print ""

    except Exception:
        raise
    sys.exit()

if __name__ == '__main__':
    main()
