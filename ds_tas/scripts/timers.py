"""
Timers and frame counters for testing.
"""
from collections import namedtuple
from time import perf_counter, sleep
from datetime import timedelta

from ..controller import KeyPress
from ..engine import tas
from ..exceptions import GameNotRunningError


__all__ = [
    'igt_vs_rta',
    'force_quit',
]


IGTComparison = namedtuple('TimerComparison', 'frames rta igt diff est_diff')
FQFrames = namedtuple('FQFrames', 'frames igt igt_frame final_frame')


def igt_vs_rta(tas_engine=tas):
    """
    Start a timer to compare RTA/IGT and Frame Count

    :param tas_engine: The TAS engine to use for the comparison
                       (defaults to current)
    :return:
        frames displayed,
        rta in ms,
        igt in ms,
        difference between rta and igt,
        estimated difference between igt and rta
    """

    rta_start, igt_start = perf_counter(), tas_engine.igt()
    frame_start = tas_engine.frame_count()
    print("Timer Started - Press Start and Select simultaneously to stop.")
    while True:
        keypress = KeyPress.from_state()
        if keypress.start and keypress.back:
            break
        sleep(0.002)
    rta_end, igt_end = perf_counter(), tas_engine.igt()
    frame_end = tas_engine.frame_count()

    rta_diff = (rta_end - rta_start) * 1000
    igt_diff = igt_end - igt_start
    rta_vs_igt = rta_diff - igt_diff
    estimate = ((igt_diff / 33) * 1000/30) - igt_diff
    frame_diff = frame_end - frame_start

    print(f'RTA: {timedelta(milliseconds=rta_diff)}')
    print(f'IGT: {timedelta(milliseconds=igt_diff)}')
    print(f'Difference: {timedelta(milliseconds=rta_vs_igt)}')
    print(f'Estimated Difference: {timedelta(milliseconds=estimate)}')
    print(f'Frame Count: {frame_diff}')

    return IGTComparison(frame_diff, rta_diff, igt_diff, rta_vs_igt, estimate)


def force_quit(tas_engine=tas):
    """
    Time the frame count after IGT stops when executing a force quit

    :param tas_engine: The TAS engine to use for the comparison
                       (defaults to current)
    :return:
        Frame difference from when IGT stopped updating
        IGT when updating stopped
        Frame when IGT stopped
        Final Frame
    """
    igt, igt_frame = tas_engine.igt(), tas_engine.frame_count()
    last_frame = tas_engine.frame_count()

    print("FQ Test started. Quit Dark souls or Ctrl-C to stop.")
    while True:
        try:
            new_igt, new_frame = tas_engine.igt(), tas_engine.frame_count()
            if new_igt and new_igt > igt:
                igt, igt_frame = new_igt, new_frame
            last_frame = new_frame
        except GameNotRunningError:
            break
        sleep(0.002)

    diff = last_frame - igt_frame

    print(f'Frame Difference: {diff}')
    print(f'IGT: {igt}')
    print(f'IGT Frame: {igt_frame}')
    print(f'Final Frame: {last_frame}')

    return FQFrames(diff, igt, igt_frame, last_frame)
