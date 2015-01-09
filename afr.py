#!/usr/bin/env python

"""AFR main program."""

from __future__ import print_function

import logging
import sys

import afr.entity
import afr.entitycomponents
import afr.map
import afr.player
import afr.screen
import afr.util

logging.basicConfig(level=logging.DEBUG,
                    format="%(filename)s (%(funcName)s) %(message)s")

MAP_WIDTH = 40
MAP_HEIGHT = 40
ALLOWED_KEYS = set('qhjklyubn')


def tick(action):
    """Run game turn. Return success."""
    # XXX: assumes there is only one player entity, but doesn't enforce it
    for e in afr.entity.entities:
        if e.has_component('player'):
            logging.debug("Handling player action for {}".format(e))
            try:
                afr.player.handle_player_action(action, e)
            except afr.player.ActionError as e:
                logging.info("Couldn't perform action {action} ({reason})"
                             .format(action=action, reason=e))
                return False
    for e in afr.entity.entities:
        if e.has_component('ai') and not e.has_component('player'):
            logging.debug("Running AI for %s" % e.name)
            e.run_ai()
    return True

def main():
    """Main game loop."""
    # Mapgen
    afr.map.CreateMap(width=MAP_WIDTH, height=MAP_HEIGHT)
    afr.map.map.generate_interior(rooms=5)

    # Test creature init
    coords = [afr.map.map.get_empty_coordinates() for i in range(5)]
    player = afr.entity.Entity('Urist', components=[
        afr.entitycomponents.Creature(max_hp=100),
        afr.entitycomponents.Fighter(strength=5, team='dwarves'),
        afr.entitycomponents.Corporeal(x=coords[0][0], y=coords[0][1],
                                       icon='@', zorder=1),
        afr.entitycomponents.AI(),
        afr.entitycomponents.Inventory(),
        afr.entitycomponents.Player(),
    ]
    )
    afr.entity.entities.add(player)
    afr.entity.entities.add(
        afr.entity.Entity('Goblin King', components=[
            afr.entitycomponents.Creature(max_hp=40),
            afr.entitycomponents.Fighter(strength=10, team='goblins'),
            afr.entitycomponents.Corporeal(x=coords[1][0], y=coords[1][1]),
            afr.entitycomponents.AI(),
        ]
        )
    )
    afr.entity.entities.add(
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
    afr.entity.entities.add(
        afr.entity.Entity('Goblin King', components=[
            afr.entitycomponents.Creature(max_hp=40),
            afr.entitycomponents.Fighter(strength=10, team='goblins'),
            afr.entitycomponents.Corporeal(x=coords[3][0], y=coords[3][1]),
            afr.entitycomponents.AI(),
        ]
        )
    )
    afr.entity.entities.add(
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
        logging.debug("Tick: %s" % n_tick)
        afr.screen.draw_map(afr.map.map, focus=player)
        action = None
        while not action:
            try:
                key = raw_input('>_ ')
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(0)
            action = afr.player.key_to_action(key)
            if not action:
                logging.warning("Unknown key '%s'", key)
        did_tick = tick(action=action)
        if did_tick:
            n_tick += 1

    sys.exit()

if __name__ == '__main__':
    main()
