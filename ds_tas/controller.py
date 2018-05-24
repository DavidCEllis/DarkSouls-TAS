"""
Main controller commands for keypresses and sequences.

These are the methods behind all of the basic commands. They are also
necessary for recording and playing back inputs.
"""

import json
from copy import copy
from itertools import chain

__all__ = [
    'controller_keys',
    'KeyPress',
    'KeySequence',
]

controller_keys = [
    'dpad_up',
    'dpad_down',
    'dpad_left',
    'dpad_right',
    'start',
    'back',
    'l_thumb',
    'r_thumb',
    'l1',
    'r1',
    'a',
    'b',
    'x',
    'y',
    'l2',
    'r2',
    'l_thumb_x',
    'l_thumb_y',
    'r_thumb_x',
    'r_thumb_y',
]


class KeyPress:
    """
    Button press for a controller.

    (For most operations you should use the aliases from basics.py)

    Example usage:
        >>> sprint_10_frames = KeyPress(frames=10, l_thumb_y=32767, b=1)
        >>> sprint_10_frames.execute()

    Results of operators:
        KeyPress1 + KeyPress2 = KeySequence([KeyPress1, KeyPress2])
        KeyPress(frames=x, ...) * n = KeyPress(frames=n*x, ...)
        KeyPress1 & KeyPress2 = KeyPress1 and KeyPress2 simultaneously for the longest number of frames

    :param frames: Number of frames to hold the keypress
    :param dpad_up:
    :param dpad_down:
    :param dpad_left:
    :param dpad_right:
    :param start:
    :param back:
    :param l_thumb:
    :param r_thumb:
    :param l1:
    :param r1:
    :param a:
    :param b:
    :param x:
    :param y:
    :param l2:
    :param r2:
    :param l_thumb_x:
    :param l_thumb_y:
    :param r_thumb_x:
    :param r_thumb_y:
    """
    def __init__(
        self,
        frames=1,
        *,
        dpad_up=0,
        dpad_down=0,
        dpad_left=0,
        dpad_right=0,
        start=0,
        back=0,
        l_thumb=0,
        r_thumb=0,
        l1=0,
        r1=0,
        a=0,
        b=0,
        x=0,
        y=0,
        l2=0,
        r2=0,
        l_thumb_x=0,
        l_thumb_y=0,
        r_thumb_x=0,
        r_thumb_y=0
    ):
        self.frames = frames
        self.dpad_up = dpad_up
        self.dpad_down = dpad_down
        self.dpad_left = dpad_left
        self.dpad_right = dpad_right
        self.start = start
        self.back = back
        self.l_thumb = l_thumb
        self.r_thumb = r_thumb
        self.l1 = l1
        self.r1 = r1
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        self.l2 = l2
        self.r2 = r2
        self.l_thumb_x = l_thumb_x
        self.l_thumb_y = l_thumb_y
        self.r_thumb_x = r_thumb_x
        self.r_thumb_y = r_thumb_y

    def __repr__(self):
        repr_mid = ', '.join(
            f'{key}={getattr(self, key)}'
            for key in controller_keys
            if getattr(self, key) != 0
        )
        if repr_mid:
            repr_mid = f', {repr_mid}'

        return f'KeyPress(frames={self.frames}{repr_mid})'

    def __add__(self, other):
        if isinstance(other, KeyPress):
            return KeySequence([self, other])
        elif isinstance(other, KeySequence):
            return KeySequence([self, *other._sequence])

    def __mul__(self, other):
        if isinstance(other, int):
            newframes = self.frames * other
            newpress = copy(self)
            newpress.frames = newframes
            return newpress
        else:
            raise TypeError('Can only multiply keypresses by integers')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __and__(self, other):
        """
        Combine KeyPresses

        This makes sense as an 'and' command but it's logically
        more connected to 'or'.

        For every button press take the 'largest' value
        This means for values that can be negative it will take the 'bigger' number.

        :param other: KeyPress instance to combine
        :type other: KeyPress
        :return: New Combined KeyPress
        """
        return KeyPress(
            frames=max(self.frames, other.frames),
            dpad_up=max(self.dpad_up, other.dpad_up),
            dpad_down=max(self.dpad_down, other.dpad_down),
            dpad_left=max(self.dpad_left, other.dpad_left),
            dpad_right=max(self.dpad_right, other.dpad_right),
            start=max(self.start, other.start),
            back=max(self.back, other.back),
            l_thumb=max(self.l_thumb, other.l_thumb),
            r_thumb=max(self.r_thumb, other.r_thumb),
            l1=max(self.l1, other.l1),
            r1=max(self.r1, other.r1),
            a=max(self.a, other.a),
            b=max(self.b, other.b),
            x=max(self.x, other.x),
            y=max(self.y, other.y),
            l2=max(self.l2, other.l2),
            r2=max(self.r2, other.r2),
            l_thumb_x=max(self.l_thumb_x, other.l_thumb_x, key=abs),
            l_thumb_y=max(self.l_thumb_y, other.l_thumb_y, key=abs),
            r_thumb_x=max(self.r_thumb_x, other.r_thumb_x, key=abs),
            r_thumb_y=max(self.r_thumb_y, other.r_thumb_y, key=abs),
        )

    def __len__(self):
        """
        len on a KeyPress returns the number of frames it will be held for.

        :return: frame count
        """
        return self.frames

    def __eq__(self, other):
        if isinstance(other, KeyPress):
            return self.keylist == other.keylist
        else:
            return False

    @classmethod
    def from_list(cls, state):
        key_values = dict(zip(controller_keys, state))
        return cls(
            frames=1,
            **key_values
        )

    @property
    def keylist(self):
        return [
            [
                self.dpad_up,
                self.dpad_down,
                self.dpad_left,
                self.dpad_right,
                self.start,
                self.back,
                self.l_thumb,
                self.r_thumb,
                self.l1,
                self.r1,
                self.a,
                self.b,
                self.x,
                self.y,
                self.l2,
                self.r2,
                self.l_thumb_x,
                self.l_thumb_y,
                self.r_thumb_x,
                self.r_thumb_y,
            ]
            for _ in range(self.frames)
        ]

    @property
    def button_pressed(self):
        """
        Return if an on/off button is pressed (does not include triggers)

        :return: True/False
        """
        return bool(sum([
            self.start,
            self.back,
            self.l_thumb,
            self.r_thumb,
            self.l1,
            self.r1,
            self.a,
            self.b,
            self.x,
            self.y
        ]))


