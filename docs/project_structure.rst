=================
Project Structure
=================

* darksoulstas.py is the main application
* build_tas.py is a script to build the wheel and exe
* darksoulstas.spec contains the build settings for the application exe

* controller.py defines classes for a single key press or a sequence of presses
* basics.py provides short aliases to useful keypresses
* exceptions.py defines the python exceptions that are called from ds_tas

* engine/hooks.py contains the code that deals with hooking into game memory
* engine/tas_engine.py deals with giving the hooks commands from the controller

* the scripts/ folder contains glitches and useful command combinations
* the demos/ folder contains some pre-recorded or programmed demos
