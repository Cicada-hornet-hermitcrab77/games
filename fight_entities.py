"""
fight_entities — re-export hub.

All classes have been split into focused modules:
  fight_projectiles.py  — projectile / hazard objects
  fight_stage.py        — stage elements (platforms, NPCs, pickups)
  fight_fighter.py      — Fighter and AIFighter
"""
from fight_projectiles import *
from fight_stage import *
from fight_fighter import *
