"""
Glitches

Note that these are defined for a 30FPS framerate PTDE.
These will not work at 60fps.

Available Sequences:
    joy_moveswap - performs the Joy animation and moveswaps to the weapon below
                   the bow (assumes the weapon is too heavy)
    poopwalk - yes

Available Functions:
    moveswap - Basic moveswap command sequence (to be performed mid animation)
    roll_moveswap - Basic fastroll moveswap
    reset_moveswap - Reset back from moveswap quickly
    itemswap - Attempt to perform the itemswap glitch
    framedupe - perform the frame perfect soul dupe.

Special Functions:
    force_quit - Perform a force quit on the correct frame for a wrong warp
                 on the next loading screen. (Will need to rehook after
                 restarting the game).
"""

from time import sleep

from .menus import joy

from ds_tas.basics import *
from ds_tas.controller import KeyPress, KeySequence
from ds_tas.exceptions import GameNotRunningError

__all__ = [
    'moveswap',
    'roll_moveswap',
    'reset_moveswap',
    'itemswap',
    'framedupe',
    'joy_moveswap',
    'poopwalk',
    'force_quit',
]


def moveswap(swap_up=False, too_heavy=True, delay=0):
    """
    Base commands for moveswap (to be executed mid animation)

    :param swap_up: Moveswap to the item above
    :param too_heavy: Is the weapon too heavy to use one handed
    :param delay: Delay frames before hitting the final moveswap input
    :return: KeySequence for moveswap
    """
    seq = KeySequence([
        l1,
        start,
        5 * wait,
        right,
        a,
        wait,
        down,
        a,
        2 * wait,
        up if swap_up else down,
        wait * delay,
        a,
        2 * wait,
        start,
        2 * wait,
        start if too_heavy else wait,
    ])
    return seq


def roll_moveswap(swap_up=False, too_heavy=True, delay=10):
    """
    Perform a roll and moveswap off the roll
    :param swap_up: Moveswap to the item above
    :param too_heavy: Is the weapon too heavy to 1 hand
    :param delay: Frame delay between roll and moveswap
                  Should be ~10 for fastroll, ~16 for midroll, ~31 for slowroll
    :return: KeySequence for rolling moveswap
    """
    return KeySequence([
        run & b,
        delay * wait,
        moveswap(swap_up, too_heavy)
    ])


def reset_moveswap(swapped_up=False):
    """
    Reset from moveswapped state back to pre-moveswap state.

    :param swapped_up: Was the weapon that was moveswapped above the bow
    :return: KeySequence to revert moveswap
    """
    return KeySequence([
        KeyPress(start=1),
        KeyPress(5),
        KeyPress(dpad_right=1),
        KeyPress(a=1),
        KeyPress(),
        KeyPress(dpad_down=1),
        KeyPress(a=1),
        KeyPress(2),
        KeyPress(dpad_up=0 if swapped_up else 1, dpad_down=1 if swapped_up else 0),
        KeyPress(a=1),
        KeyPress(2),
        KeyPress(start=1),
    ])


def itemswap(walk_time, toggle, use):
    return KeySequence([
        walkfor(walk_time),
        x,
        wait,
        down,
        runfor(toggle),
        run & right,
        runfor(use),
        x,
    ])


def framedupe(dupes):
    onedupe = x + waitfor(57) + x
    extradupe = waitfor(48) + waitfor(57) + x
    if dupes == 1:
        return onedupe
    elif dupes > 1:
        return onedupe + (dupes - 1) * extradupe


def force_quit(tas_engine, delay_frames=0):
    """
    Force quit the game after IGT pauses and resumes.

    :param tas_engine: Engine for force quit glitch
    :param delay_frames: additional frames to wait after IGT starts.
    """
    igt, igt_frame = tas_engine.igt(), tas_engine.frame_count()
    last_frame = tas_engine.frame_count()

    frame_wait = 0

    print("FQ Test started. Quit Dark souls or Ctrl-C to stop.")
    igt_running = True
    while True:
        try:
            new_igt, new_frame = tas_engine.igt(), tas_engine.frame_count()
            if new_igt and new_igt > igt:
                if not igt_running:
                    if frame_wait == 0:
                        print('IGT Started')
                    if frame_wait >= delay_frames:
                        print('Force Quitting')
                        tas_engine.h.force_quit()
                        break
                    frame_wait += 1
                igt, igt_frame = new_igt, new_frame

            elif new_frame > last_frame + 1 and igt_running:
                igt_running = False
                print('IGT Stopped')

            last_frame = new_frame

        except (GameNotRunningError, RuntimeError, OSError):
            break
        sleep(0.01)


poopwalk = l1 + waitfor(12) + l2

joy_moveswap = joy + waitfor(100) + moveswap()
