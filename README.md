# Dark Souls TAS tools #
 
 Instructions:

- Go offline in Steam (if you are not already)
- Launch Dark Souls
- Launch darksoulstas.exe

The tools should be compatible with both the latest steam release of
Dark Souls and the debug version.

Note that this is designed for use in offline play for testing
(and maze games). RNG currently makes it impractical to do a consistent
TAS run at the moment.

**Note: You must have an XInput controller connected**

## Quick Preset Examples ##

```python
TAS>>> wave = select + right + a
TAS>>> tas.run(wave)
TAS>>>
TAS>>> tas.run(glitches.roll_moveswap())
TAS>>>
TAS>>> tas.run(menus.quitout)
```

## Basic Movement Keypresses ##

The basic movements can be found in the `ds_tas.basics` module.
These are pre-defined inputs designed to make working with the
tools easier.

The following keypresses are predefined in the basics module.

Do Nothing:
```python
wait
```

Buttons and triggers:
```python
a, b, x, y, start, select, l1, l2, l3, r1, r2, r3
```

DPad:
```python
up, down, left, right
```

Joysticks:
```python
run, run_back, run_left, run_right
walk, walk_back, walk_left, walk_right
aim_up, aim_down, aim_left, aim_right
s_aim_up, s_aim_down, s_aim_left, s_aim_right
```
(`s_` stands for slow)

`sprint` is also defined, but if done for a small number of frames will
instead perform a roll.

To execute any of these keypresses you can simply call tas.run on them
`tas.run(name)` into the python window after importing them.

For Example opening the menu and selecting things (while in game):
```python
TAS>>> # Open the menu and move left and right and close it again
TAS>>> tas.run(start)
TAS>>> tas.run(right)
TAS>>> tas.run(left)
TAS>>> tas.run(start)
```

If you simply type one of these without .execute() in you will see
that they appear as `KeyPress(frames=x, ...)` in the terminal. This
is the object being used internally and is a useful representation
of what's going on.

## Combining KeyPresses and building sequences ##

The previous example showed doing one keypress at a time, which
isn't really what we want to be able to do. Ideally you would want
to set up a sequence of keypresses and then execute that sequence.

To combine keypresses you can use the +, * and & operators.

On a `KeyPress` object:

The + operator chains commands, so `select + right` will press the
select key, then the right key a frame later.

The * operator allows you to hold a keypress for multiple frames,
so `run * 20` will run for 20 frames.

The & operator allows you to perform button presses at the same time,
so `run & b` will run and press b on the same frame, usually
resulting in a roll.

When you use these combinations you will see the resulting `KeyPress`
and `KeySequence` objects returned.

On a `KeySequence` object:

The * operator will repeat the set of commands, the + operator will
chain the sequences, and the & operator does not work.

### Example: Changing Weapon ###

(Return values have been formatted for readability in this example.)
Wait times are used where otherwise inputs would be too quick to
register.

```python
TAS>>> # Start menu with delay
TAS>>> start_menu = start + (wait * 5)
TAS>>> start_menu
KeySequence([KeyPress(frames=1, start=1), KeyPress(frames=5)])
TAS>>>
TAS>>> inventory_menu = start_menu + right + a
TAS>>> inventory_menu
KeySequence([
    KeyPress(frames=1, start=1),
    KeyPress(frames=5),
    KeyPress(frames=1, dpad_right=1),
    KeyPress(frames=1, a=1)
])
TAS>>> swap_lh_weapon = inventory_menu + wait + down + a + (wait * 2) + up + a
TAS>>> tas.run(swap_lh_weapon)  # Actually swap weapons
```

These commands can also be combined by creating a list and passing
that list into the KeySequence class. For example creating the same
weapon swap would be the following list

```python
TAS>>> swap_lh_weapon = KeySequence([
    start,
    wait * 5,
    right,
    a,
    wait,
    down,
    a,
    wait * 2,
    up,
    a
])
```

Commands built like this can bs seen in `demos/bonfire_run.py` and
the `glitches.py` and `menus.py` in the scripts folder.

## Recording inputs and playback ##

Record on first button press (wait for the counter then load a save):
```python
TAS>>> record()
```
This will record inputs until you press start and select at the same time.

Reload the savefile and highlight the save then execute the commands:
```python
TAS>>> playback()
```

Save the recording:
```python
TAS>>> save('tas_demo.txt')
```

Reload the recording:
```python
TAS>>> load('tas_demo.txt')
```


## Example Demo ##

To try to playback the asylum run. The most likely outcome is dying to asylum demon. You might get lucky though!

Make a new game as male thief with firebombs.

Quitout without touching anything.

Execute the commands and then make sure dark souls is active before the countdown finishes.

Setting igt_wait to False makes the playback execute the first command before waiting for IGT to change.

```python
TAS>>> load('demos/asylum_run.txt')
TAS>>> playback(start_delay=10, igt_wait=False)
```

If you're really lucky it looks like this: https://youtu.be/gf_ApkcKt6I


## Jupyter Notebook Demo ##

There is also a Jupyter notebook demo if you have the source instead.

If you want to try the example notebook you will need to install Jupyter.
From a command terminal (where `python` will launch python 3.6)
```
> python -m pip install jupyter
> jupyter notebook
```

Then open the DS_TAS Demo notebook (found in the notebooks folder).

(If you haven't used a Jupyter notebook before you can step through the
cells by pressing shift+enter)
