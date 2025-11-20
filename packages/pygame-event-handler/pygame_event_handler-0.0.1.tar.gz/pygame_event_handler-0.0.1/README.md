## Pygame Event Handler

A simple python package that helps with handling events in pygame-ce.

### Features
 - Provides easy-to-use interface for checking if a key is pressed,held, or released (keyboard and mouse buttons)
 - Provides easy-to-use interface to find the location of the mouse cursor
 - Calculates delta time and real time FPS
 - Checks window focus

### Example
```python
import pygame_ce
from pygame_event_handler.event_handler import EventHandler

pg.init()
screen = pg.display.set_mode([800,600])

event_handler = EventHandler()

while not event_handler.should_quit:
    event_handler.get_events()
```