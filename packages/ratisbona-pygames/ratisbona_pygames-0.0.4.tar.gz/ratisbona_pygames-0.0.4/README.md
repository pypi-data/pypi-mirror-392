# Ratisbona Pygames

This project comprises a set of small games and demos written in python using the pygame library.

fire_demo:   
  Demo that shows a famous fire effect using Pygame.

etchasketch:   
  A small etch-a-sketch like drawing program.

fanedit:
  Utility to create a cirular image for a usb-powered persistence-of-vision led-display fan.

death_by_powerpoint:   
  A little psycho-game that lets you experience, that your brain just has around 7 fast registers for objects.
  Guessing the number of larger sets of objects is slower, causes more strain and is more error-prone as for 7 objects.
  
palette_demo:   
  Demos different palettes that are available in the ratisbona_utils.simplecolors module.

## Project-structure, Installing Dependencies and PYTHONPATH configuration.

This Project houses it's sources below the `src/{projectname}` directory. You have
to have this directory in your module-searchpath to execute the project. It should also
be present in the module-searchpath of your IDE.

If using pycharm or any other Jetbrains-based IDE, use 
`Settings->Project->Project Structure`
to `mark as sourcefolder` the `src`-folder of this.

The Project requirements, as well as the dev-requirements are intended to be listed in the 
`pyproject.toml`-file (see there)

By issuing:

```shell
pip install -e .
```

you add all the project dependencies as well as the projects sourcefolder to your 
[hopefully virtual!] environment, relieving you of the burden of having to manually 
installing anything or having to configure your python path by other means.

Likewise you can install all the dev-dependencies by:

```shell
pip install -e .'[dev]'
```

