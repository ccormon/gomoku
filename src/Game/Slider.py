import pygame as pg
from pygame.locals import *


class Slider:
    TRACK_COLOR       = (80,  80,  80)
    FILL_COLOR        = (200, 200, 200)
    KNOB_COLOR        = (255, 255, 255)
    KNOB_BORDER_COLOR = (150, 150, 150)
    KNOB_SHADOW_COLOR = (50,  50,  50)
    TRACK_HEIGHT      = 8
    KNOB_RADIUS       = 12

    # center_pct:     (x%, y%) centre of the slider track in window-percentage coordinates
    # width_pct:      width of the track as a percentage of the window width
    # initial_value:  starting value in [0.0, 1.0]
    # callback:       called with the new float value whenever the knob moves
    def __init__(self, window, center_pct: tuple, width_pct: float,
                 initial_value: float = 1.0, callback: callable = None):

        self.cx = int(center_pct[0] * window.size[0] / 100)
        self.cy = int(center_pct[1] * window.size[1] / 100)
        self.width = int(width_pct * window.size[0] / 100)
        self.value = max(0.0, min(1.0, initial_value))
        self.callback = callback
        self.dragging = False

        self.track_rect = pg.Rect(
            self.cx - self.width // 2,
            self.cy - self.TRACK_HEIGHT // 2,
            self.width,
            self.TRACK_HEIGHT,
        )
        self._update_knob()


    def _update_knob(self):
        self.knob_x = int(self.cx - self.width // 2 + self.value * self.width)
        self.knob_y = self.cy


    def _set_value_from_x(self, x: int):
        track_left = self.cx - self.width // 2
        self.value = max(0.0, min(1.0, (x - track_left) / self.width))
        self._update_knob()
        if self.callback:
            self.callback(self.value)


    def draw(self, surface: pg.Surface):
        # Background track
        pg.draw.rect(surface, self.TRACK_COLOR, self.track_rect,
                     border_radius=self.TRACK_HEIGHT // 2)
        # Filled portion
        filled_w = max(0, int(self.value * self.width))
        if filled_w > 0:
            filled_rect = pg.Rect(self.track_rect.x, self.track_rect.y,
                                  filled_w, self.TRACK_HEIGHT)
            pg.draw.rect(surface, self.FILL_COLOR, filled_rect,
                         border_radius=self.TRACK_HEIGHT // 2)
        # Knob shadow
        pg.draw.circle(surface, self.KNOB_SHADOW_COLOR,
                       (self.knob_x + 2, self.knob_y + 2), self.KNOB_RADIUS)
        # Knob
        pg.draw.circle(surface, self.KNOB_COLOR,
                       (self.knob_x, self.knob_y), self.KNOB_RADIUS)
        pg.draw.circle(surface, self.KNOB_BORDER_COLOR,
                       (self.knob_x, self.knob_y), self.KNOB_RADIUS, 2)


    def update(self, event: pg.event.Event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            dx, dy = mx - self.knob_x, my - self.knob_y
            if dx * dx + dy * dy <= (self.KNOB_RADIUS + 6) ** 2:
                self.dragging = True
            elif self.track_rect.inflate(0, 20).collidepoint(event.pos):
                self.dragging = True
                self._set_value_from_x(mx)
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION:
            if self.dragging:
                self._set_value_from_x(event.pos[0])