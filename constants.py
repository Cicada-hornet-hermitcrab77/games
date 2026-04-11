#!/usr/bin/python3
import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 900, 550
GROUND_Y = 430
FPS = 60

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

font_large  = pygame.font.SysFont("Arial", 72, bold=True)
font_medium = pygame.font.SysFont("Arial", 36, bold=True)
font_small  = pygame.font.SysFont("Arial", 24)
font_tiny   = pygame.font.SysFont("Arial", 13)

GRAVITY = 0.55
STAGE_VOID    = False   # when True the ground floor is removed; falling off = instant death
STAGE_CEILING = False   # when True the ceiling is lethal; jumping into the top kills you


HEAD_R   = 18
BODY_LEN = 50
ARM_LEN  = 38
LEG_LEN  = 45
NECK_LEN = 5

