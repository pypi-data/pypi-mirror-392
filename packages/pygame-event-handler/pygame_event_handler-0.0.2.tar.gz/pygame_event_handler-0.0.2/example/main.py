import pygame as pg
from pygame import RESIZABLE
from pygame_event_handler.event_handler import EventHandler

import pygame


def get_text(text):
    surface = font.render(text, True, "black")
    return surface



pg.init()
screen = pg.display.set_mode([800,600],RESIZABLE)
font = pygame.font.Font(None, 80)

event_handler = EventHandler()

while not event_handler.should_quit:

    screen.fill("white")
    event_handler.get_events()
    screen.blit(get_text("FPS: "+str(event_handler.final_fps)),[0,0])
    screen.blit(get_text("Window focus: "+str(event_handler.window_focus)),[0,80])
    screen.blit(get_text("Mouse Focus: "+str(event_handler.mouse_focus)),[0,160])
    screen.blit(get_text("Held Keys "+str(event_handler.held_keys)),[0,240])
    screen.blit(get_text("Mouse held buttons "+str(event_handler.mouse_held_keys)),[0,320])
    pg.display.update()