class KeySequence:
    """
    A sequence or chain of keypresses to be executed by the TAS.

    Includes methods for addition and multiplication.

    Use the .execute() method to perform the sequence in game.

    :param sequence: list of KeyPress or KeySequence objects
    """
    def __init__(self, sequence=None):
        sequence = sequence if sequence else []
        seq = []
        for item in sequence:
            if isinstance(item, KeyPress):
                seq.append(copy(item))
            elif isinstance(item, KeySequence):
                seq.extend(item._sequence)
            else:
                raise TypeError(
                    f'Expected KeyPress or KeySequence, found {type(item)}'
                )
        self._sequence = seq
        self.condense()

    def __repr__(self):
        seq = ', '.join(repr(item) for item in self._sequence)
        return f'KeySequence([{seq}])'

    def __radd__(self, other):
        if isinstance(other, KeySequence):
            return KeySequence([*other._sequence, *self._sequence])
        elif isinstance(other, KeyPress):
            return KeySequence([KeyPress,  *self._sequence])
        else:
            return NotImplemented

    def __add__(self, other):
        if isinstance(other, KeySequence):
            return KeySequence([*self._sequence, *other._sequence])
        elif isinstance(other, KeyPress):
            return KeySequence([*self._sequence, other])
        else:
            return NotImplemented

    def __len__(self):
        """
        Return the number of steps in the keyseq

        :return: Number of steps in the keysequence
        """
        return len(self._sequence)

    def __mul__(self, other):
        """
        Integer Multiplication of a sequence should repeat the sequence

        :param other: Number of times to perform sequence
        :return: new sequence.
        """
        if isinstance(other, int):
            return KeySequence(self._sequence * other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __getitem__(self, item):
        value = self._sequence[item]
        if isinstance(value, list):
            return KeySequence(value)
        else:
            return value

    def __setitem__(self, key, value):
        self._sequence[key] = value

    @property
    def framecount(self):
        return sum(press.frames for press in self._sequence)

    @property
    def keylist(self):
        return list(chain.from_iterable(item.keylist for item in self._sequence))

    def append(self, keypress):
        self._sequence.append(keypress)

    def extend(self, keypresses):
        self._sequence.extend(keypresses)

    def condense(self):
        """
        Reduce the keysequence to the minimum number of KeyPress instances by
        combining identical button presses into single instances with multiple
        frames.

        Do nothing if the sequence is shorter than 2 KeyPresses.
        """
        if len(self._sequence) > 1:
            newseq = []
            current_press = copy(self._sequence[0])
            for press in self._sequence[1:]:
                if not press.keylist:
                    # Skip empty presses
                    continue
                elif not current_press.keylist:
                    # If the original press is empty
                    # load the next press
                    current_press = copy(press)
                    continue
                elif press.keylist[0] == current_press.keylist[0]:
                    # Only care if the keypress uses the same keys
                    current_press.frames += press.frames
                else:
                    # If the presses are different append to our new
                    # sequence and update the current press
                    newseq.append(current_press)
                    current_press = copy(press)
            newseq.append(copy(current_press))
            self._sequence = newseq

    def to_string(self):
        """
        Dump list data to string

        :return: list of keypress commands as a string
        """
        return json.dumps(self.keylist)

    def to_file(self, keylist_file):
        with open(keylist_file, 'w') as outdata:
            outdata.write(self.to_string())

    @classmethod
    def from_string(cls, keylist_string):
        return cls.from_list(json.loads(keylist_string))

    @classmethod
    def from_file(cls, keylist_file):
        with open(keylist_file) as indata:
            result = cls.from_list(json.load(indata))
        return result

    @classmethod
    def from_list(cls, states):
        """
        Return the keypresses from a list of lists of press values
        :param states:
        :return:
        """
        instance = cls([KeyPress.from_list(state) for state in states])
        return instance


def print_press(keylist, print_wait=False):
    """
    Method to print keypresses as KeyPress given individual list inputs.

    :param keylist: List of key values
    :param print_wait: Print 'wait' values
    """
    wait = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if print_wait or keylist != wait:
        print(KeyPress.from_list(keylist))
