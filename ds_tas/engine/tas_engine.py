import time
from contextlib import contextmanager

from .hooks import PTDEHook
from ..controller import KeyPress, KeySequence, print_press
from ..exceptions import GameNotRunningError


class TAS:
    """
    The high level TAS engine - provides more user friendly functions
    than working directly with the hook.

    This class handles the keypresses and sequences and the command
    queue.

    Initialise with a hook to work with remaster - creating with no
    arguments will attempt to create a hook to Dark Souls PTDE.

    :param hook: TAS Hook type to hook into the game.
    """
    def __init__(self, hook=None):
        if hook is None:
            hook = PTDEHook

        self.h = hook()
        self.queue = []

    def igt(self):
        """
        Get the raw in game time (alias for h.igt)

        :return: In game time in ms(?)
        """
        return self.h.igt()

    def rehook(self):
        """
        Make the TAS Hook reconnect

        :return:
        """
        self.h.rehook()

    def check_and_rehook(self):
        """
        Check if the game is running, if not try to rehook.

        :return:
        """
        self.h.check_and_rehook()

    def force_quit(self):
        self.h.force_quit()

    def frame_count(self):
        return self.h.frame_count()

    @contextmanager
    def tas_control(self):
        """
        Give control of the game to the TAS Engine for commands
        and return control after.
        """
        try:
            self.h.controller(False)
            self.h.background_input(True)
            self.h.disable_mouse(True)
            yield
        except PermissionError:
            raise GameNotRunningError(
                'TAS Hook has lost connection to the game. '
                'Call tas.rehook() to reconnect.'
            )
        finally:
            self.h.disable_mouse(False)
            self.h.background_input(False)
            self.h.controller(True)

    def _clear(self):
        """
        Clear the keypress queue
        """
        self.queue.clear()

    def _push(self, i):
        """
        Add an input to the queue
        Expects a list of 20 integers.

        Or a Keypress or a KeySequence

        index: meaning (values)
        0: dpad_up (0 or 1)
        1: dpad_down (0 or 1)
        2: dpad_left (0 or 1)
        3: dpad_right (0 or 1)
        4: start (0 or 1)
        5: back (0 or 1)
        6: left_thumb (0 or 1)
        7: right_thumb (0 or 1)
        8: left_shoulder (0 or 1)
        9: right_shoulder (0 or 1)
        10: a (0 or 1)
        11: b (0 or 1)
        12: x (0 or 1)
        13: y (0 or 1)
        14: l_trigger (0 to 255)
        15: r_trigger (0 to 255)
        16: l_thumb_x (-32,768 to 32,767)
        17: l_thumb_y (-32,768 to 32,767)
        18: r_thumb_x (-32,768 to 32,767)
        19: r_thumb_y (-32,768 to 32,767)
        """
        if isinstance(i[0], list) and len(i[0]) == 20:
            self.queue.extend(i)
        elif isinstance(i[0], int) and len(i) == 20:
            self.queue.append(i)
        else:
            raise ValueError(f'Invalid Input: {i}')

    def _execute(self, igt_wait=True, side_effect=None):
        """
        Execute the sequence of commands that have been pushed
        to the TAS object

        Show Commands will ignore 'wait' commands

        :param igt_wait: wait for the igt to tick before performing the first input
        :param side_effect: Call this method on each keypress if it is defined
        """
        with self.tas_control():
            igt = self.igt()
            if igt_wait:
                # Wait for IGT to tick before running the first input
                while igt == self.igt():
                    time.sleep(0.002)
            else:
                # If not waiting for IGT, sleep for 1/20th of a second
                # Otherwise the first input often gets eaten.
                time.sleep(0.05)

            # Loop over the queue and then clear it
            for command in self.queue:
                self.h.write_input(command)
                if side_effect:
                    side_effect(command)
                igt = self.igt()
                while igt == self.igt():
                    time.sleep(0.002)
            self.queue.clear()

    def keystate(self):
        """
        Get the current input state as a keypress
        :return:
        """
        state = self.h.read_input()
        return KeyPress.from_list(state)

    def record(self, start_delay=5, record_time=None, button_wait=True):
        """
        Record the inputs for a time or indefinitely

        Exit out and save by pressing start and select/back at the same time.

        use:
            >>> tas = TAS()
            >>> seq = tas.record(start_delay=10)

        playback:
            >>> tas.run(seq, start_delay=10)

        :param start_delay: Delay before recording starts in seconds
        :param record_time: Recording time
        :param button_wait: Wait for a button press to start recording
        :return: recorded tas data
        """
        print(f'Preparing to record in {start_delay} seconds')
        recording_data = []
        igt_diffs = set()

        if start_delay is None:
            start_delay = 0

        if start_delay >= 5:
            time.sleep(start_delay - 5)
            print('Countdown')
            for i in range(5, 0, -1):
                print(f'{i}')
                time.sleep(1)
        else:
            time.sleep(start_delay)

        print('Recording Started')
        start_time = time.clock()
        end_time = start_time + record_time if record_time else None
        first_input = True

        # Special code for waiting for first input
        if first_input and button_wait:
            print('Waiting for input')
            keypress = self.h.read_input()
            while not sum(keypress[4:6] + keypress[10:14]):
                time.sleep(0.002)
                keypress = self.h.read_input()
            print('Recording Resumed')

        while True:
            keypress = self.h.read_input()
            # Exit if start and select are held down
            if keypress[4] and keypress[5]:
                break
            recording_data.append(keypress)

            igt = self.h.igt()
            # Wait until next igt time
            while igt == self.h.igt():
                time.sleep(0.002)
            igt_diffs.add(self.h.igt() - igt)

            # Check if record time complete
            if end_time and time.clock() > end_time:
                break

        print('Recording Finished')
        print(f'Frame Lengths: {sorted(igt_diffs)}')

        recording = KeySequence.from_list(recording_data)

        return recording

    def run(self, keyseq, start_delay=None, igt_wait=True, display=True):
        """
        Queue up and execute a series of controller commands

        :param keyseq: KeySequence or KeyPress of inputs to execute
        :param start_delay: Delay before execution starts in seconds
        :param igt_wait: Wait for IGT to tick before performing the first input
        :param display: Display the game inputs as they are pressed
        """
        if len(keyseq) > 0:
            effect = print_press if display else None
            if start_delay:
                print(f'Delaying start by {start_delay} seconds')
                if start_delay >= 5:
                    time.sleep(start_delay - 5)
                    for i in range(5, 0, -1):
                        print(f'{i}')
                        time.sleep(1)
                else:
                    time.sleep(start_delay)

            print('Executing sequence')
            self._clear()
            self._push(keyseq.keylist)
            self._execute(igt_wait=igt_wait, side_effect=effect)
            print('Sequence executed')
        else:
            print('No Sequence Defined')
