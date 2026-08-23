#!/usr/bin/python3
import pygame
import sys
import math
import random
import datetime as _datetime

pygame.init()

WIDTH, HEIGHT = 900, 550
GROUND_Y = 430
FPS = 60

# Dev mode ("cicada77" on the home screen): lets the offset below be
# nudged from a UI panel so date-gated content (seasonal events,
# eclipses, daily streaks, etc.) can be tested without waiting for the
# real calendar date. 0 offset == real time.
DEV_TIME_OFFSET = _datetime.timedelta(0)


def dev_now():
    return _datetime.datetime.now() + DEV_TIME_OFFSET


def dev_today():
    return dev_now().date()

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (220,  40,  40)
BLUE   = (40,  100, 220)
GREEN  = (40,  180,  60)
YELLOW = (255, 220,   0)
GRAY   = (120, 120, 120)
DARK   = (30,   30,  30)
ORANGE = (255, 140,   0)
PURPLE = (160,  40, 200)
CYAN   = (0,   200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Fighter")
clock = pygame.time.Clock()

font_large  = pygame.font.SysFont("Arial", 52, bold=True)
font_medium = pygame.font.SysFont("Arial", 26, bold=True)
font_small  = pygame.font.SysFont("Arial", 18)
font_tiny   = pygame.font.SysFont("Arial", 11)

GRAVITY = 0.55
STAGE_VOID    = False   # when True the ground floor is removed; falling off = instant death
STAGE_CEILING = False   # when True the ceiling is lethal; jumping into the top kills you
STAGE_WATER   = False   # when True the arena is flooded up to WATER_LINE_Y (Underwater stage)
WATER_LINE_Y  = HEIGHT * 0.35   # raised from the old HEIGHT/2 — water covers more of the arena


HEAD_R   = 18
BODY_LEN = 50
ARM_LEN  = 38
LEG_LEN  = 45
NECK_LEN = 5

