import pygame as pg
from pygame.locals import *

from Position import Position


def createHoverImage(image: pg.Surface, factor: float):
    imageHoverSize = (int(image.get_width() * factor), int(image.get_height() * factor))
    imageHover = pg.transform.smoothscale(image, imageHoverSize)
    return imageHover


class Button:
    def __init__(self, image_path: str, position: Position, callBack: callable, unloadOnClick: bool=True):
        self.image = pg.image.load(image_path).convert_alpha()
        self.size = self.image.get_size()
        self.position = position
        pos = position.get(self.size)
        self.rect = pg.Rect(pos[0], pos[1], self.size[0], self.size[1])
        self.callback = callBack
        self.onHover = False
        self.unloadOnClick = unloadOnClick
        self.imageHover = createHoverImage(self.image, 1.1)


    def draw(self, surface: pg.Surface):
        if self.onHover:
            surface.blit(self.imageHover, self.position.get(self.imageHover.get_size()))
        else:
            surface.blit(self.image, self.position.get(self.image.get_size()))


    def onButton(self, pos: tuple):
        return self.rect.collidepoint(pos)


    def onClickDown(self):
        pass


    def onClickRelease(self):
        if self.callback:
            self.callback(self)
        if self.unloadOnClick:
            self.onHover = False


    def update(self, event: pg.event.Event):
        if event.type == MOUSEBUTTONDOWN:
            if self.onButton(event.pos):
                self.onClickDown()

        elif event.type == MOUSEBUTTONUP:
            if self.onButton(event.pos):
                self.onClickRelease()

        elif event.type == MOUSEMOTION:
            if self.onButton(event.pos):
                self.onHover = True
            else:
                self.onHover = False


class ToggleButton(Button):
    def __init__(self, imageOnPath: str, imageOffPath: str, position: Position, initialState: bool=True, callBack: callable=None):
        super().__init__(imageOnPath, position, callBack)
        self.imageOn = self.image
        self.imageOnHover = self.imageHover
        self.imageOff = pg.image.load(imageOffPath).convert_alpha()
        self.imageOffHover = createHoverImage(self.imageOff, 1.1)
        self.active = initialState


    def onClickRelease(self):
        self.toggle()
        if self.callback:
            self.callback(self)


    def toggle(self):
        self.active = not self.active
        self.image, self.imageHover = (self.imageOn, self.imageOnHover) if self.active else (self.imageOff, self.imageOffHover)